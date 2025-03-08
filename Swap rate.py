import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

# import raw data
df = pd.read_csv("c:/Users/hanyoungjae/myPycode/myPycode/testdata.csv",encoding='cp949')

# Get rid of NA
df= df.dropna()

# 산금1 - irs pay 스프레드
data1 = (df['산금1'] - df['IRS pay 1'] )

# 산금3 - irs pay 3 스프레드
data2 = (df['산금3'] - df['IRS pay 3'] )
df["산금3-irs3"] = data2

# 일자별 group by 
df['일자'] = pd.to_datetime(df['일자'])

# Make plots
fig, ax = plt.subplots()

# 눈금위치와 레이블 설정
ax.set_xticks(df['일자'] )
ax.set_xticklabels(df['일자'].dt.strftime("%Y-%m-%d"))

# 데이터 그리기
ax.plot(df['일자'],df['산금3'], 'r', label = '산금3')
ax.plot(df['일자'],df['IRS pay 3'], 'b', label = 'irs3')
ax.plot(df['일자'],df['산금3-irs3'], 'g' , label = '산금3-irs3')




# 세로축 설정
plt.grid(True, axis='y', color='black', alpha=0.5, linestyle='--')
plt.legend()
plt.show()

#print(df)

# 필요한 사항.
# 1.원하는 종목 지정 (산금3, irs3)
#
#
# 2.원하는 시작~ 종료일자 지점 입력
#
# 
# 3. 입력된 기간동안 일드커브 보여주기.

# ############### 1.시작일자 ############### _HJY
# Start = (input("조회시작일자 입력 (숫자만): "))  
# Start_Year = Start[:4]
# Start_Month = Start[4:6]
# Start_Date = Start[6:8]
# Start_day = str(Start_Year+"-"+Start_Month+"-"+Start_Date)
# Start_day = Start_day[0:12]
# #print(" 발행일자 : {}-{}-{}".format(Start_Year,Start_Month,Start_Date))
# Start_day = datetime.strptime(Start_day,"%Y-%m-%d")

# ################ 2.종료일자 ############### _HJY
# End = (input("조회마지막일자 입력 (숫자만): "))  
# End_Year = End[:4]
# End_Month =End[4:6]
# End_Date = End[6:8]
# End_day = str(End_Year+"-"+End_Month+"-"+End_Date)
# End_day = End_day[0:12]
# #print(" 만기일자 : {}-{}-{}".format(End_Year,End_Month,End_Date))
# End_day = datetime.strptime(End_day,"%Y-%m-%d")