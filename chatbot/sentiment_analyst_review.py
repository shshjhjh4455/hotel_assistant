from transformers import BertForSequenceClassification, AdamW
from kobert_tokenizer import KoBERTTokenizer
import pandas as pd
import sqlalchemy
import torch
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pyodbc
from tqdm import tqdm

# CSV 파일에서 데이터 로드
reviews_df = pd.read_csv("crawling/data/reivew_table.csv")


# 점수 기준으로 레이블 결정
def label_sentiment(row):
    return 1 if row["RATING"] >= 4 else 0


# 점수 기준으로 레이블 결정
def label_sentiment(row):
    return 1 if row["RATING"] >= 4 else 0


# 새로운 'Sentiment' 열 추가
reviews_df["Sentiment"] = reviews_df.apply(label_sentiment, axis=1)

# sentiment_analysis_dataset으로 사용할 데이터셋
sentiment_analysis_dataset = reviews_df[["COMMENT", "Sentiment"]]

# 토크나이저 로드
tokenizer = KoBERTTokenizer.from_pretrained("skt/kobert-base-v1")


# 데이터셋 클래스 정의
class SentimentDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.len = len(dataframe)
        self.data = dataframe
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __getitem__(self, index):
        text = self.data.iloc[index]["COMMENT"]
        sentiment = self.data.iloc[index]["Sentiment"]
        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
        )
        return {
            "input_ids": torch.tensor(inputs["input_ids"], dtype=torch.long),
            "attention_mask": torch.tensor(inputs["attention_mask"], dtype=torch.long),
            "labels": torch.tensor(sentiment, dtype=torch.long),
        }

    def __len__(self):
        return self.len


# 학습/테스트 데이터셋으로 분리
train_dataset, test_dataset = train_test_split(
    sentiment_analysis_dataset, test_size=0.1
)
train_dataset = SentimentDataset(train_dataset, tokenizer, max_len=128)
test_dataset = SentimentDataset(test_dataset, tokenizer, max_len=128)

# 데이터 로더 생성
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=True)

# 모델 로드
model = BertForSequenceClassification.from_pretrained(
    "skt/kobert-base-v1", num_labels=2
)

# 학습을 위한 설정
optimizer = AdamW(model.parameters(), lr=5e-6)
criterion = torch.nn.CrossEntropyLoss()

# GPU 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Fine-tuning 학습
model.train()
for epoch in range(3):  # 에포크 수는 필요에 따라 조정
    loop = tqdm(train_loader, leave=True)
    for batch in loop:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch {epoch+1}/{3}, Loss: {loss.item()}")

# 평가
model.eval()
predictions, true_labels = [], []
loop = tqdm(test_loader, leave=True)
for batch in loop:
    batch = {k: v.to(device) for k, v in batch.items()}
    with torch.no_grad():
        outputs = model(**batch)

    logits = outputs.logits
    predictions.extend(torch.argmax(logits, dim=-1).tolist())
    true_labels.extend(batch["labels"].tolist())

# 성능 지표 계산
accuracy = accuracy_score(true_labels, predictions)
precision, recall, f1, _ = precision_recall_fscore_support(
    true_labels, predictions, average="binary"
)
print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1: {f1}")

# 모델 저장
torch.save(model.state_dict(), "kobert_finetuned.bin")
