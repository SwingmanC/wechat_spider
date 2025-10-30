import requests
from datetime import datetime
import random
import json

def generate_request_id():
    # 1. 生成17位时间戳（yyyyMMddHHmmssSSS）
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S%f")[:17]  # 取前17位（%f是微秒，只取前3位作为毫秒）

    # 2. 生成6位随机数（补零到6位）
    random_num = f"{random.randint(0, 999999):06d}"

    # 3. 拼接时间戳和随机数
    request_id = f"{timestamp}{random_num}"
    return request_id

# 定义要发送的数据
url = 'http://10.32.41.228:44501/scene_gateway/agent/open/dcf391bfc1634339b15b8a3a3d5982c3'
headers = {
    'Content-Type': 'application/json',  # 假设API需要JSON格式的数据
    'AuthToken': '00a837714b064105a0dbc3e99b8654c2'
}

content = '区领导调研重点项目建设工作吴中发改10月14日，区委书记丁立新调研重点项目建设工作。他强调，要坚定不移实施“产业强区、创新引领”发展战略，坚持大抓项目、抓大项目、抓高质量项目，全力保障重点项目建设提速提质提效，为吴中经济高质量发展提供坚实支撑。丁立新先后来到绿的谐波（胥江湾）具身智能机器人（硬核）产业园项目、苏州凯尔博科技股份有限公司全球总部项目、江苏迈信林航空科技股份有限公司航空航天产业零部件研发生产总部项目、恒而思达高端医疗影像设备与智能康养产业总部项目建设现场，实地查看建设推进情况，询问了解企业未来发展规划，现场协调解决建设中面临的问题困难。他叮嘱各相关负责人务必坚守安全生产底线，科学统筹施工计划，全力加快建设进度，确保项目如期保质保量完成、早日投产达效。丁立新强调，重点项目是经济发展的“压舱石”，更是未来发展的“增长极”。要整合各方资源、强化高效服务，聚焦项目建设关键节点和难点堵点，以全天候的响应服务、全要素的精准支撑，助推重点项目加快建设进度、尽早实现投产运营。要完善基础配套、优化产业生态，以重点项目建设为契机，合理布局工业集聚区人才公寓、生活服务综合体、道路交通等，充分发挥龙头企业虹吸效应，吸引高端人才落户入驻，为产业集群建设增势赋能。要坚持项目为王、加强项目储备，结合“十五五”规划编制，围绕“3+2+N”重点产业集群科学谋划，形成“投产一批、建设一批、储备一批”的良性循环，为持续壮大产业规模、增强发展后劲注入源源不断动力。区委常委、常务副区长周学斌，区相关部门、板块负责人参加调研。来源：吴中发布预览时标签不可点微信扫一扫关注该公众号继续滑动看下一个轻触阅读原文吴中发改向上滑动看下一个知道了微信扫一扫使用小程序取消允许取消允许取消允许×分析微信扫一扫可打开此内容，使用完整服务：，，，，，，，，，，，，。 视频小程序赞，轻点两下取消赞在看，轻点两下取消在看分享留言收藏听过'

for i in range(0, 5):
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
                # 统一使用UTF-8解码，忽略错误字符
                buffer += chunk.decode('utf-8', errors='ignore')
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

    print(resp)
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

        # print(data)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应: {resp}")
        # 处理解析失败的情况
        data = {}