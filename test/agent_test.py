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

content = '明确！江苏扩大社保补贴范围苏州发布今天多云北风5～6级阵风7级、水面阵风8级最低气温：14℃最高气温：19℃早安☀01早报头条近日，江苏省人力资源社会保障厅和省财政厅联合印发《关于加快落实扩大社会保险补贴范围政策有关工作的通知》，明确：江苏扩大社会保险补贴范围政策，支持制造业、生活服务业中小微企业吸纳重点群体就业，对符合条件的个人给予一定金额的社保补贴！申请期限截至2025年底。申领条件制造业、生活服务业的中小微企业与重点群体签订1年以上劳动合同，2025年按规定为其新缴纳或继续缴纳基本养老保险费、基本医疗保险费、失业保险费的。补贴对象重点群体包括：1、2025届高校毕业生、2023届和2024届离校未就业高校毕业生；2、2025年有登记失业记录且连续失业6个月以上的人员；3、防止返贫监测对象。补贴标准按照个人缴费额的25%给予社会保险补贴。补贴由中小微企业申请，申请期限截至2025年底。补贴期限为一年，从中小微企业2025年为重点群体实际缴纳社保的当月开始计算，补贴最晚发放时间不超过2026年底。符合条件的重点群体累计享受补贴期限不得超过12个月。更多详情可点击：江苏扩大社会保险补贴范围02君到苏州降温了，风里终于捎来了真正的秋意，深秋的太湖在正酝酿着一场盛大的浪漫，红嘴鸥即将振翅南飞。不防沿苏州太湖1号公路，与沿途的桂花、银杏、红枫共舞，路边的橘子、柿子、石榴也缀满枝头。来吧，把这整条公路的秋日记忆“打包”回家！（点击下方图片查看详情）更多文旅资讯请点击进入君到苏州文旅总入口03重点关注今天，美国都福集团百士吉旗下CPC中国总部项目正式签约落户太仓。此次百士吉集团在太仓高新区设立的CPC中国总部项目，主要从事具有高附加值的各类高端连接器、高端泵产品和系统的研发与生产，预计达产后年销售额可达4亿元，年纳税额5200万元。（详情）10月21日，海英荷普曼船舶设备（常熟）有限公司开业仪式举行。新工厂的建成让产能得到充分保障，原本老厂房每年约生产100条船的配套设备，现在能达到200至300条船的产能规模。（详情）10月21日，位于苏州浒墅关的ESR国际生物医药创新港正式竣工交付。园区建有3栋三层坡道高标准厂房，单层挑高达10米，光线通透且空间开阔，为高端医疗器械、生物医药企业量身定制了现代化生产场景。04民生热点近日，“英才筑家”人才购房季首场活动在苏州工业园区房产超市举行，吸引100余位人才到场参与。据了解，自即日起至12月31日，我市将开展“英才筑家”人才购房季系列活动，在全市范围内组织近20场人才购房专项服务，为人才提供安居支持。（详情）近日，吴中中等专业学校新实训大楼已顺利通过竣工验收，并正式投入使用。项目位于龙翔路333号吴中中等专业学校内北部区域，占地面积约4千平方米，总建筑面积4.2万平方米，分为地上11层及地下1层，可容纳3000余名师生。（详情）近日，来自贵州高山生态产区的特色农产品方竹笋，首次在南环桥市场亮相上市，方竹笋首日上市量约2000斤，批发价在每斤15至18元之间。近日，太仓市沙溪镇老旧小区改造工程迎来历史性时刻，随着利泰社区利泰新村棉纺厂、利泰新村电厂、利泰新村油厂及松墩新村4个老旧小区改造工程完工，沙溪镇自2012年起分批实施的21个老旧小区改造工程全面完成。2025年苏州公开赛·ATPCH75国际男子职业网球挑战赛于10月19日至26日在阳澄湖畔的新建元国际网球中心接续展开。作为ATP挑战赛体系中冠军积分75分的重要赛事，本届比赛吸引了近70名来自全球多个国家和地区的男子网球选手，将在8天赛期内进行近80场单打与双打对决。05国内聚焦近日，可重复使用火箭朱雀三号首飞箭顺利完成加注合练及静态点火试验，进入首飞的关键准备阶段，可用于大型星座组网。最新数据显示，截至目前，全国风电新增并网容量超5784万千瓦，累计并网容量5.8亿千瓦，占全国发电装机容量的15.7%，规模以上企业风电发电量占全社会用电量的10.1%。我国风电装机规模已连续15年稳居世界第一。10月21日，国际乒联公布2025年第43周排名：女单方面，孙颖莎11600分连续第171周霸榜第一，王曼昱8850分排名第二，陈幸同6075分排名第三。男单方面，王楚钦10900分排名第一，林诗栋8075分排名第二，雨果6050分排名第三。从中国国家铁路集团有限公司获悉，今年前三季度，全国铁路发送旅客35.4亿人次，同比增长6%，再创历史同期新高，全国铁路运输安全平稳有序。06服务导览（点击图片跳转查看）江苏省2026年普通高校招生艺术类专业省统考时间及考点安排这个地铁站，怎么没找到卫生间？10月大件垃圾免费清运周来啦~素材来源：苏州发布综合整理海报摄影：喜玛拉雅北坡的鱼点赞+在看分享小伙伴↓↓↓预览时标签不可点微信扫一扫关注该公众号继续滑动看下一个轻触阅读原文苏州发布向上滑动看下一个知道了微信扫一扫使用小程序取消允许取消允许取消允许×分析微信扫一扫可打开此内容，使用完整服务：，，，，，，，，，，，，。 视频小程序赞，轻点两下取消赞在看，轻点两下取消在看分享留言收藏听过'
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

    print(data)
except json.JSONDecodeError as e:
    print(f"JSON解析错误: {e}")
    print(f"原始响应: {resp}")
    # 处理解析失败的情况
    data = {}