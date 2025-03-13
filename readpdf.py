import fitz  # PyMuPDF
import pandas as pd

# 📌 홈플러스 감사보고서 PDF 파일 경로 (파일 경로에 맞게 수정)
pdf_path = "홈플러스_감사보고서_2024.05.31.pdf"

# PDF 파일 열기
doc = fitz.open(pdf_path)

# 📌 특정 키워드를 기반으로 필요한 재무 데이터 추출
financial_data = []
target_keywords = ["자산", "부채", "자본", "매출액", "영업이익", "당기순이익", "EBITDA", "이자보상배율"]

# PDF 페이지 순회하며 데이터 추출
for page in doc:
    text = page.get_text("text")
    lines = text.split("\n")
    
    for line in lines:
        for keyword in target_keywords:
            if keyword in line:
                financial_data.append(line)

# 📌 추출된 데이터를 정리하여 DataFrame 생성
df = pd.DataFrame(financial_data, columns=["재무제표 데이터"])

# 📌 데이터 확인
print(df)

# 📌 데이터 CSV 저장 (선택 사항)
df.to_csv("홈플러스_재무제표_추출.csv", index=False)
