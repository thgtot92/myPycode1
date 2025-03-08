# 금리위험액.
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd

# 개별위험액 산출.
def Individual_Risk_Price_Rate (Spc, Grad, Month) :
    # 채권 구분: 유동화냐 우량이냐..
    #Spec_list = ['KUK','Youdong','WooRyang'] 
    Credit_Grad_WooRyang_AAA_AA     =  ['AAA','AAA0','AAA-','AA+','AA0','AA-','AAA','AA']
    Credit_Grad_WooRyang_AP_AM      =  ['A+','A0','A-','A'] 
    Credit_Grad_WooRyang_BBBP_BBBM  =  ['BBB+','BBB0','BBB-','BBB'] 
    Credit_Grad_WooRyang_No_Grad    =  6.0
    #유동화채권
    if Spc == "Youdong" : 
        if Grad == "AAA" :
            if Month <= 6 :
                Price_Rate = 0.5
            elif Month > 6 or Month <= 24  :
                Price_Rate = 1
            else :
                Price_Rate = 1.6
        elif Grad == "AA" :
            if Month <= 6 :
                Price_Rate = 1.6
            elif Month > 6 or Month <= 24  :
                Price_Rate = 2.4
            else :
                Price_Rate = 4.0
        elif Grad == "A" :
            if Month <= 6 :
                Price_Rate = 4.0
            elif Month > 6 or Month <= 24  :
                Price_Rate = 6.0
            else :
                Price_Rate = 8.0
        elif Grad == "BBB" :
            Price_Rate = 8.0
        else :
            Price_Rate = 8.0
    elif Spc == "WooRyang" :
        #우량채권
        if Credit_Grad_WooRyang_AAA_AA.count(Grad) > 0 :
            if Month <= 6 :
                Price_Rate = 0.25
            elif Month > 6 or Month <= 24  :
                Price_Rate = 0.5
            else :
                Price_Rate = 1.0
        elif Credit_Grad_WooRyang_AP_AM.count(Grad) > 0 :
            if Month <= 6 :
                Price_Rate = 0.5
            elif Month > 6 or Month <= 24  :
                Price_Rate = 1.0
            else :
                Price_Rate = 1.6
        elif Credit_Grad_WooRyang_BBBP_BBBM.count(Grad) > 0 :
            if Month <= 6 :
                Price_Rate = 1.0
            elif Month > 6 or Month <= 24  :
                Price_Rate = 1.6
            else :
                Price_Rate = 2.4
        else :
                Price_Rate = 6.0
    else :
        #KUK
        Price_Rate = 0

    return Price_Rate


# 일반위험액 산출.
# Spec_Name : 종목명 
# Coupon_Price : 액면가액 
# Left_Month : 잔존만기
# Coupon_Method: 이자지급방법 
# Market_Price : 시장가격 (+ long (매수) / - short (매도)) 
def General_Risk_Price (Spec_Name,Coupon_Price ,Left_Month, Coupon_Method, Market_Price):
    # 1. 가중치
    Add_point = 0
    # 0. 포지션분해. (소그룹 1 ~ 3)
    # 12개월 이내 <소그룹 1>
    if Left_Month < 12:
        if Left_Month < 1:
            Add_point = 0
        elif Left_Month >=1 or Left_Month < 3 :
            Add_point = 0.002
        elif Left_Month >=3 or Left_Month < 6 :
            Add_point = 0.004
        elif Left_Month >= 6 or Left_Month <12:
            Add_point = 0.007
        else :
            print("Month Error")
    First_Price = Market_Price * Add_point 

    # 48개월(4년 이내) 이내 <소그룹 2>
    elif Left_Month >=12 or Left_Month <48 :


    # 48개월(4년 이후부터) 이상 <소그룹 3> 
    elif Left_Month >=48 :


    else :
        break


        # 1. 매입포지션과 매도포지션 분리
    
        # 2. 가중매입(매도)포지션 산출

        # 3.

    return Price


# 개별위험액 산정.
# 
try : 
    Price = int(input("가격 입력 : "))
    Risk_Prie_Rate  = Individual_Risk_Price_Rate('WooRyang','A+',3) * 0.01
    print(Risk_Prie_Rate*Price)
except KeyError:
    print("Key Error")

