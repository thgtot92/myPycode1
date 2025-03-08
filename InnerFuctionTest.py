# 1) 1, 2 번 종목 만기일치시킨 이후 수익률 그래프 그림.
# 2) 일자 2개 선택하여 스프레드 출력.
# 3) 현재는.. UI가 후짐. 나중에 개선 생각해봄.
# 4) 데이터셋 적용문제는 여전히 고민중.

import pandas as pd
import numpy as np
import plotly.express as px # 그래픽 간단하게 짤때.
import plotly.graph_objects as go # 그래픽 세부 디자인할떄
import tkinter as tk

import os
import re
import sys

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from matplotlib import dates
from plotly.subplots import make_subplots
from tkinter import filedialog
from tkinter import Listbox
from tkinter import *
from tkinter import ttk


# list box column function
def Make_Listbox_column(data_list, result_col_list) : 
    new_column_list = []
    new_column_list1 = []

    delete_column_list = ["3M","6M","9M","1Y","1.5Y","2Y","2.5","3Y","4Y","5Y","6Y","7Y","8Y","9Y","10Y","15Y","20Y","25Y","30Y"]

    data_list = data_list

    for i in delete_column_list :
        for j in data_list :
            #print(i.find(j), i, j)
            if j.find(i) != -1 :
                i = str(i)
                j = str(j)
                x= j.replace(i,"")
                new_column_list.append(x)
    # 깔끔하게 안빠질 경우..
    for a in new_column_list :
        if a.rfind('Y') != -1:
            a = str(a)
            a = a.replace('Y', '')
            new_column_list1.append(a)
        elif a.rfind('1.') != -1:            
            a = str(a)
            a = a.replace('1.', '')
            new_column_list1.append(a)
        elif a.rfind('2.') != -1:            
            a = str(a)
            a = a.replace('2.', '')
            new_column_list1.append(a)            

    # 빠진거 일단 몇개 채우기.
    new_column_list1.append('기준금리')
    new_column_list1.append('T-bill')
    new_column_list1.append('T-note')
    new_column_list1.append('미정책금리상단')
    new_column_list1.append('미정책금리하단')

    new_column_list1 = pd.DataFrame(new_column_list1)        
    result_col_list = new_column_list1[0].unique()
    return result_col_list.tolist()

