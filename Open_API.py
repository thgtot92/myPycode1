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

# ✅ DB 연결
conn = pymysql.connect(
    host='localhost',
    user='root',
    db='open_api_info_db',
    password='920511',
    charset='utf8mb4'
)

# KR6355951D64 여기까지함
#종목정보를 직접 입력해야 하는 불편함이 있기때문에, 인포에서 잔존종목 다 가져와서 엑셀 -> 리스트로 만들어서 loop!
file_path ='./sample_list.xlsx'
table_name ='bnd0001'
try :
    dataset_list = pd.read_excel(file_path,engine="openpyxl")
    dataset_list = dataset_list[1:]
except Exception as e:
    print(f"❌ 엑셀 파일을 읽는 중 오류 발생: {e}")
    exit()

Code_list = dataset_list.iloc[:,0:1]
print(Code_list.iat[1,0])
# ID : E240562
# PW : 123456789a
# session request
session = requests.Session()

# 세선 검증 x
session.verify = False

# gov_hist : 일별 종목조회
api_url = 'https://infomaxy.einfomax.co.kr/api/bond/basic_info'

# 접속 기본정보
#connect_info = {"ID":"E240562","PW":"123456789a'}

# 종목정보 종목코드/일자 조회                
#params = {"stdcd":"KR103502GEC4","bonddate":"20250218"}
for a in range(0, len(Code_list),1) :
    
    # 120개 씩 분당 제한이 있는거 같다. 60개 하고 1분 뒤 재처리 테스트트
    if a % 60 == 1 :
        print("{}번째 60sec sleep".format(a))
        time.sleep(60)

    params = {"stdcd":Code_list.iat[a,0],"inttype_1":"","issuedate":"","expidate":""}
    
    # 헤더부 (인증키 입력)
    headers = {"Authorization" : 'bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJFMjQwNTYyIiwiY291cG9uVHlwZSI6ImFwaSIsInN2YyI6ImluZm9tYXgiLCJpYXQiOjE3Mzk4NjQ5OTYsImV4cCI6MjY4NTk0NDk5Nn0.VCRaCvEkJI7K6v_qSPSC_pAP5ojMYYHYoaW_Oj6fuxU'}

    # 수신부
    r = session.get(api_url, params = params, headers = headers)

    # 정렬. ensure_ascii = 한글 깨짐 방지. indent = 들여쓰기.
    data = json.dumps(r.json(), ensure_ascii=False, indent=2)  # JSON 응답을 Python 객체로 변환

    # 잘 들어왔는지 확인
    contents = r.text
    pp = pprint.PrettyPrinter(indent=4)

    #print(pp.pprint(contents))
    # read_json 으로 할 경우 nest 형태로 나오기 때문에 사용 불가능.
    #df = pd.read_json(data)
    #print(df)
    sample_json = json.loads(data)
    sample_josn_pandas = pd.DataFrame(sample_json['results'])
    print(sample_josn_pandas)

    # 컬럼
    columns = ["stdcd","shortcd","bondnm",\
    "engnm","compnm","issuedate","presaledate","expidate","issuerate","repayrate","couponrate","issueamt","intpayterm","lstgb","lstdate","lstclosedate","lstamt","gurttype","optionkind",\
    "agentorg","rcvorgon","substprice","currencygb","collectgb","subordbond","ksccd","absgb","bhgigwancd","inttype_1","crdtparcomp1","crdtparcomp2","crdtparcomp3","crdtparcomp4",\
    "crdtparrate1","crdtparrate2","crdtparrate3","crdtparrate4","hybridgb","aclass","bclass","cclass","wonissueamt","wonlstamt","estyld","estdanga","duration","exbalcond","condcapcertgb"
    ]
    placeholders = ["%s" for _ in columns]

    cur = conn.cursor()

    # ✅ Debugging
    print(f"Dataset Columns: {sample_josn_pandas.shape[1]}, Expected: {len(columns)}")
    if sample_josn_pandas.shape[1] != len(columns):
        print("❌ 데이터셋의 컬럼 개수가 SQL 컬럼과 일치하지 않습니다. 데이터셋을 확인하세요.")
        #exit() # SKIP
        print("{} 해당 종목 SKIP".format(columns))
        continue
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
            cur.executemany(sql_insert, data_list)
            conn.commit()
            print("✅ 종목코드 : {} 데이터 삽입 완료!".format(Code_list.iat[a,0]))
        except pymysql.MySQLError as e:
            conn.rollback()
            print(f"❌ MySQL 오류 발생: {e}")
            continue  # 다음 종목코드로 스킵

cur.close()
conn.close()