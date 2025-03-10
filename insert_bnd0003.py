import sys
import json
import requests
import pandas as pd
import numpy as np
import pymysql
import pprint
from urllib.request import urlopen
import openpyxl
import time
from datetime import datetime

# ✅ DB 연결
conn = pymysql.connect(
    host='localhost',
    user='root',
    db='open_api_info_db',
    password='920511',
    charset='utf8mb4'
)

# Today
today_yyyymmdd = datetime.today().strftime("%Y%m%d")

# table 
table_name ='bnd0003'

# session request
session = requests.Session()

# 세선 검증 x
session.verify = False

# gov_hist : 일별 조회회
api_url = 'https://infomaxy.einfomax.co.kr/api/bond/marketvaluation'

cur = conn.cursor()

# SELECT
sql = 'SELECT DISTINCT STDCD FROM OPEN_API_INFO_DB.BND0011'
cur.execute(sql)
result = cur.fetchall()

result = pd.DataFrame(result)

for a in range(0,len(result),1)  :
    
    # 종목명
    print(" 첫번재 insert 종목 : {}".format(result.iloc[a,0]))

    # # 헤더부 (인증키 입력)
    headers = {"Authorization" : 'bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJFMjQwNTYyIiwiY291cG9uVHlwZSI6ImFwaSIsInN2YyI6ImluZm9tYXgiLCJpYXQiOjE3Mzk4NjQ5OTYsImV4cCI6MjY4NTk0NDk5Nn0.VCRaCvEkJI7K6v_qSPSC_pAP5ojMYYHYoaW_Oj6fuxU'}

    # 파라미터
    params = {"stdcd":result.iloc[a,0],"bonddate":today_yyyymmdd }

    # # 수신부
    r = session.get(api_url, params = params, headers = headers)

    # # 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
    data = json.dumps(r.json(), ensure_ascii=False, indent=2)  # JSON 응답을 Python 객체로 변환

    # # 잘 들어왔는지 확인
    contents = r.text
    pp = pprint.PrettyPrinter(indent=4)

    sample_json = json.loads(data)
    sample_josn_pandas = pd.DataFrame(sample_json['results'])
    print(sample_josn_pandas)
    print(len(sample_josn_pandas))

    # # 컬럼
    # 컬럼
    columns = ["bonddate","stdcd","estyldt","estpricet","calcyldt","estyldf","estpricef","calcyldf"]

    placeholders = ["%s" for _ in columns]

    cur2 = conn.cursor()

    # ✅ Debugging
    print(f"Dataset Columns: {sample_josn_pandas.shape[1]}, Expected: {len(columns)}")
    if sample_josn_pandas.shape[1] != len(columns):
        print("❌ 데이터셋의 컬럼 개수가 SQL 컬럼과 일치하지 않습니다. 데이터셋을 확인하세요.")
        print("{} 해당 종목 SKIP".format(columns))
    else :
        # ✅ SQL INSERT 문 생성
        sql_insert = "INSERT INTO {} ({}) VALUES ({})".format(
            table_name, ', '.join(columns), ', '.join(placeholders)
        )
        print(f"SQL Insert Statement: {sql_insert}")
        print(f"Expected Columns: {len(columns)}, Expected Placeholders: {len(placeholders)}")

        # ✅ 데이터 리스트 변환
        data_list = [tuple(row) for row in sample_josn_pandas.itertuples(index=False, name=None)]

        # ✅ 첫 번째 데이터 샘플 확인
        print(f"First Tuple to Insert: {data_list[0]}")

        # ✅ 실행 및 예외 처리
        try:
            cur2.execute(sql_insert, data_list[0])
            conn.commit()
            print("✅ 종목코드 : {} 데이터 삽입 완료!".format(data_list[0]))
        except pymysql.MySQLError as e:
            conn.rollback()
            print(f"❌ MySQL 오류 발생: {e}")
            exit()  # 다음 종목코드로 스킵

cur.close()
conn.close()