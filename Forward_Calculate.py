# ## 채권이론가격 계산기 ###
# 3개 종목
# 종목 갯수에 따른 바스켓 구성.
# ###############  _HJY 에 구분된 입력값 없이 가능하도록 변경
# ** 현재는 입력하는 값에 따라 달라지게 구성되어 있으나 추후 종목 고정 변경 예정
# ** 변경되는 91Cd, Call 금리, 유통수익률만 입력하여 계신되도록 변경


## 최종은 csv 파일 넣고 계산되도록 변경 예정.

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

global CD_Rate
global CALL_Rate


# 0. 바스켓 구성 종목 수 
########## ########## ########## Start Build Fuction ########## ########## ########## 
def Fixed_Income_Calculator(basket_num, basket_list) :
    #바스켓 종목 구하기.
    Temp_data = []
    for basktet_number in range(0,basket_num) :

        Name = (input("종목명 : "))  
        ############### 1.발행일자 ############### _HJY
        Start = (input("발행일 입력 (숫자만): "))  
        Start_Year = Start[:4]
        Start_Month = Start[4:6]
        Start_Date = Start[6:8]
        Start_day = str(Start_Year+"-"+Start_Month+"-"+Start_Date)
        Start_day = Start_day[0:12]
        #print(" 발행일자 : {}-{}-{}".format(Start_Year,Start_Month,Start_Date))
        Start_day = datetime.strptime(Start_day,"%Y-%m-%d")

        ################ 2.만기일자 ############### _HJY
        End = (input("만기일 입력 (숫자만): "))  
        End_Year = End[:4]
        End_Month =End[4:6]
        End_Date = End[6:8]
        End_day = str(End_Year+"-"+End_Month+"-"+End_Date)
        End_day = End_day[0:12]
        #print(" 만기일자 : {}-{}-{}".format(End_Year,End_Month,End_Date))
        End_day = datetime.strptime(End_day,"%Y-%m-%d")

        ################ 3.이표주기 ############### _HJY
        Coupon_Peroid = int(input("이표주기 (개월):  "))

        ################ 이표지급일자 ############### _HJY
        Month_list = pd.period_range(Start_day,End,freq=str(str(Coupon_Peroid)+"M"))
        New_month_list = []
        for month_list in Month_list :
            New_month_list.append(str(month_list)+"-"+Start_Date) 
            
        #print("발행일 기준 이표 지급 계획일자 : {} ".format(New_month_list))

        ################ 5.쿠폰rate ############### _HJY
        Coupon_Rate = float(input("쿠폰 금리 (% 단위 입력) : "))
        Coupon_Rate = Coupon_Rate*(0.01)
        #print("쿠폰금리 : {}".format(Coupon_Rate))

        ################ 6.액면가 ############### _HJY
        #Coupon_Price = int(input("액면가 (원): "))
        Coupon_Price = 10000
        #print("액면가 : {0:,d} 원 ".format(Coupon_Price))

        # 쿠폰이자액
        Coupon_Rate_Price = Coupon_Rate*Coupon_Price / (12/Coupon_Peroid)

        ################ 7. 결제일자 / YTM 입력 ############### _HJY
        Settle = (input("결제일자 입력 (숫자만): "))  
        Settle_Year = Settle[:4]
        Settle_Month = Settle[4:6]
        Settle_Date = Settle[6:8]
        Settle_day = str(Settle_Year+"-"+Settle_Month+"-"+Settle_Date)
        Settle_day = Settle_day[0:12]
        #print(" 결제일자 : {}-{}-{}".format(Settle_Year,Settle_Month,Settle_Date))
        Settle_day = datetime.strptime(Settle_day,"%Y-%m-%d")

        YTM_Rate = float(input("만기수익률 : (%입력)"))
        YTM_Rate = YTM_Rate*(0.01)

        # 8.결제일자 기준 다음 이표지급일자 :

        i = 0
        for Month_list_day in New_month_list :
            i += 1
            if Settle_day <= datetime.strptime(Month_list_day,"%Y-%m-%d") :
                Next_Coupon_day = Month_list_day
                #print("결제일 다음 이표지급일 : {} ".format(Next_Coupon_day))
                break
            
        Pre_Coupon_day   = New_month_list[i-2]
        #print("결제일 직전 이표지급일 : {}".format(Pre_Coupon_day)   )

        # # 일자 차이. # #
        Settle_diff_Coupon_day = pd.to_datetime(Next_Coupon_day) - pd.to_datetime(Settle_day)
        Coupon_diff_Next_Coupon_day = pd.to_datetime(Next_Coupon_day) - pd.to_datetime(Pre_Coupon_day)

        #print(" 결제일-이표일 {} 일 // 이표 - 다음이표 {} 일 ".format(Settle_diff_Coupon_day, Coupon_diff_Next_Coupon_day))

        # 9.결제일 기준 이표지급 날짜 생성.
        Coupon_Days = []
        for c_d in New_month_list :
            # 이표시작~ 만기일까지 append.
            if datetime.strptime(c_d,"%Y-%m-%d") >= datetime.strptime(Next_Coupon_day,"%Y-%m-%d") :
                Coupon_Days.append(c_d)
            else :
                pass

        #print("결제일 기준 쿠폰지급일자 :  {} ".format(Coupon_Days))

        # 10. pandas 사용하여 데이터 프레임 생성.

        p = 0
        data = { 'Count_Index' : [i for i in range(1,len(Coupon_Days)+1)],
                'Duration_Index' :[i/(12/Coupon_Peroid) for i in range(1,len(Coupon_Days)+1)],
                'Coupon Days' : Coupon_Days ,
                'Coupon_Rate_Price' : [Coupon_Rate_Price for i in range(1,len(Coupon_Days)+1)]
                }

        # 프레임 생성
        df = pd.DataFrame(data)

        #print(df)

        # PV구하기  :
        PV_List = []
        DU_List = []
        numb = 0
        for numb in range(0,len(Coupon_Days)) :
            a =  float(df.loc[numb ,['Count_Index']])
            b =  float(df.loc[numb ,['Coupon_Rate_Price']])
            x =  float(df.loc[numb ,['Duration_Index']])
            PV_List.append(round(b   / (1+YTM_Rate/(12/Coupon_Peroid))**(a-1),3)  )
            DU_List.append(round(b*x / (1+YTM_Rate/(12/Coupon_Peroid))**(a-1),3)  )

        data2 = { 'Count_Index' : [i for i in range(1,len(Coupon_Days)+1)],
                'PV' : PV_List ,
                'DU' : DU_List}
        df2 = pd.DataFrame(data2)

        PV_data = pd.merge(df,df2,on='Count_Index')
        print(PV_data)

        # 11.만기일 상환금액 :
        c = int(PV_data.loc[len(Coupon_Days)-1,'Count_Index']) # index라서-1
        d = float(PV_data.loc[len(Coupon_Days)-1,'Duration_Index']) # index라서-1
        Last_price    = round( Coupon_Price/ (1+YTM_Rate/(12/Coupon_Peroid))**(c-1),3) 
        Last_du_price = Last_price * d
        PV_SUM = PV_data['PV'].sum() + Last_price
        DU_SUM = PV_data['DU'].sum() + Last_du_price
        #print("총합 : {}".format(PV_SUM))
        #print("총합 : {}".format(DU_SUM))

        # 12.최종 채권 단가 계산 :
        Fixed_Income_Price = round(PV_SUM /(1+YTM_Rate/(12/Coupon_Peroid)*Settle_diff_Coupon_day.days/Coupon_diff_Next_Coupon_day.days),2)

        # 13.듀레이션 구하기 :
        Fixed_Income_Duration =  round(DU_SUM / Fixed_Income_Price,1)
        print("############# 최종 채권 단가계산 : {0:10,.2f} 원 #############".format(Fixed_Income_Price))
        print("############# 최종 채권 듀레이션 : {} 월 #############".format(Fixed_Income_Duration))
        
        # Temp_data 저장.
        Temp_data.append([Name,Fixed_Income_Price])

    Fixed_Income_Price_List_Column = pd.DataFrame(Temp_data,columns=['종목명','채권단가'])

    return Fixed_Income_Price_List_Column

########## ########## ########## End Build Fuction ########## ########## ########## 

basket_number_call = int(input("종목 수량 : "))
basket_list = []

# Call Fuction.
basket_list  = Fixed_Income_Calculator(basket_number_call,basket_list)
# print basket list 
print(basket_list)

# B.선도가격 구하기.



