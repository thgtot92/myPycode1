from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from tkinter.messagebox import *

# GUI
import tkinter as tk
import os
import re
import sys
import time

from tkinter import filedialog
from tkinter import Listbox
from tkinter import *


#  - Version 1 코드로 실행 추후 EXE로 변경하여 입력가능한 지수를 생성하도록 변경 예정 _ HYJ
#  - 입력된 하단 지수에서 호출 
#  - 중간 TAB 이동부터는 현재 해당 PAGE의 내부 3중 구조 IFRAME 이 동적 호출 이후 CSS가 입력되지 않음. 간단하게 TAB으로 해결.
#  - CTRL + F 후 ### 입력 . 하단 부 주석 제거 후 진행하면 생성 완료
#  - 현재 페이지 내 미생성된 기간은 자동으로 set 되기에 날짜 설정은 안하도록 함
def Make_Jisu(CODE):

    # 브라우저 옵션 설정 (요거는 수정 x)
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")

    #크롬 드라이브 Active
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get("https://kis-net.kr/index.do")

        wait = WebDriverWait(driver, 10)

        # iframe 전환
        iframe = wait.until(EC.presence_of_element_located((By.ID, "view")))
        driver.switch_to.frame(iframe)

        # 팝업 닫기 버튼 클릭
        close_button_css = "#mainframe_VFrameSet0_HFrameSet0_VFrameSet1_HomeFrame_MainPopup_titlebar_closebuttonAlignImageElement"
        close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_button_css)))
        close_button.click()

        # 메인 프레임으로 복귀
        driver.switch_to.default_content()

        # 다시 iframe으로 전환
        iframe = wait.until(EC.presence_of_element_located((By.ID, "view")))
        driver.switch_to.frame(iframe)

        # 로그인 버튼 클릭
        login_button_css = "#mainframe_VFrameSet0_TopFrame_form_btn_login"
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_css)))
        login_button.click()

        time.sleep(1)

        # 로그인 ID 입력
        id_input_css = "#mainframe_VFrameSet0_LoginFrame_form_div_login_edt_id_input"
        id_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, id_input_css)))
        id_input.click()
        id_input.send_keys("koreastock06")

        # 비밀번호 입력
        pw_input_css = "#mainframe_VFrameSet0_LoginFrame_form_div_login_edt_pw_input"
        pw_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, pw_input_css)))
        pw_input.click()
        pw_input.send_keys("koreastock06")

        # 로그인 버튼 클릭
        login_button_css = "#mainframe_VFrameSet0_LoginFrame_form_div_login_btn_login > div"
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_css)))
        login_button.click()

        # 지수정보 입력
        jisu_button_css = "#mainframe_VFrameSet0_TopFrame_form_div_menu_btn_topMenu_1000TextBoxElement > div"
        jisu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, jisu_button_css)))
        jisu_button.click()

        jisu_button_css2 = "#mainframe_VFrameSet0_HFrameSet0_LeftFrame_form_div_menu_div_menu_btn_menu_1210TextBoxElement > div"
        jisu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, jisu_button_css2)))
        jisu_button.click()

        jisu_button_css3 = "#mainframe_VFrameSet0_HFrameSet0_LeftFrame_form_div_menu_div_menu_grd_menu_body_gridrow_0_cell_0_0GridCellTextSimpleContainerElement"
        jisu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, jisu_button_css3)))
        jisu_button.click()

        #잠깐 슬립 먹이고 한텀 쉬기.
        time.sleep(3)
        # 여기부터 노가다.

        # 지수 창 선택
        if CODE != 'ALL_LIST' :
            action = ActionChains(driver)
            action.send_keys(Keys.RETURN).perform()

            time.sleep(1)
            # 지수 코드 입력
            action.send_keys(CODE).perform()
            action.send_keys(Keys.RETURN).perform()
            
            time.sleep(3)
            
            # 확인 선택택
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.RETURN).perform()

            # 지수 생성 선택
            time.sleep(1)
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.RETURN).perform()

            # 확인
            time.sleep(1)
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.ENTER).perform()
            
            # 확인 누르기
            time.sleep(2)
            action.send_keys(Keys.TAB).perform()
            action.send_keys(Keys.RETURN).perform()

            # 확인
            time.sleep(1)
            action.send_keys(Keys.TAB).perform()
            # 실제 생성 시 여기 풀어야 합니다. ### 아래 라인 #제거
            #action.send_keys(Keys.RETURN).perform()
        else :
            action = ActionChains(driver)
            action.send_keys(Keys.RETURN).perform()

            time.sleep(1)
            # 4개 지수 리스트
            data_list_all = ['BC240642','BC240647','BC240648','BC240700']
            for i in range(0,len(data_list_all),1):
                # 지수 코드 입력
                CODE = data_list_all[i]
                print(CODE)
                action.send_keys(CODE).perform()
                action.send_keys(Keys.RETURN).perform()

                time.sleep(3)

                # 확인 선택
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.RETURN).perform()

                # 지수 생성 선택
                time.sleep(1)
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()
                action.send_keys(Keys.TAB).perform()

                action.send_keys(Keys.RETURN).perform()

                # 확인
                time.sleep(1) 
                #action.send_keys(Keys.TAB).perform()
                # 실제 생성 시 여기 풀어야 합니다. ### 아래 라인 #제거 
                action.send_keys(Keys.ENTER).perform()
                
                # 확인 누르기
                #time.sleep(1)
                #action.send_keys(Keys.TAB).perform()
                #action.send_keys(Keys.RETURN).perform()

                # 확인
                #time.sleep(1)
                #action.send_keys(Keys.TAB).perform()
                #action.send_keys(Keys.RETURN).perform()

                # shift + tab x 5 원래대로
                time.sleep(1)
                if i != len(data_list_all)-1 :
                    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
                    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
                    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
                    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
                    action.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
                    action.send_keys(Keys.RETURN).perform()

                    #ctrl +A
                    time.sleep(2)
                    action.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()              
                    action.send_keys(Keys.DELETE).perform()  # clear
                else :
                    print("Last list")

        print("### END ###")

    except Exception as e:
        print(f"Error: {e}")
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    finally:
        #생성 완료 후 1차 자동 종료
        driver.quit()
        showinfo("Success","지수 생성 완료")
        
