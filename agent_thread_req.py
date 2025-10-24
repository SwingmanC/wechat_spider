import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import requests
import json
from datetime import datetime
import random
import os

def generate_request_id():
    # 1. 生成17位时间戳（yyyyMMddHHmmssSSS）
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S%f")[:17]  # 取前17位（%f是微秒，只取前3位作为毫秒）

    # 2. 生成6位随机数（补零到6位）
    random_num = f"{random.randint(0, 999999):06d}"

    # 3. 拼接时间戳和随机数
    request_id = f"{timestamp}{random_num}"
    return request_id

def process_chunk(chunk, chunk_index):
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
                        data = {}
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
                    output.append(
                        [account_name, item['日期'], title, d['区县'], d['单位名称'], d['商机类型'], d['涉及金额'],
                         d['概述'], item['链接']])
            else:
                output.append([account_name, item['日期'], title, '', '', '', '', '', item['链接']])
        except:
            output.append([account_name, item['日期'], title, '', '', '', '', '', item['链接']])

    output_df = pd.DataFrame(output,
                             columns=['公众号', '发布日期', '文章标题', '区县', '单位名称', '商机类型', '涉及金额',
                                      '概述', '链接'])

    # 示例处理：添加一列显示这是哪个块处理的
    output_df['处理线程'] = f"线程-{chunk_index + 1}"
    return output_df


def split_and_process(input_file, output_file, num_chunks=10):
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
            futures.append(executor.submit(process_chunk, chunk, i))

        # 等待所有任务完成并收集结果
        for future in futures:
            processed_chunks.append(future.result())

    # 4. 合并处理后的数据块
    merged_df = pd.concat(processed_chunks, ignore_index=True)

    # 5. 保存到新的Excel文件
    merged_df.to_excel(output_file, index=False)
    print(f"处理完成，结果已保存到: {output_file}")


# 使用示例
if __name__ == "__main__":
    root = 'D:/ipa/商机挖掘/公众号爬虫/'
    input_excel = "20251023.xlsx"  # 输入文件
    output_excel = "processed_result_20251023_1.xlsx"  # 输出文件

    # 确保输入文件存在
    if not os.path.exists(root + input_excel):
        print(f"错误: 输入文件 {input_excel} 不存在")
    else:
        split_and_process(root + input_excel, root + output_excel, num_chunks=10)
