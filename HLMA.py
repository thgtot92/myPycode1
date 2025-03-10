import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


# 파일 경로
file_path = "./data_matrix_rate_infomax_ver01.xlsx"

# 엑셀 파일 읽기
xls = pd.ExcelFile(file_path)

# 모든 시트 이름 확인
xls.sheet_names
# 필요한 열 선택 (KTB 날짜 및 3년 이하 금리)
ktb_df = xls.parse('KTB')
ktb_df_filtered = ktb_df.iloc[2:, [0, 10]]  # 날짜와 '3년이하(당일)' 금리 선택

# 컬럼명 변경
ktb_df_filtered.columns = ['Date', '3Y_Bond_Rate']

# 날짜 변환
ktb_df_filtered['Date'] = pd.to_datetime(ktb_df_filtered['Date'])

# 금리 데이터 숫자로 변환
ktb_df_filtered['3Y_Bond_Rate'] = pd.to_numeric(ktb_df_filtered['3Y_Bond_Rate'], errors='coerce')

# 고저 평균 이동 계산 (단순 10일 이동평균 사용)
ktb_df_filtered['HLMA_10'] = ktb_df_filtered['3Y_Bond_Rate'].rolling(window=10).mean()


# 데이터 준비: 필요 컬럼 선택
df = ktb_df_filtered[['3Y_Bond_Rate', 'HLMA_10']].dropna()

# 다음날 수익률(Target) 생성
df['Next_Day_Return'] = df['3Y_Bond_Rate'].pct_change(1).shift(-1) * 100

# 결측치 제거
df = df.dropna()

# 독립 변수(X)와 종속 변수(y) 설정
X = df[['3Y_Bond_Rate', 'HLMA_10']]
y = df['Next_Day_Return']

# 데이터 분할 (80% 학습, 20% 테스트)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 랜덤 포레스트 회귀 모델 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 모델 평가 (테스트 데이터 MAE 계산)
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

# 가장 최근 데이터로 다음날 수익률 예측
latest_data = X.iloc[-1:].values.reshape(1, -1)
predicted_return = model.predict(latest_data)[0]

print("MAE : {},    Pre_return{}".format(mae, predicted_return))