# Select Item Handle Function
def Select_Item  (File_path, val, result) :
    # read Csv
    df = pd.read_csv(File_path,encoding='cp949')
    # Get rid of NA (결측치 제거)
    df= df.dropna()

    # df.iloc[0:,1:1] -> 일자
    Date_Frame = pd.DataFrame(df.iloc[0:,0:1])
    if val == '국' :
        # 종목 국채 Data Frame 정제
        Data_guk =  df.iloc[0:,2:17]
        Data_guk = pd.DataFrame(Data_guk)
        Data_guk['date'] = Date_Frame
        Data_guk.insert(0,'date',Data_guk.pop('date'))

        column_data = []

        for i in Data_guk.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[1:]))

        Data_guk.columns = column_data
        result = Data_guk
        return result   
    elif val == '통' :
        # #통안채
        Data_tong = df.iloc[0:,17:24]
        Data_tong = pd.DataFrame(Data_tong)
        Data_tong['date'] = Date_Frame
        Data_tong.insert(0,'date',Data_tong.pop('date'))

        column_data = []

        for i in Data_tong.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[1:]))

        Data_tong.columns = column_data
        result = Data_tong
        return result   
    elif val == '특' :
        # #특은채
        Data_tk = df.iloc[0:,24:39]
        Data_tk = pd.DataFrame(Data_tk)
        Data_tk['date'] = Date_Frame
        Data_tk.insert(0,'date',Data_tk.pop('date'))

        column_data = []

        for i in Data_tk.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[1:]))

        Data_tk.columns = column_data
        result = Data_tk
        return result
    elif val == '산' :
        # #산은채
        Data_san = df.iloc[0:,39:53]
        Data_san = pd.DataFrame(Data_san)
        Data_san['date'] = Date_Frame
        Data_san.insert(0,'date',Data_san.pop('date'))

        column_data = []

        for i in Data_san.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[1:]))

        Data_san.columns = column_data
        result = Data_san
        return result
    # #중
    elif val == '중' :
        Data_jung = df.iloc[0:,53:67]
        Data_jung = pd.DataFrame(Data_jung)
        Data_jung['date'] = Date_Frame
        Data_jung.insert(0,'date',Data_jung.pop('date'))

        column_data = []

        for i in Data_jung.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[1:]))

        Data_jung.columns = column_data
        result = Data_jung
        return result
    elif val == '은' :
        # #은행채
        Data_eon = df.iloc[0:,67:81]
        Data_eon = pd.DataFrame(Data_eon)
        Data_eon['date'] = Date_Frame
        Data_eon.insert(0,'date',Data_eon.pop('date'))

        column_data = []

        for i in Data_eon.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[1:]))

        Data_eon.columns = column_data
        result = Data_eon
        return result
    elif val == '카(AA+)' :
        # #카드채AA+
        Data_cardAAP = df.iloc[0:,81:95]
        Data_cardAAP = pd.DataFrame(Data_cardAAP)
        Data_cardAAP['date'] = Date_Frame
        Data_cardAAP.insert(0,'date',Data_cardAAP.pop('date'))

        column_data = []

        for i in Data_cardAAP.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[6:]))

        Data_cardAAP.columns = column_data
        result = Data_cardAAP
        return result
    elif val == '카(AA0)' :
        # #카드채AA0
        Data_cardAA0 = df.iloc[0:,95:109]
        Data_cardAA0['date'] = Date_Frame
        Data_cardAA0.insert(0,'date',Data_cardAA0.pop('date'))

        column_data = []

        for i in Data_cardAA0.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[6:]))

        Data_cardAA0.columns = column_data
        result = Data_cardAA0
        return result
    elif val == '금(AA-)' :
        # #금AAM
        Data_goldAM = df.iloc[0:,109:123]
        Data_goldAM = pd.DataFrame(Data_goldAM)
        Data_goldAM['date'] = Date_Frame
        Data_goldAM.insert(0,'date',Data_goldAM.pop('date'))

        column_data = []

        for i in Data_goldAM.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[6:]))

        Data_goldAM.columns = column_data
        result = Data_goldAM
        return result
    elif val == '금(A+)' :
        # #금AP
        Data_goldAP = df.iloc[0:,123:137]
        Data_goldAP = pd.DataFrame(Data_goldAP)
        Data_goldAP['date'] = Date_Frame
        Data_goldAP.insert(0,'date',Data_goldAP.pop('date'))

        column_data = []

        for i in Data_goldAP.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[5:]))

        Data_goldAP.columns = column_data
        result = Data_goldAP
        return result
    elif val == '금(A0)' :
        # #금A0
        Data_goldA0 = df.iloc[0:,137:151]
        Data_goldA0 = pd.DataFrame(Data_goldA0)
        Data_goldA0['date'] = Date_Frame
        Data_goldA0.insert(0,'date',Data_goldA0.pop('date'))

        column_data = []

        for i in Data_goldA0.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[5:]))

        Data_goldA0.columns = column_data
        result = Data_goldA0
        return result
    elif val == '회(AA+)' :
        # #회사채AA+
        Data_CompAAP = df.iloc[0:,151:165]
        Data_CompAAP = pd.DataFrame(Data_CompAAP)
        Data_CompAAP['date'] = Date_Frame
        Data_CompAAP.insert(0,'date',Data_CompAAP.pop('date'))

        column_data = []

        for i in Data_CompAAP.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[6:]))

        Data_CompAAP.columns = column_data
        result = Data_CompAAP
        return result
    elif val == '회(AA0)' :
        # #회사채AA0
        Data_CompAA0 = df.iloc[0:,165:179]
        Data_CompAA0 = pd.DataFrame(Data_CompAA0)
        Data_CompAA0['date'] = Date_Frame
        Data_CompAA0.insert(0,'date',Data_CompAA0.pop('date'))

        column_data = []

        for i in Data_CompAA0.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[6:]))

        Data_CompAA0.columns = column_data
        result = Data_CompAA0
        return result
    elif val == '회(AA-)' :
        # #회사채AA-
        Data_CompAAM = df.iloc[0:,179:193]
        Data_CompAAM = pd.DataFrame(Data_CompAAM)
        Data_CompAAM['date'] = Date_Frame
        Data_CompAAM.insert(0,'date',Data_CompAAM.pop('date'))

        column_data = []

        for i in Data_CompAAM.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[6:]))

        Data_CompAAM.columns = column_data
        result = Data_CompAAM
        return result
    elif val == '회(A+)' :
        # #회사채AP
        Data_CompAP = df.iloc[0:,193:207]
        Data_CompAP = pd.DataFrame(Data_CompAP)
        Data_CompAP['date'] = Date_Frame
        Data_CompAP.insert(0,'date',Data_CompAP.pop('date'))

        column_data = []

        for i in Data_CompAP.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[5:]))

        Data_CompAP.columns = column_data
        result = Data_CompAP
        return result
    elif val == '회(A0)' :
        # #회사채A0
        Data_CompA0 = df.iloc[0:,207:221] 
        Data_CompA0 = pd.DataFrame(Data_CompA0)
        Data_CompA0['date'] = Date_Frame
        Data_CompA0.insert(0,'date',Data_CompA0.pop('date'))

        column_data = []

        for i in Data_CompA0.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[5:]))

        Data_CompA0.columns = column_data
        result = Data_CompA0
        return result 
    elif val == '회(A-)' :
        # #회사채AM
        Data_CompAM = df.iloc[0:,221:235]
        Data_CompAM = pd.DataFrame(Data_CompAM)
        Data_CompAM['date'] = Date_Frame
        Data_CompAM.insert(0,'date',Data_CompAM.pop('date'))

        column_data = []

        for i in Data_CompAM.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[5:]))

        Data_CompAM.columns = column_data
        result = Data_CompAM
        return result         
    elif val == '회(BBB+)' :
        # #회사채BBBP
        Data_CompBBBP= df.iloc[0:,235:249]
        Data_CompBBBP = pd.DataFrame(Data_CompBBBP)
        Data_CompBBBP['date'] = Date_Frame
        Data_CompBBBP.insert(0,'date',Data_CompBBBP.pop('date'))

        column_data = []

        for i in Data_CompBBBP.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[7:]))

        Data_CompBBBP.columns = column_data
        result = Data_CompBBBP
        return result         
    elif val == '회(BBB0)' :
        # #회사채BBB0
        Data_CompBBB0= df.iloc[0:,249:263]
        Data_CompBBB0 = pd.DataFrame(Data_CompBBB0)
        Data_CompBBB0['date'] = Date_Frame
        Data_CompBBB0.insert(0,'date',Data_CompBBB0.pop('date'))

        column_data = []

        for i in Data_CompBBB0.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[7:]))

        Data_CompBBB0.columns = column_data
        result = Data_CompBBB0
        return result         
    elif val == '회(BBB-)' :
        # #회사채BBB-
        Data_CompBBBM = df.iloc[0:,263:277]
        Data_CompBBBM = pd.DataFrame(Data_CompBBBM)
        Data_CompBBBM['date'] = Date_Frame
        Data_CompBBBM.insert(0,'date',Data_CompBBBM.pop('date'))

        column_data = []

        for i in Data_CompBBBM.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[7:]))

        Data_CompBBBM.columns = column_data
        result = Data_CompBBBM
        return result        
    elif val == 'IRS' :
        # #IRS
        Data_IRS= df.iloc[0:,277:289]
        Data_IRS = pd.DataFrame(Data_IRS)
        Data_IRS['date'] = Date_Frame
        Data_IRS.insert(0,'date',Data_IRS.pop('date'))

        column_data = []

        for i in Data_IRS.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[3:]))

        Data_IRS.columns = column_data
        result = Data_IRS
        return result               
    elif val == 'CRS' :
        # #CRS
        Data_CRS = df.iloc[0:,289:299]
        Data_CRS = pd.DataFrame(Data_CRS)
        Data_CRS['date'] = Date_Frame
        Data_CRS.insert(0,'date',Data_CRS.pop('date'))

        column_data = []

        for i in Data_CRS.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            else :
                column_data.append((i[3:]))

        Data_CRS.columns = column_data
        result = Data_CRS
        return result            
    elif val == '기준금리' :
        # #기준금리
        Data_BasicRate = df.iloc[0:,1:2]
        Data_BasicRate = pd.DataFrame(Data_BasicRate)
        Data_BasicRate['date'] = Date_Frame
        Data_BasicRate.insert(0,'date',Data_BasicRate.pop('date'))

        column_data = []

        for i in Data_BasicRate.columns :
            column_data.append((i[0:]))
        Data_BasicRate.columns = column_data
        result = Data_BasicRate
        return result        
    elif val == '미정책금리상단' :
        # #미정책금리상단;
        Data_AmBasicRateH= df.iloc[0:,299:300]
        Data_AmBasicRateH = pd.DataFrame(Data_AmBasicRateH)
        Data_AmBasicRateH['date'] = Date_Frame
        Data_AmBasicRateH.insert(0,'date',Data_AmBasicRateH.pop('date'))

        column_data = []

        for i in Data_AmBasicRateH.columns :
            column_data.append((i[0:]))
        Data_AmBasicRateH.columns = column_data
        result = Data_AmBasicRateH
        return result
    elif val == '미정책금리하단' :
        # #미정책금리하단
        Data_AmBasicRateL= df.iloc[0:,300:301]
        Data_AmBasicRateL = pd.DataFrame(Data_AmBasicRateL)
        Data_AmBasicRateL['date'] = Date_Frame
        Data_AmBasicRateL.insert(0,'date',Data_AmBasicRateL.pop('date'))

        column_data = []

        for i in Data_AmBasicRateL.columns :
            column_data.append((i[0:]))
        Data_AmBasicRateL.columns = column_data
        result = Data_AmBasicRateL
        return result
    elif val == 'T-bill' :
        # # T-BIll
        Data_Tbill= df.iloc[0:,301:304]
        Data_Tbill = pd.DataFrame(Data_Tbill)
        Data_Tbill['date'] = Date_Frame
        Data_Tbill.insert(0,'date',Data_Tbill.pop('date'))

        column_data = []

        for i in Data_Tbill.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            elif len(Data_Tbill.columns) == 10 :
                column_data.append((i[0:3]))
            else :
                column_data.append((i[0:2]))
        Data_Tbill.columns = column_data
        result = Data_Tbill
        return result    
    elif val == 'T-note' :
        # # T-note
        Data_TNote= df.iloc[0:,304:311]
        Data_TNote = pd.DataFrame(Data_TNote)
        Data_TNote['date'] = Date_Frame
        Data_TNote.insert(0,'date',Data_TNote.pop('date'))

        column_data = []

        for i in Data_TNote.columns :
            if i == 'date':
                column_data.append((i[0:]))
                continue
            elif len(Data_TNote.columns) == 10 :
                column_data.append((i[0:3]))
            else :
                column_data.append((i[0:2]))
        Data_TNote.columns = column_data
        result = Data_TNote
        return result        
    else :
        return val

