import time
import requests
import warnings
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

import setting
from setting import proxies
from setting import page_num

warnings.filterwarnings("ignore")

# 一个处理返回结果的函数
def dealspring(prostring):
    return json.loads(prostring["publish_page"])['publish_list']

# 获取公众号文章链接
def geturl(file_path):

    root = 'D:/ipa/商机挖掘/公众号爬虫/'
    df = pd.read_excel(file_path, sheet_name=0)
    output_name = datetime.now().strftime("%Y%m%d")

    wechat_accounts_fakeid = {}
    for index,item in df.iterrows():
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
    print(wechat_accounts_fakeid)
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
                if passages[len(passages)-1][2] < '2025-10-01':
                    break
                else:
                    begin_index += page_num
                    time.sleep(1)
            except Exception as e:
                print(f"发生异常: {e}")
                break
        time.sleep(2)

    response.close()

    # 公众号文章爬虫
    for item in sum_data:
        key = item[0]
        print("目前爬取的公众号和文章是：", key + '   ' + item[1])

        if os.path.exists(root + key + '/' + item[1] + '.txt'):
            continue

        if os.path.exists(root + key) is False:
            os.mkdir(root + key)

        response = requests.get(item[3], headers=setting.headers, proxies=proxies, verify=False)
        # 在这里处理正常响应的逻辑
        soup = BeautifulSoup(response.text, 'lxml')
        html_text = soup.text.replace(" ", "").replace("\n", "")

        with open(root + key + '/' + item[1] + '.txt', 'w', encoding='utf-8') as f:
            f.write(html_text)

    result_df = pd.DataFrame(sum_data, columns=['公众号', '文章标题', '日期', '链接'])
    result_df.to_excel(root + output_name + '.xlsx', index=False)

if __name__ == "__main__":
    file_path = 'D:/ipa/商机挖掘/公众号v1.xlsx'
    geturl(file_path=file_path)
