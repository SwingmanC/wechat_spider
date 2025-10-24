import requests
import json
from datetime import datetime
import random
import pandas as pd

def generate_request_id():
    # 1. 生成17位时间戳（yyyyMMddHHmmssSSS）
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S%f")[:17]  # 取前17位（%f是微秒，只取前3位作为毫秒）

    # 2. 生成6位随机数（补零到6位）
    random_num = f"{random.randint(0, 999999):06d}"

    # 3. 拼接时间戳和随机数
    request_id = f"{timestamp}{random_num}"
    return request_id

def busi_identify():
    root = 'D:/ipa/商机挖掘/公众号爬虫/'
    file_name = datetime.now().strftime("%Y%m%d")

    # 定义URL
    url = 'http://10.32.41.228:44501/scene_gateway/agent/open/dcf391bfc1634339b15b8a3a3d5982c3'

    # 定义请求头
    headers = {
        'Content-Type': 'application/json',  # 假设API需要JSON格式的数据
        'AuthToken': '00a837714b064105a0dbc3e99b8654c2'
    }

    # df = pd.read_excel(root + file_name + '.xlsx', sheet_name=0)
    df = pd.read_excel(root + 'test.xlsx', sheet_name=0)
    output = []
    for index, item in df.iterrows():
        account_name = item['公众号']
        title = item['文章标题']
        print('正在分析：' + account_name + ',' + title)
        txt_path = root + account_name + '/' + title + '.txt'

        # 读取整个文件内容
        with open(txt_path, 'r', encoding='utf-8') as file:
            content = file.read()

        try:
            # 定义要发送的数据
            request_id = generate_request_id()
            data = {
                "keyword": content,
                "requestId": request_id,
                "dialogId": request_id,
                "agentState": 'release'
            }

            # 发起POST请求，并传入headers参数
            response = requests.post(url, json=data, headers=headers)

            # 手动解析 SSE 事件
            buffer = ''
            resp = ''
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    try:
                        # 确保以 UTF-8 解码
                        buffer += chunk.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        # 如果UTF-8解码失败，尝试GBK
                        try:
                            buffer += chunk.decode('gbk', errors='ignore')
                        except:
                            # 最后尝试latin-1，它不会解码失败
                            buffer += chunk.decode('latin-1', errors='ignore')

                    # 分割事件（事件由两个换行符分隔）
                    while '\n\n' in buffer:
                        event, buffer = buffer.split('\n\n', 1)
                        for line in event.split('\n'):
                            data_str = line
                            if data_str.startswith('data:'):
                                data_str = data_str.replace('data: ', '')
                            try:
                                data = json.loads(data_str)
                                content_value = data["choices"][0]["delta"].get('content')
                                if content_value is not None and content_value != 'end##end':
                                    if content_value == '<think>':
                                        content_value = '【思考过程】'
                                    elif content_value == '</think>':
                                        content_value = '【思考过程】'
                                    elif content_value == '<br />':
                                        content_value = '\n'
                                    resp += content_value
                            except (json.JSONDecodeError, KeyError) as e:
                                continue  # 跳过解析错误的行
            response.close()
            # 更安全地提取JSON部分
            try:
                start_idx = resp.find('```json') + 7
                end_idx = resp.rfind('```')
                if start_idx >= 7 and end_idx > start_idx:
                    json_str = resp[start_idx:end_idx].replace('<br />', '')
                    data = json.loads(json_str)
                else:
                    # 如果没有找到代码块标记，尝试直接解析整个响应
                    data = json.loads(resp)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print(f"原始响应: {resp}")
                # 处理解析失败的情况
                data = []
            if len(data) != 0:
                for d in data:
                    output.append([account_name,item['日期'],title,d['区县'],d['单位名称'],d['商机类型'],d['涉及金额'],d['概述'],item['链接']])
            else:
                output.append([account_name, item['日期'], title, '', '', '', '', '', item['链接']])
        except:
            output.append([account_name, item['日期'], title, '', '', '', '', '', item['链接']])

    output_df = pd.DataFrame(output, columns=['公众号', '发布日期', '文章标题', '区县', '单位名称', '商机类型', '涉及金额', '概述', '链接'])
    output_df.to_excel(root + file_name + '_output.xlsx', index=False)


if __name__ == "__main__":
    busi_identify()