# Date Handle Function
def Select_Date(Or_date, Md_date) :
# Start Date
    Start = Or_date 
    Start_Year = Start[:4]
    Start_Month = Start[4:6]
    Start_Date = Start[6:8] 
    Start_day = str(Start_Year+"-"+Start_Month+"-"+Start_Date)
    Start_day = Start_day[0:12]
    Md_date = Start_day
     
    return Md_date

# Main Call Function
def Main_Call(path, value_1, value_2, st_dt, end_dt) :
    value_1 = value_1
    value_2 = value_2
    # CALL ITEM 1_1
    Result1 = []
    Result1 = Select_Item(path,value_1, Result1)
    # CALL ITEM 2_1
    Result2 = []
    Result2 = Select_Item(path,value_2, Result2)
    # CALL ITEM 1_2
    Result3 = []
    Result3 = Select_Item(path,value_1, Result3)
    # CALL ITEM 2_2
    Result4 = []
    Result4 = Select_Item(path,value_2, Result4)
    # 1. 지정일자
    pick_date1 = st_dt
    pick_date1 = Select_Date(pick_date1  , pick_date1)
    # 2. 비교일자
    pick_date2 = end_dt
    pick_date2 = Select_Date(pick_date2  , pick_date2)

    ## 1
    try : 
            # val1
        Result1 = pd.DataFrame(Result1)
        # # Sorting Index
        Result1 = Result1.set_index('date')
        Result1 = Result1.sort_index(axis=0, ascending= False)
                    
        # val2
        Result2 = pd.DataFrame(Result2)
        # # Sorting Index
        Result2 = Result2.set_index('date')
        Result2 = Result2.sort_index(axis=0, ascending= False)
        # val3
        Result3 = pd.DataFrame(Result3)
        # # Sorting Index
        Result3 = Result3.set_index('date')
        Result3 = Result3.sort_index(axis=0, ascending= False)

        # val4
        Result4 = pd.DataFrame(Result4)
        # # Sorting Index
        Result4 = Result4.set_index('date')
        Result4 = Result4.sort_index(axis=0, ascending= False)

        new_set = pd.DataFrame(Result1.loc[pick_date1])
        # 강제형변환
        new_set = new_set.astype(float)
        new_set.columns = ["{}_{}".format(value_1,pick_date1)]

        new_set2 = pd.DataFrame(Result2.loc[pick_date1])
        new_set2.columns = ["{}_{}".format(value_2,pick_date1)]

        new_set3 = pd.DataFrame(Result3.loc[pick_date2])
        new_set3.columns = ["{}_{}".format(value_1,pick_date2)]
        
        new_set4 = pd.DataFrame(Result4.loc[pick_date2])
        new_set4.columns = ["{}_{}".format(value_2,pick_date2)]

        new_set["{}_{}".format(value_2,pick_date1)] = new_set2.astype(float)
        new_set["{}_{}".format(value_1,pick_date2)] = new_set3.astype(float)
        new_set["{}_{}".format(value_2,pick_date2)] = new_set4.astype(float)
