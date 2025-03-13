import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np


# 📌 1️⃣ 정량 데이터 로드 (재무제표)
financial_data_path = "CJ_CGV_Financial_Data.csv"
df_financial = pd.read_csv(financial_data_path)

# 📌 2️⃣ 정량 데이터 전처리
# 📌 2️⃣ 데이터 타입 변환 (문자열 → 숫자)
df_financial = df_financial.drop(columns=["항목"], errors="ignore")  # 필요 없는 문자 컬럼 제거
df_financial = df_financial.replace(",", "", regex=True)  # 숫자 형식에서 콤마 제거
df_financial = df_financial.apply(pd.to_numeric, errors="coerce")  # 숫자로 변환 (문자 → NaN)
df_financial = df_financial.fillna(0)  # 결측값 처리
df_financial = df_financial.astype(np.float32)  # float32 변환

X_numeric = torch.tensor(df_financial.values, dtype=torch.float32)

# 📌 3️⃣ 정성 데이터 로드 (신용평가 보고서, 주석)
filtered_text_path = "CJ_CGV_Filtered_Text.txt"
with open(filtered_text_path, "r", encoding="utf-8") as file:
    qualitative_text = file.read()

# 📌 4️⃣ BERT 기반 정성 데이터 임베딩 (간소화된 TF-IDF 방식 대체)
text_embedding_size = 128  # 가상의 벡터 크기 설정
X_text = torch.randn((X_numeric.shape[0], text_embedding_size))  # 랜덤 벡터 생성

# 📌 5️⃣ MMNN 모델 정의
class MultimodalNN(nn.Module):
    def __init__(self, numeric_input_dim, text_embedding_dim, hidden_dim, output_dim):
        super(MultimodalNN, self).__init__()

        # 정량 데이터 처리 MLP
        self.fc_numeric = nn.Sequential(
            nn.Linear(numeric_input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # 정성 데이터 처리 (BERT 임베딩 대체)
        self.fc_text = nn.Sequential(
            nn.Linear(text_embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # 결합 및 최종 예측층
        self.fc_fusion = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, numeric_data, text_data):
        numeric_features = self.fc_numeric(numeric_data)
        text_features = self.fc_text(text_data)
        fused_features = torch.cat((numeric_features, text_features), dim=1)
        output = self.fc_fusion(fused_features)
        return output

# 📌 6️⃣ 모델 초기화
numeric_input_dim = X_numeric.shape[1]
text_embedding_dim = X_text.shape[1]
hidden_dim = 64
output_dim = 2  # 0: 정상, 1: 부실징후

model_mmnn = MultimodalNN(numeric_input_dim, text_embedding_dim, hidden_dim, output_dim)

# 📌 7️⃣ 모델 학습 설정
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model_mmnn.parameters(), lr=0.001)

# 📌 8️⃣ 더미 라벨 데이터 생성 (부실 여부: 0 또는 1)
y_train = torch.randint(0, 2, (X_numeric.shape[0],))  # 임시 라벨 데이터

# 📌 9️⃣ 모델 학습
epochs = 50
for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model_mmnn(X_numeric, X_text)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

# 📌 🔟 2025년 데이터 예측
latest_numeric = X_numeric[-1].unsqueeze(0)
latest_text = X_text[-1].unsqueeze(0)
with torch.no_grad():
    prediction_mmnn = model_mmnn(latest_numeric, latest_text).argmax().item()

print(f"2025년 CJ CGV 부실 예측 결과: {prediction_mmnn}")  # 1이면 부실징후, 0이면 정상