###  Basic Frame ###
# 구조는 선택한 리스트에서 실행되도록 함
def press1() :
    selection = lb1.curselection()
    try: 
        value = lb1.get(selection[0])
        print(value) 
        ent1.insert(0,value)
        # 입력 성공 후 실행 버튼 활성화
        bt2 = tk.Button(root,text ="실행", command=press2)
        bt3 = tk.Button(root,text ="초기화", command=press3)
        bt2.grid(row=6,column=1,sticky="ws")
        bt3.grid(row=6,column=2,sticky="es")    
    except IndexError :
        print("인덱스 미선택")
        showerror("Error","지수가 선택되지 않았습니다.")

def press2 ():
    if len(ent1.get()) < 8 :
        showerror("Error","지수가 선택되지 않았습니다.")
    else :
        Make_Jisu(ent1.get())

def press3 ():
    ent1.delete(0,100)

root = Tk()

root.title("KIS지수 자동 생성기")
root.geometry("200x220")
root.resizable(True,True)

L0 = tk.Label(root, text = "KIS 지수 생성 프로그램")
L0.grid(row=1,column=1,columnspan=3)

L1 = tk.Label(root, text = "종목 리스트")
L1.grid(row=2,column=1,columnspan=3)

lb1 = Listbox(root,selectmode="browse",height=3)
lb1.grid(row=3,column=2)

# 리스트 생성
# 'BC240642' : 안전형 ,'BC240647' : 수익형 
# 'BC240648' : ESG 、'BC240700' : RP
data_list = ['ALL_LIST','BC240642','BC240647','BC240648','BC240700']
b = 0
for i in data_list :
    lb1.insert(b,i)
    b +=1 
       
bt1= tk.Button(root,text="▼ 지수선택 ▼",command=press1)
bt1.grid(row=4,column=1,columnspan=3)

blank = tk.Label(root, text=' ', font=12, height=3)

ent1 = Entry(root)
ent1.grid(row=5,column=1,columnspan=3)
root.mainloop() 

