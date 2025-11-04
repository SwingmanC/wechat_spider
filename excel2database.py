import pandas as pd
import numpy as np
import oracledb

def upload(file_path):
    user = 'ydzw'
    password = 'YDzwi769hja6'
    host = '10.33.222.38:30024'
    service_name = 'psz'
    conn_str = f"{user}/{password}@{host}/{service_name}"
    connect = oracledb.connect(conn_str)
    cursor = connect.cursor()

    df = pd.read_excel(file_path, sheet_name=0)
    df = df.replace(np.nan, '')

    cursor.execute('select max(busi_id) from t_sc_busi_detail')
    busi_id = cursor.fetchall()[0][0]
    if busi_id is None:
        busi_id = 1
    else:
        busi_id += 1

    for index, item in df.iterrows():
        if item['商机概述'] != '':
            print(item['商机概述'])
            county = item['区县']
            county = county.replace('苏州', '')
            if county.find('高新') != -1:
                county = '新区'
            if county.find('姑苏') != -1 or county.find('相城') != -1 or county.find('吴中') != -1:
                county = county.replace('区', '')
            cursor.execute('insert into t_sc_busi_detail values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,sysdate)',
                           (busi_id,county,item['发布日期'],item['单位名称'],item['商机类型'],item['商机概述'],
                            item['涉及金额（万元）'],item['公众号'],item['文章标题'],item['链接']))
        busi_id += 1

    connect.commit()
    cursor.close()
    connect.close()

upload(file_path='D:/ipa/商机挖掘/output/20251103/output_20251103.xlsx')