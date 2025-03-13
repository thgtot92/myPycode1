import torch
import torch.nn as nn
import torch.optim as optim
from transformers import BertModel, BertTokenizer
import pandas as pd

# 1️⃣ **데이터 전처리 (정량 데이터)**
data_homeplus = {
    "연도": [2020, 2021, 2022, 2023, 2024],
    "부채비율": [859.5, 726.0, 663.9, 944.0, 3211.7],
    "차입금의존도": [69.9, 64.1, 65.1, 67.9, 72.6],
    "영업이익률": [2.2, 1.3, -2.1, -3.9, -2.9],
    "EBITDA_매출액": [10.1, 9.0, 6.0, 4.1, 4.6],
    "EBITDA_이자비용": [1.7, 1.5, 1.0, 0.7, 0.7],
    "총차입금_EBITDA": [10.8, 11.0, 16.5, 22.6, 19.8],
    "순차입금_EBITDA": [10.6, 9.7, 15.8, 22.1, 20.3],
    "부실여부": [0, 0, 1, 1, 1],  # 1: 부실징후, 0: 정상
}

df_homeplus = pd.DataFrame(data_homeplus)

# 2️⃣ 모델 학습을 위한 데이터 분리
X_homeplus = df_homeplus.drop(columns=["연도", "부실여부"])
y_homeplus = df_homeplus["부실여부"]


# 1️⃣ **데이터 전처리 (정량 데이터)**
# 홈플러스의 재무 데이터 (정량적 변수)
X_numeric_hp = torch.tensor(X_homeplus.values, dtype=torch.float32)
y_numeric_hp = torch.tensor(y_homeplus.values, dtype=torch.long)

# 2️⃣ **데이터 전처리 (정성 데이터: BERT 활용)**
tokenizer_hp = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model_hp = BertModel.from_pretrained("bert-base-uncased")

# 샘플 텍스트 데이터 (홈플러스 신용평가 보고서 및 감사보고서 주요 내용)
text_data_hp = [
    "Homeplus has a high debt ratio and continues to struggle with profitability.",
    "Credit rating downgraded due to worsening financial conditions.",
    "Retail industry is facing structural challenges affecting Homeplus revenue.",
    "Significant reliance on store sales and asset liquidation for liquidity.",
    "Debt repayment pressures and declining operational cash flow."
]

# BERT 토큰화 및 임베딩 추출
encoded_texts_hp = tokenizer_hp(text_data_hp, padding=True, truncation=True, return_tensors="pt")
with torch.no_grad():
    text_embeddings_hp = bert_model_hp(**encoded_texts_hp).last_hidden_state[:, 0, :]

# 3️⃣ **멀티모달 신경망 (MMNN) 모델 설계**
class MultimodalNN_HP(nn.Module):
    def __init__(self, numeric_input_dim, text_embedding_dim, hidden_dim, output_dim):
        super(MultimodalNN_HP, self).__init__()

        # 정량 데이터 처리 MLP (재무제표)
        self.fc_numeric = nn.Sequential(
            nn.Linear(numeric_input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # 정성 데이터 (BERT Embedding 활용)
        self.fc_text = nn.Sequential(
            nn.Linear(text_embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # 결합(Fusion) 및 최종 예측
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

# 모델 초기화
numeric_input_dim_hp = X_numeric_hp.shape[1]
text_embedding_dim_hp = text_embeddings_hp.shape[1]
hidden_dim_hp = 64
output_dim_hp = 2  # 부실(1) / 정상(0)

model_mmnn_hp = MultimodalNN_HP(numeric_input_dim_hp, text_embedding_dim_hp, hidden_dim_hp, output_dim_hp)

# 4️⃣ **모델 학습 설정**
criterion_hp = nn.CrossEntropyLoss()
optimizer_hp = optim.Adam(model_mmnn_hp.parameters(), lr=0.001)

# 5️⃣ **학습 데이터 준비**
X_text_tensor_hp = text_embeddings_hp[:len(X_numeric_hp)]  # 문장 임베딩 매칭
y_train_tensor_hp = y_numeric_hp

# 6️⃣ **모델 학습**
epochs_hp = 50
for epoch in range(epochs_hp):
    optimizer_hp.zero_grad()
    outputs_hp = model_mmnn_hp(X_numeric_hp, X_text_tensor_hp)
    loss_hp = criterion_hp(outputs_hp, y_train_tensor_hp)
    loss_hp.backward()
    optimizer_hp.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs_hp}], Loss: {loss_hp.item():.4f}")

# 7️⃣ **최신 데이터 예측 (2024년 기준)**
latest_numeric_hp = X_numeric_hp[-1].unsqueeze(0)
latest_text_hp = text_embeddings_hp[-1].unsqueeze(0)
with torch.no_grad():
    prediction_mmnn_hp = model_mmnn_hp(latest_numeric_hp, latest_text_hp).argmax().item()

print(f"2024년 홈플러스 부실 예측 결과: {prediction_mmnn_hp}")  # 1이면 부실징후, 0이면 정상

