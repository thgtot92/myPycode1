import pymysql
import pandas as pd
import openpyxl



# 🔹 DB 연결
conn = pymysql.connect(

    host='localhost',
    user='root',
    db='open_api_info_db',
    password='920511',
    charset='utf8mb4'
)

cur = conn.cursor()


# SELECT
sql = 'SELECT DISTINCT STDCD FROM OPEN_API_INFO_DB.BND0011'
cur.execute(sql)
result = cur.fetchall()


result = pd.DataFrame(result)
print(result)