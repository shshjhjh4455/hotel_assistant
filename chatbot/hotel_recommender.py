from transformers import BertForSequenceClassification, BertTokenizer
from sentence_transformers import SentenceTransformer
import torch
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm
from kobert_tokenizer import KoBERTTokenizer

# 감성 분석 모델 로드
model_path = "chatbot/data/kobert_finetuned.bin"
sentiment_model = BertForSequenceClassification.from_pretrained(
    "skt/kobert-base-v1",
    num_labels=2,
    state_dict=torch.load(model_path, map_location=torch.device("cpu")),
)


# 호텔 리뷰 데이터 로드 및 처리 (CSV 파일 또는 데이터베이스에서 로드)
reviews_df = pd.read_csv("crawling/data/reivew_table.csv")

# SBERT 모델 로드
sbert_model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")


# KoBERT 토크나이저 로드
tokenizer = KoBERTTokenizer.from_pretrained("skt/kobert-base-v1")


def get_sentiment_score(review, sentiment_model, tokenizer):
    inputs = tokenizer.encode_plus(
        review,
        add_special_tokens=True,
        return_tensors="pt",
        max_length=512,
        truncation=True,
        padding="max_length",
    )
    outputs = sentiment_model(**inputs)
    # 긍정 클래스의 점수를 추출
    sentiment_score = torch.sigmoid(outputs.logits)[0][1].item()
    return sentiment_score


def recommend_hotel(question, reviews_df, sentiment_model, sbert_model):
    # 사용자 질문 임베딩
    question_embedding = sbert_model.encode(question)

    # 호텔별 리뷰 임베딩 및 감성 점수 계산
    hotel_scores = {}
    for hotel_id in tqdm(
        reviews_df["HOTEL_ID"].unique(),
        desc="Calculating embeddings and sentiment scores for each hotel",
    ):
        hotel_reviews = reviews_df[reviews_df["HOTEL_ID"] == hotel_id]["COMMENT"]
        embeddings = []
        sentiment_scores = []
        for review in hotel_reviews:
            embedding = sbert_model.encode(review)
            sentiment_score = get_sentiment_score(review, sentiment_model, tokenizer)
            embeddings.append(embedding)
            sentiment_scores.append(sentiment_score)

        avg_embedding = np.mean(embeddings, axis=0)
        avg_sentiment_score = np.mean(sentiment_scores)

        # 유사도 계산
        sim = cosine_similarity([question_embedding], [avg_embedding]).flatten()[0]

        # 유사도와 감성 점수 결합
        hotel_scores[hotel_id] = sim * avg_sentiment_score

    # 최종 호텔 추천
    recommended_hotel_id = max(hotel_scores, key=hotel_scores.get)
    return recommended_hotel_id


# main 함수
if __name__ == "__main__":
    question = "깨끗하고 친절한 호텔을 찾고 있어요"
    recommended_hotel_id = recommend_hotel(
        question, reviews_df, sentiment_model, sbert_model
    )
    print(f"추천 호텔 ID: {recommended_hotel_id}")
