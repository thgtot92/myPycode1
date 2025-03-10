import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
#import tensorflow as tftensorflow
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import SimpleRNN, Dense, Dropout

# 파일 다시 로드
file_path = "./data_matrix_rate_infomax_ver01.xlsx"
xls = pd.ExcelFile(file_path)

# KTB 시트 데이터 로드
ktb_df = xls.parse('KTB')

# 필요한 열 선택 (날짜 및 3년 이하 금리)
ktb_df_filtered = ktb_df.iloc[2:, [0, 10]]  # 날짜와 '3년이하(당일)' 금리 선택

# 컬럼명 변경
ktb_df_filtered.columns = ['Date', '3Y_Bond_Rate']

# 날짜 변환
ktb_df_filtered['Date'] = pd.to_datetime(ktb_df_filtered['Date'])

# 금리 데이터 숫자로 변환
ktb_df_filtered['3Y_Bond_Rate'] = pd.to_numeric(ktb_df_filtered['3Y_Bond_Rate'], errors='coerce')

# 날짜 기준 정렬 (최신 데이터가 가장 마지막에 위치하도록)
ktb_df_filtered = ktb_df_filtered.sort_values(by='Date', ascending=True)

# ADX 계산 함수 정의
def compute_adx(data, window=14):
    """ADX (Average Directional Index) 계산"""
    high_diff = data.diff().clip(lower=0)
    low_diff = -data.diff().clip(upper=0)

    tr = np.maximum(high_diff, low_diff)
    atr = tr.rolling(window=window).mean()

    plus_di = (high_diff / atr).rolling(window=window).mean() * 100
    minus_di = (low_diff / atr).rolling(window=window).mean() * 100

    dx = (np.abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=window).mean()

    return adx

# CCI 계산 함수 정의
def compute_cci(data, window=14):
    """CCI (Commodity Channel Index) 계산"""
    typical_price = data
    mean_tp = typical_price.rolling(window=window).mean()
    mean_dev = (typical_price - mean_tp).abs().rolling(window=window).mean()

    cci = (typical_price - mean_tp) / (0.015 * mean_dev)
    return cci

# ADX & CCI 계산 (14일 기준)
ktb_df_filtered['ADX_14'] = compute_adx(ktb_df_filtered['3Y_Bond_Rate'], window=14)
ktb_df_filtered['CCI_14'] = compute_cci(ktb_df_filtered['3Y_Bond_Rate'], window=14)

# 최신 데이터 준비 (NaN 제거)
df_model = ktb_df_filtered[['3Y_Bond_Rate', 'ADX_14', 'CCI_14']].dropna()

# 다음날 금리(Target) 생성
df_model['Next_Day_Rate'] = df_model['3Y_Bond_Rate'].shift(-1)

# 결측치 제거
df_model = df_model.dropna()

# 데이터 정규화
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df_model[['3Y_Bond_Rate', 'ADX_14', 'CCI_14', 'Next_Day_Rate']])

# 시계열 데이터 생성 함수
def create_sequences(data, seq_length=10):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length, :-1])  # Feature columns
        y.append(data[i+seq_length, -1])     # Target column
    return np.array(X), np.array(y)

# 시계열 데이터 준비
seq_length = 10
X, y = create_sequences(scaled_data, seq_length)

# 데이터 분할 (80% 학습, 20% 테스트)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

# RNN 모델 생성
model = Sequential([
    SimpleRNN(50, activation='relu', return_sequences=True, input_shape=(seq_length, X.shape[2])),
    Dropout(0.2),
    SimpleRNN(50, activation='relu', return_sequences=False),
    Dropout(0.2),
    Dense(1)
])

# 모델 컴파일
model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 학습
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test), verbose=1)

# 최신 데이터를 기반으로 2월 18~20일 예측
latest_data = scaled_data[-seq_length:, :-1]  # 최근 seq_length 만큼 데이터 사용
predictions = {}
current_date = pd.to_datetime("2025-02-17")

for i in range(3):
    next_date = current_date + pd.Timedelta(days=i+1)
    latest_data_reshaped = latest_data.reshape(1, seq_length, X.shape[2])
    pred_scaled = model.predict(latest_data_reshaped)[0, 0]
    pred_rate = scaler.inverse_transform([[0, 0, 0, pred_scaled]])[0, -1]  # 역변환하여 실제 금리로 변환
    predictions[next_date.strftime("%Y-%m-%d")] = pred_rate
    
    # 최신 데이터 업데이트 (예측값 추가)
    latest_data = np.append(latest_data[1:], [[0, 0, 0, pred_scaled]], axis=0)

# 예측 결과 반환
predictions
