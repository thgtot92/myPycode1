import pymysql
import pandas as pd
import numpy as np
import openpyxl

## 퀀텀 전체 데이터 삽입

# TABLE \\xEC\\xA7\\x80\\xEB\\xB0\\xA9 오류 발생 시
# ALTER TABLE bond_grade_qum CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# ✅ DB 연결
conn = pymysql.connect(
    host='localhost',
    user='root',
    db='myself',
    password='920511',
    charset='utf8mb4',  # utf8mb4는 한글 + 이모지까지 지원
    use_unicode=True,
     cursorclass=pymysql.cursors.DictCursor
)

cur = conn.cursor()

# ✅ 업로드된 파일 경로로 변경
file_path = "./quantum_data.xlsx"
sheet_name = 'all_data'

try:
    # ✅ 한글 데이터 깨짐 방지: dtype=str 적용
    data_frames = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl", dtype=str)
    
    # ✅ 한글 인코딩 변환 제거 (Pandas는 기본적으로 UTF-8을 지원)
    data_frames.head()

except Exception as e:
    print(f"❌ 엑셀 파일을 읽는 중 오류 발생: {e}")
    exit()

table_name = 'bond_all_data'

# ✅ 데이터 정제 (2번째 행부터 사용)
dataset = data_frames.copy()

# ✅ 날짜 컬럼 변환 (VARCHAR(8) 형식: YYYYMMDD)
dataset.iloc[:, 0] = pd.to_datetime(dataset.iloc[:, 0], errors='coerce').dt.strftime('%Y%m%d')
dataset.iloc[:, 0].fillna('', inplace=True)  # NaT 처리

# ✅ NaN 값을 None으로 변환 (MySQL NULL 처리)
dataset = dataset.where(pd.notna(dataset), None)
dataset = dataset.replace({np.nan: None})  # np.nan 값 변환
dataset.fillna(value=0, inplace=True)  # 남아 있는 NaN 변환

# ✅ 데이터 타입 변환 (숫자 컬럼이 있다면)
for col in dataset.columns[4:]:
    dataset[col] = pd.to_numeric(dataset[col], errors='coerce')

# ✅ Expected Columns in MySQL Table
columns = [
    "Date_col", "Bond_GBN", "Bond_Detail", "Bond_FROM", "Under_3M", "Under_6M", "Under_9M", "Under_1Y", "Under_1_5Y", "Under_2Y",
    "Under_2_5Y", "Under_3Y", "Under_4Y", "Under_5Y", "Under_7Y", "Under_10Y", "Under_15Y", "Under_20Y", "Under_30Y", "Under_50Y"
]
placeholders = ["%s" for _ in columns]

# ✅ 컬럼 개수 확인 및 디버깅
print(f"Dataset Columns: {dataset.shape[1]}, Expected: {len(columns)}")
print(f"Dataset Column Names: {dataset.columns.tolist()}")
if dataset.shape[1] != len(columns):
    print("❌ 데이터셋의 컬럼 개수가 SQL 컬럼과 일치하지 않습니다. 데이터셋을 확인하세요.")
    exit()

# ✅ SQL INSERT 문 생성
sql_insert = "INSERT INTO {} ({}) VALUES ({})".format(
    table_name, ', '.join(columns), ', '.join(placeholders)
)

print(f"SQL Insert Statement: {sql_insert}")

data_list = [
    tuple(val.encode('utf-8').decode('utf-8') if isinstance(val, str) else val for val in row)
    for row in dataset.itertuples(index=False, name=None)
]


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
