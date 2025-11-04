import time
import requests
import warnings
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from excel2database import upload
import random
import os

import setting
from setting import proxies
from setting import page_num

warnings.filterwarnings("ignore")

# 一个处理返回结果的函数
def dealspring(prostring):
    return json.loads(prostring["publish_page"])['publish_list']

# 获取公众号文章链接
def geturl(file_path,root,output_file_name):

    txt_dir_path = root + '公众号爬虫/'
    df = pd.read_excel(file_path, sheet_name=0)

    limit = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    wechat_accounts_fakeid = {}
    for index, item in df.iterrows():
        params1 = {
            'action': 'search_biz',
            'begin': '0',
            'count': '1',
            'query': item['公众号名称'],
            'token': setting.wx_token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
        }
        try:
            response = requests.get('https://mp.weixin.qq.com/cgi-bin/searchbiz',verify=False,
                                        params=params1, cookies=setting.wxgeturl_cookies, headers=setting.headers, proxies=proxies)
            if json.loads(response.text)['base_resp']['ret'] == 200040:
                print('微信公众号token过期')
                return 0
            fakeid = json.loads(response.text)['list'][0]['fakeid']
            wechat_accounts_fakeid[item['公众号名称']] = fakeid
        except requests.exceptions.ConnectionError as e:
            # 处理连接错误的异常逻辑
            print("请求断了,10秒后重试，", e)
            time.sleep(10)
            geturl(file_path)
            return 0
    # print(wechat_accounts_fakeid)
    # 多个公众号的文章获取，每一个fakeid对应一个公众号，要爬取的公众号在setting中配置
    sum_data = []  # 用来存每一个公众号的文章链接
    response = None
    for key in wechat_accounts_fakeid:
        begin_index = 0
        while(True):
            try:
                passages = []
                print("正在轮询 " + key + " 第" + str(begin_index/page_num+1) + "页")
                params2 = {
                    'begin': str(begin_index),
                    'count': page_num,
                    'query': '',
                    'fakeid': wechat_accounts_fakeid[key],
                    'type': '101_1',
                    'free_publish_type': '1',
                    # 'sub_action': 'list_ex',
                    'token': setting.wx_token,  # 需要定时更换token
                    'lang': 'zh_CN',
                    'f': 'json',
                    'ajax': '1',
                }
                try:
                    response = requests.get('https://mp.weixin.qq.com/cgi-bin/appmsgpublish', verify=False,
                                            params=params2, cookies=setting.wxgeturl_cookies, headers=setting.headers, proxies=proxies)
                    # 在这里处理正常响应的逻辑
                    if json.loads(response.text) == {"base_resp": {"ret": 200003, "err_msg": "invalid session"}}:
                        print('微信公众号token过期')
                        return 0
                except requests.exceptions.ConnectionError as e:
                    # 处理连接错误的异常逻辑
                    print("请求断了,10秒后重试，", e)
                    time.sleep(10)
                    geturl(file_path)
                    return 0
                for i in range(page_num):
                    try:
                        msg_list = json.loads(dealspring(json.loads(response.text))[i]['publish_info'])['appmsg_info']
                        sent_dict = json.loads(dealspring(json.loads(response.text))[i]['publish_info'])['sent_info']
                    except Exception as e:
                        print(f"发生异常: {e}")
                        break
                    publish_time = sent_dict['time']
                    # 将时间戳转换为datetime对象
                    dt = datetime.fromtimestamp(publish_time)
                    # 格式化为yyyymmdd字符串
                    date_str = dt.strftime("%Y-%m-%d")

                    for b in msg_list:
                        passage = msg_list[msg_list.index(b)]
                        title = passage['title']
                        chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
                        for c in chars:
                            title = title.replace(c, '-')
                        passages.append([key, title, date_str, passage['content_url']])
                sum_data.extend(passages)
                # 判断是否为10月后的公众号，若不是，则结束轮询爬取公众号标题的循环
                if passages[len(passages)-1][2] < limit:
                    break
                else:
                    begin_index += page_num
                    time.sleep(1)
                # break
            except Exception as e:
                print(f"发生异常: {e}")
                break
        time.sleep(3)

    response.close()

    # 公众号文章爬虫
    for item in sum_data:
        key = item[0]
        print("目前爬取的公众号和文章是：", key + '   ' + item[1])

        if os.path.exists(txt_dir_path + key + '/' + item[1] + '.txt'):
            continue

        if os.path.exists(txt_dir_path + key) is False:
            os.mkdir(txt_dir_path + key)
        try:
            response = requests.get(item[3], headers=setting.headers, proxies=proxies, verify=False)
            # 在这里处理正常响应的逻辑
            soup = BeautifulSoup(response.text, 'lxml')
            html_text = soup.text.replace(" ", "").replace("\n", "")

            with open(txt_dir_path + key + '/' + item[1] + '.txt', 'w', encoding='utf-8') as f:
                f.write(html_text)
        except:
            continue

    result_df = pd.DataFrame(sum_data, columns=['公众号', '文章标题', '日期', '链接'])
    result_df.to_excel(root + 'output/' + output_file_name + '/' + output_file_name + '.xlsx', index=False)

