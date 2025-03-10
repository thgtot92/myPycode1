import pymysql
import pandas as pd
import openpyxl
import numpy as np

## 인포맥스 데이터 삽입
# TABLE \\xEC\\xA7\\x80\\xEB\\xB0\\xA9 오류 발생 시
# ALTER TABLE bond_grade_qum CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# 테이블명 데이터 셋 만 바꿔서 사용하면 신규 생성 가능

# ✅ DB 연결
conn = pymysql.connect(
    host='localhost',
    user='root',
    db='myself',
    password='920511',
    charset='utf8mb4'
)

cur = conn.cursor()

# ✅ 엑셀 파일 및 시트 이름
# 변경경
file_path = "./data_matrix_rate_infomax_ver01.xlsx"
sheet_name = 'hsaAAA'

try:
    data_frames = pd.read_excel(file_path, engine="openpyxl", sheet_name=sheet_name)
except Exception as e:
    print(f"❌ 엑셀 파일을 읽는 중 오류 발생: {e}")
    exit()


# 변경경
table_name = 'bond_hsa'

# ✅ 데이터 정제 (4번째 행부터)
dataset = data_frames.iloc[2:].copy()

# ✅ 날짜 컬럼 변환 (VARCHAR(8) 형식: YYYYMMDD)
dataset.iloc[:, 0] = pd.to_datetime(dataset.iloc[:, 0], errors='coerce').dt.strftime('%Y%m%d')

# ✅ NaN 값을 None으로 변환 (MySQL NULL 처리)
# ✅ NaN 값을 None으로 변환 (MySQL NULL 처리)
dataset = dataset.where(pd.notna(dataset), None)
dataset = dataset.replace({np.nan: None})  # np.nan 값 변환
dataset.fillna(value=0, inplace=True)  # 남아 있는 NaN 변환

# ✅ 데이터 타입 변환 (숫자 컬럼이 있다면)
for col in dataset.columns[1:]:
    dataset[col] = pd.to_numeric(dataset[col], errors='coerce')

# ✅ '채권분류' 및 '세부' 컬럼 추가
dataset['채권분류'] = 'KTB'
dataset['세부'] = 'KTB'

# ✅ Expected Columns in MySQL Table
columns = [
    "Date_col",  "Under_3M", "Under_6M", "Under_9M", "Under_1Y", "Under_1_5Y", "Under_2Y",
    "Under_2_5Y", "Under_3Y", "Under_4Y", "Under_5Y", "Under_7Y", "Under_10Y", "Under_15Y", "Under_20Y", \
    # "Under_30Y", "Under_50Y",
    "Bond_GBN", "Bond_Detail"
]
placeholders = ["%s" for _ in columns]

# ✅ Debugging
print(f"Dataset Columns: {dataset.shape[1]}, Expected: {len(columns)}")
if dataset.shape[1] != len(columns):
    print("❌ 데이터셋의 컬럼 개수가 SQL 컬럼과 일치하지 않습니다. 데이터셋을 확인하세요.")
    exit()

# ✅ SQL INSERT 문 생성
sql_insert = "INSERT INTO {} ({}) VALUES ({})".format(
    table_name, ', '.join(columns), ', '.join(placeholders)
)

print(f"SQL Insert Statement: {sql_insert}")
print(f"Expected Columns: {len(columns)}, Expected Placeholders: {len(placeholders)}")

# ✅ 데이터 리스트 변환
data_list = [tuple(row) for row in dataset.itertuples(index=False, name=None)]

# ✅ 첫 번째 데이터 샘플 확인
print(f"First Tuple to Insert: {data_list[0]}")

# ✅ 실행 및 예외 처리
try:
    cur.executemany(sql_insert, data_list)
    conn.commit()
    print("✅ 데이터 삽입 완료!")
except pymysql.MySQLError as e:
    conn.rollback()
    print(f"❌ MySQL 오류 발생: {e}")
finally:
    cur.close()
    conn.close()
