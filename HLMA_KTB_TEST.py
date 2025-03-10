import pandas as pd

# 업로드된 엑셀 파일 불러오기
file_path = "./data_matrix_rate_infomax_ver01.xlsx"
xls = pd.ExcelFile(file_path)

# 시트 이름 확인
xls.sheet_names


# "KTB" 시트 데이터 불러오기
ktb_df = pd.read_excel(xls, sheet_name="KTB")

# 데이터 확인
ktb_df.head()

# 데이터 정리
# 첫 번째 행을 컬럼명으로 설정하고 불필요한 행 제거
ktb_df.columns = ktb_df.iloc[1]
ktb_df = ktb_df.iloc[2:].reset_index(drop=True)

# 날짜 컬럼 변환
ktb_df = ktb_df.rename(columns={"일자": "Date"})
ktb_df["Date"] = pd.to_datetime(ktb_df["Date"])

# 필요한 금리 데이터(1년~10년 이하)만 선택
ktb_rates = ktb_df[["Date", "1년이하(당일)", "1.5년이하(당일)", "2년이하(당일)", "2.5년이하(당일)",
                     "3년이하(당일)", "4년이하(당일)", "5년이하(당일)", "7년이하(당일)", "10년이하(당일)"]].copy()

# 컬럼명 변경
ktb_rates.columns = ["Date", "1Y", "1.5Y", "2Y", "2.5Y", "3Y", "4Y", "5Y", "7Y", "10Y"]

# 숫자로 변환
ktb_rates.iloc[:, 1:] = ktb_rates.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

# 최근 데이터 기준 정렬
ktb_rates = ktb_rates.sort_values(by="Date", ascending=True).reset_index(drop=True)

# 고저평균이동(HLA) 계산 (5일 이동 평균)
hla_window = 5
for col in ktb_rates.columns[1:]:
    ktb_rates[f"HLA_{col}"] = ktb_rates[col].rolling(window=hla_window).mean()

# 결측치 제거
ktb_rates_clean = ktb_rates.dropna().reset_index(drop=True)

print(ktb_rates)
