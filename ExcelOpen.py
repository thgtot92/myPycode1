import os
import time as tm
import subprocess
import re
import win32com.client
import openpyxl as op
import glob
from openpyxl import load_workbook
import datetime

# xlsx -> open 

# 아침에 와서 시작 위치 확인하고 조정.
# 사용방법 : 1. 기존 사용하는 인포맥스 로우데이터 고급 옵션에 자동저장 기능 활성화 (1분 내지로 추천드립니다.)
#            2. 아침에 인포맥스에서 추출하는 엑셀 이름 #MOD 쪽에 변경해주심 됩니다.
# file path 추출 
cmd = "dir/s/b | findstr "".*.xlsx"" "

f = open('new.txt','w')
sysMsg = subprocess.getstatusoutput(cmd)
f.write(sysMsg[1])
f.close()
 
path_list = []
f2 = open('new.txt', 'r')
line = []
while True :
    line = f2.readline() #한줄씩 읽습니다.
    path_list.append(line)
    if("" == line) :        
        break
 
f3 = open('new2.txt','w')
f3.write(str(path_list))
 
f2.close()
f3.close()

os.system("del new.txt")
os.system("del new2.txt")
# 경로찾기. #MOD   -> ' raw data source '  쪽 변경하면 된다.
matching = [ s for s in path_list if 'raw_data_source' in s]
new_path = str(matching[0])
new_path = new_path.replace("\n", "")
new_path = new_path.split('\\')
print(new_path)

path_result = ""
file_result = new_path[-1]
for i in range(0,len(new_path)-1,1) :
    if i == 0 :
        path_result = new_path[i]
    else :
        path_result = path_result+"\\"+new_path[i]

print(path_result)

file_name = new_path[-1]
file_result = f'{path_result}\{new_path[-1]}'

print("파일명 : " + file_result)
os.system("cd {}".format(path_result))
os.system("{}".format(file_result))



################################### 엑셀 조작하기. ###################################
# # 1번 엑셀 load
# excel = win32com.client.Dispatch("Excel.Application")
# # # 실행된 엑셀의 시각화
# excel.Visible = True
# # # 기존 파일 열기
# wb = excel.Workbooks.Open(file_result)
# ws = wb.ActiveSheet         # 활성화 시트 변수 지정

# # 15초 정도 슬립 (엑셀 적용이 느림.)
# tm.sleep(15)
# new_name = "result_dataset.xlsx"
# result = f'{path_result}\{new_name}'
# wb.SaveAs(result)

# wb.Close()
# excel.Quit()

# # 2번 엑셀 로드. 삭제해야 한다. (중복 오류 해결 못함.)
# # 새로생성된 result_dataset에 첫시트를 testdata.csv에 행추가로 해주기.
# excel2 = win32com.client.Dispatch("Excel.Application")
# excel2.Visible = True
# new_result = f'{path_result}\{new_name}'
# new_name2= "testdata.csv"
# new_result2 = f'{path_result}\{new_name2}'

# wb1 = excel2.Workbooks.Open(new_result)
# tm.sleep(20)
# wb2 = excel2.Workbooks.Open(new_result2)
# wb1.Worksheets("data").Copy(After=wb2.Worksheets("testdata"))
# #1차 저장
# wb2.Save()
# # 일단 시트 복사 후 처리해보기.
# ws1 = wb2.Worksheets("data")         # 활성화 시트 변수 지정
# ws2 = wb2.Worksheets("testdata")         # 활성화 시트 변수 지정
# # Temp
# ws3 = wb2.Worksheets.Add()
# ws3.Name = "Temp"
# ws1.Range("A5:NB5").Copy()
# ws3.Range("A1:NB1").PasteSpecial(-4163)  

# ws2.Range("A2:NB2").Insert() # 행추가
# ws3.Range("A1:NB1").Copy(ws2.Range("A2:NB2")) 
# # 날짜 바꾸기. 당일자로 들어오는 날짜가 뭉개져서 들어온다 이거 변경
# now = datetime.datetime.now()
# one_day = datetime.timedelta(days=1)
# yesterday = now - one_day
# formatted_date = yesterday.strftime("%Y-%m-%d")

# ws2.Cells(2,1).Value = formatted_date

# # End 삭제하고 끝내자.
# wb2.Worksheets('data').Delete()
# wb2.Worksheets('Temp').Delete()

# result_file_name = "result_dataset.csv"
# result_full_name = f'{path_result}\{result_file_name}'
# wb2.SaveAs(result_full_name)

# excel2.Quit()
# os.system("del {}".format(result))