#     # Main dt
        new_set['Spread_{}'.format(pick_date1)] = ((new_set["{}_{}".format(value_1,pick_date1)]- new_set["{}_{}".format(value_2,pick_date1)])) * 100
        new_set['Spread_{}'.format(pick_date2)] = ((new_set["{}_{}".format(value_1,pick_date2)]- new_set["{}_{}".format(value_2,pick_date2)]))* 100 

    except KeyError:
        print("조회 날짜가 없습니다.")
    except UnboundLocalError:
        print("Local Value Type Error.")

    df = pd.DataFrame(new_set)
    # 결측치 전,후 흐름으로 채우기. 
    df = df.interpolate()

    new_index2 = []
    for a in df.index :
        a = str(a)
        if a.find("M") != -1 :
            a = a.replace("M","")
            a = float(a)
            new_index2.append(a)
        elif a.find("Y") != -1 :
            a = a.replace("Y","")
            a = float(a) * 12
            new_index2.append(a)
        else:
            continue    
    # 가장 큰 기울기 구간 구하기.   
    df['Xaxis'] = new_index2
    Spread_1 = df['Spread_{}'.format(pick_date1)].fillna(method='bfill')
    Spread_2 = df['Spread_{}'.format(pick_date2)].fillna(method='bfill')
    
    gradient1 = list(map(lambda i: (round(Spread_1[i+1] - Spread_1[i]) / (new_index2[i+1] - new_index2[i]), i), range(len(new_index2) - 1)))
    gradient2 = list(map(lambda i: (round(Spread_2[i+1] - Spread_2[i]) / (new_index2[i+1] - new_index2[i]), i), range(len(new_index2) - 1)))


    max_gradient, max_index = max(gradient1, key=lambda item: abs(item[0]))
    max_gradient2, max_index2 = max(gradient2, key=lambda item: abs(item[0]))

    print(df)    
    # # # ############################# Using Plotly  ############################# #
    # # # Easy Basic Graph 
    fig = make_subplots(specs=[[{"secondary_y":True}]])

    # # vaule_1 / value_2 표시 / 기준금리
    fig.add_trace(go.Scatter(x=df.Xaxis,y=df["{}_{}".format(value_1,pick_date1)],mode='lines',name="{}_{}".format(value_1,pick_date1)), secondary_y= False) # va1
    fig.add_trace(go.Scatter(x=df.Xaxis,y=df["{}_{}".format(value_2,pick_date1)],mode='lines',name="{}_{}".format(value_2,pick_date1)), secondary_y= False) # va2

    # # # 2중 y축
    fig.add_trace(go.Scatter(x=df.Xaxis,y=df['Spread_{}'.format(pick_date1)],line=dict(color='black', width=4, dash='dash') ,name='Spread_{}'.format(pick_date1)),  secondary_y= True)
    fig.add_trace(go.Scatter(x=df.Xaxis,y=df['Spread_{}'.format(pick_date2)],line=dict(color='gold', width=4, dash='dash') ,name='Spread_{}'.format(pick_date2)),  secondary_y= True)
    # #     # Title Naming
    fig.update_layout(hovermode = 'x unified' , title_text = "{} - {} Spread Yield Curve".format(value_1,value_2),title_font_size=30)

    # #     # x,y,y2 Axis Naming
    fig.update_yaxes(title_text="<b> Rate </b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b> Spread Bp </b> yaxis title", secondary_y=True)

    # #     # grid express
    fig.update_xaxes(showgrid=True, minor_showgrid=True)
    fig.update_yaxes(showgrid=True, minor_showgrid=True)
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10)
    # # X축 간격 및 포맷 조정
    fig.update_xaxes(
        tickvals =  df.Xaxis,
        dtick=24,            # X축 간격 (])
        showgrid=True,      # 주요 그리드 표시
        minor_showgrid=True # 세부 그리드 표시
    )
    # #     # Hover express
    fig.update_traces(hovertemplate= '해당만기: %{x}Month <br>'+
                                     ' 수치 :%{y}%')

    fig.add_vrect(x0=df.Xaxis[max_index], x1=df.Xaxis[max_index+1], line_width=0, fillcolor="green", opacity=0.2,
              annotation_text="{} Spread 최대 기울기".format(pick_date1), 
              annotation_position="bottom right",
              annotation_font_size=20,
              annotation_font_color="green",
              annotation_font_family="Times New Roman")
    ####### result #######
    # 표 출력

    # Pick date 1기울기 
    for grad, idx in gradient1:
        print(f"구간 ({new_index2[idx]}M, {round(Spread_1[idx],2)}) -> ({new_index2[idx+1]}M, {round(Spread_1[idx+1],2)}): (절대값)기울기 {round(abs(grad),2)}")
    print("{} Spread 최대 기울기 : {}  // 스프레드 폭이 큰 구간 : {}Y ~ {}Y ({}M-{}M)".format(pick_date1, round(max_gradient,2),round(df.Xaxis[max_index]/12,2),round(df.Xaxis[max_index+1]/12,2), df.Xaxis[max_index], df.Xaxis[max_index+1]))
    
    # Pick date 2기울기 
    for grad, idx in gradient2:
        print(f"구간 ({new_index2[idx]}M, {round(Spread_2[idx],2)}) -> ({new_index2[idx+1]}M, {round(Spread_2[idx+1],2)}): (절대값)기울기 {round(abs(grad),2)}")
    print("{} Spread 최대 기울기 : {}  // 스프레드 폭이 큰 구간 : {}Y ~ {}Y ({}M-{}M)".format(pick_date2, round(max_gradient2,2),round(df.Xaxis[max_index2]/12,2),round(df.Xaxis[max_index2+1]/12,2),df.Xaxis[max_index2],df.Xaxis[max_index2+1]))

    # 그래프출력 
    fig.show()
    ####### result #######