def generate_request_id():
    # 1. 生成17位时间戳（yyyyMMddHHmmssSSS）
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S%f")[:17]  # 取前17位（%f是微秒，只取前3位作为毫秒）

    # 2. 生成6位随机数（补零到6位）
    random_num = f"{random.randint(0, 999999):06d}"

    # 3. 拼接时间戳和随机数
    request_id = f"{timestamp}{random_num}"
    return request_id

def process_chunk(root, chunk, chunk_index):
    """
    处理数据块的函数（这里只是一个示例，你可以替换为自己的处理逻辑）
    参数:
        chunk: 数据块(DataFrame)
        chunk_index: 数据块索引
    返回:
        处理后的数据块(DataFrame)
    """

    # 这里可以添加你的实际处理逻辑
    # 例如: chunk['新列'] = chunk['文章标题'].apply(lambda x: len(x))

    # 定义URL
    url = 'http://10.32.41.228:44501/scene_gateway/agent/open/dcf391bfc1634339b15b8a3a3d5982c3'

    # 定义请求头
    headers = {
        'Content-Type': 'application/json',  # 假设API需要JSON格式的数据
        'AuthToken': '00a837714b064105a0dbc3e99b8654c2'
    }

    output = []
    for index, item in chunk.iterrows():
        account_name = item['公众号']
        title = item['文章标题']
        print('正在分析：' + account_name + ',' + title)
        txt_path = root + account_name + '/' + title + '.txt'

        # 读取整个文件内容
        content = ''
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as file:
                content = file.read()

        if content == '':
            output.append(['', item['日期'], '', '', '', '', account_name, title, item['链接']])
            continue
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
            resp = ''

            resp_str_list = response.text.split('\n\n')
            for resp_str_item in resp_str_list:
                if resp_str_item.startswith('data:'):
                    resp_str_item = resp_str_item.replace('data: ', '')
                try:
                    data = json.loads(resp_str_item)
                    content_value = data["choices"][0]["delta"].get('content')
                    if content_value is not None and content_value != 'end##end':
                        if content_value == '<br />':
                            content_value = '\n'
                        resp += content_value
                except (json.JSONDecodeError, KeyError) as e:
                    continue  # 跳过解析错误的行

            response.close()
            # print(resp)
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
                # print(f"JSON解析错误: {e}")
                print(f"原始响应: {resp}")
                # 处理解析失败的情况
                data = []
            if len(data) != 0:
                print('解析成功：' + title)
                for d in data:
                    output.append(
                        [d['区县'], item['日期'], d['单位名称'], d['商机类型'], d['概述'], d['涉及金额'],
                         account_name, title, item['链接']])
            else:
                output.append(['', item['日期'], '', '', '', '', account_name, title, item['链接']])
        except:
            output.append(['', item['日期'], '', '', '', '', account_name, title, item['链接']])

    output_df = pd.DataFrame(output,
                             columns=['区县', '发布日期', '单位名称', '商机类型', '商机概述', '涉及金额（万元）', '公众号', '文章标题', '链接'])

    # 示例处理：添加一列显示这是哪个块处理的
    # output_df['处理线程'] = f"线程-{chunk_index + 1}"
    return output_df

def split_and_process(root, input_file, output_file, num_chunks=10):
    """
    主函数：读取Excel，分割数据，多线程处理，合并结果
    参数:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径
        num_chunks: 要分割的块数
    """
    # 1. 读取Excel文件
    df = pd.read_excel(input_file)
    total_rows = len(df)
    print(f"总行数: {total_rows}")

    # 2. 将数据分割成num_chunks块
    chunk_indices = np.array_split(range(total_rows), num_chunks)
    chunks = [df.iloc[indices] for indices in chunk_indices]

    # 3. 使用线程池处理各个数据块
    processed_chunks = []
    with ThreadPoolExecutor(max_workers=num_chunks) as executor:
        # 提交所有任务到线程池
        futures = []
        for i, chunk in enumerate(chunks):
            futures.append(executor.submit(process_chunk, root+'公众号爬虫/', chunk, i))

        # 等待所有任务完成并收集结果
        for future in futures:
            processed_chunks.append(future.result())

    # 4. 合并处理后的数据块
    merged_df = pd.concat(processed_chunks, ignore_index=True)

    # 5. 保存到新的Excel文件
    merged_df.to_excel(output_file, index=False)
    print(f"处理完成，结果已保存到: {output_file}")

if __name__ == "__main__":
    root = 'D:/ipa/商机挖掘/'
    file_path = 'D:/ipa/商机挖掘/公众号v1.xlsx'
    output_file_name = datetime.now().strftime("%Y%m%d")

    if os.path.exists(root + 'output/' + output_file_name) is False:
        os.mkdir(root + 'output/' + output_file_name)

    geturl(file_path=file_path, root=root, output_file_name=output_file_name)

    input_excel = root + 'output/' + output_file_name + '/' + output_file_name + '.xlsx'  # 输入文件
    output_excel = root + 'output/' + output_file_name + '/output_' + output_file_name + '.xlsx' # 输出文件

    split_and_process(root, input_excel, output_excel, num_chunks=10)
    upload(file_path=output_excel)