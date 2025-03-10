import win32com.client
import time

# 엑셀 파일 경로
file_path = r"C:\Users\infomax\Desktop\python\test_infomax_data.xlsx"  # 경로를 실제 파일 경로로 변경

# 엑셀 실행
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = True  # 엑셀 창을 보이게 설정 (필요 시 False로 변경)

# 워크북 열기
wb = excel.Workbooks.Open(file_path)

# 자동 저장 기능 활성화 (1분 간격)
save_interval = 60  # 초 단위 (1분)
time.sleep(save_interval)
# while True:
#     time.sleep(save_interval)  # 지정된 시간만큼 대기
#     wb.Save()  # 자동 저장
#     print("자동 저장 완료")

# 종료 시 사용
wb.Close(SaveChanges=True)
excel.Quit()