# ############################## MAKE GUI # ############################## 
# Basic Frame 
root =Tk()

root.title("2개 종목Spreed Yield Curve Chart")
root.geometry("700x400")
root.resizable(True,True)

# 파일찾기
def press() :
    root.file = filedialog.askopenfile(
                initialdir = f'{os.getcwd()}',
                title = '파일 선택창' ,
                filetypes = (('csv files','*.csv'),('all files','*.*')))
                # csv를 우선으로 선택, 모든 확장자도 가능하긴하게 함.
    L2.configure(text ="""파일명 '""" + root.file.name )
    # # 확인
    L2.grid(row=3, column=1, columnspan= 5)
    B2.grid(row=4, column=3)
    
# 확인 후 버튼 생성
def press2() :
    #Cal_Swap_rate(window.file.name)
    df = pd.read_csv(root.file.name,encoding='cp949')
    # Get rid of NA (결측치 제거)
    df= df.dropna()
    data_column = df.columns

    # # column -> list 변환 
    data_column.to_list()
    data_column = data_column[2:]
    result_col = []
    L3 = tk.Label(root,text=' 종목 리스트 ')
    L3.grid( row=5, column=1, columnspan=2 )
    L3_1 = tk.Label(root,text=' 선택 가능 날짜')
    L3_1.grid( row=5, column=4, columnspan=2 )
    # create single select list box
    lb = Listbox(root, selectmode="browse",height= 4) 
    lb.grid(row=6,column=1,columnspan=2)
    list_column = Make_Listbox_column(data_column,result_col)
    a = 0 # 2부터 종목임.
    for i in list_column :
        lb.insert(a, i)
        a += 1
        if a == len(list_column) :
            lb.insert(END, i)
            break
    # 일자 List 
    Data_test = df.iloc[0:,0:1]
    Data_test = pd.DataFrame(Data_test)
    # create single select list box
    lb2 = Listbox(root, selectmode="browse",height= 4) 
    lb2.grid(row=6,column=4,columnspan=2 )
    date_result = []
    for i in range(0,len(Data_test),1) :
        date_result = Data_test['일자'].str.replace("-","")
    date_result = date_result.sort_values(ascending=False)

    b = 0 # 2부터 종목임.
    for i in date_result :
        lb2.insert(b, i)
        b += 1
        if b == len(date_result) :
            lb2.insert(END, i)
            break
    # add 종목1
    def selectItem() :
        selection = lb.curselection()
        if(len(selection) == 0) :
            print(selection)
            return
        value = lb.get(selection[0])
        print(value)
        ent1.insert(0,value)

    def selectItem2() :
        selection = lb.curselection()
        if(len(selection) == 0) :
            print(selection)
            return
        value = lb.get(selection[0])
        print(value)
        ent2.insert(0,value)   

    def selectItem3() :
        selection = lb2.curselection()
        if(len(selection) == 0) :
            print(selection)
            return
        value = lb2.get(selection[0])
        print(value)
        ent3.insert(0,value)   

    def selectItem4() :
        selection = lb2.curselection()
        if(len(selection) == 0) :
            print(selection)
            return
        value = lb2.get(selection[0])
        print(value)
        ent4.insert(0,value)                       
        
    btn1 = tk.Button(root, text='종목1 ▼',command=selectItem)
    btn2 = tk.Button(root, text='종목2 ▼',command=selectItem2)
    btn3 = tk.Button(root, text='기준일자 ▼',command=selectItem3)
    btn4 = tk.Button(root, text='비교일자▼',command=selectItem4)

    btn1.grid(row=7, column=1)
    btn2.grid(row=7, column=2)
    btn3.grid(row=7, column=4)
    btn4.grid(row=7, column=5)
    ent1.grid(row=8, column=1,columnspan=1)
    ent2.grid(row=8, column=2,columnspan=1)
    ent3.grid(row=8, column=4,columnspan=1)
    ent4.grid(row=8, column=5,columnspan=1)
    
    B4.grid(row=10, column=3)

# 종료
def press3() :
    root.destroy()
    sys.exit()

# 그래프 그리기
def press5() :
    Main_Call(root.file.name,ent1.get(), ent2.get(),ent3.get(),ent4.get())
    # 1회성으로 만들 경우 주석제거
    #root.destroy()
    #sys.exit()

L1 = tk.Label(root,text='파일(.csv)를 업로드하세요.\n\n 종료를 원한다면 종료를 누르십시오.',font=10)
L1.grid(row=1,column=1,columnspan=5)

L2 = tk.Label(root, text=' ', font=12, height=3)

B1 = tk.Button(root, text='Upload',font=10,command=press)
B1.grid(row=2,column=1,columnspan=2)

B3 = tk.Button(root, text='종료', font=10 , command=press3)
B3.grid(row=2, column=5, columnspan=2)

B2 = tk.Button(root, text='확인', font=10 , command=press2)
B4 = tk.Button(root, text='그래프 출력', font=10 , command=press5)

ent1 = Entry(root)
ent2 = Entry(root)
ent3 = Entry(root)
ent4 = Entry(root)

root.mainloop() 

