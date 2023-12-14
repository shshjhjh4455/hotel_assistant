from transformers import BertForSequenceClassification, BertConfig
from sentence_transformers import SentenceTransformer
import torch
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm

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


# 호텔 추천 함수 정의
def recommend_hotel(question, reviews_df, sentiment_model, sbert_model):
    # 사용자 질문 임베딩
    question_embedding = sbert_model.encode(question)

    # 호텔별 리뷰 임베딩 및 감성 점수 계산
    hotel_embeddings = {}
    for hotel_id in tqdm(
        reviews_df["HOTEL_ID"].unique(), desc="Calculating embeddings for each hotel"
    ):
        hotel_reviews = reviews_df[reviews_df["HOTEL_ID"] == hotel_id]["COMMENT"]
        embeddings = [sbert_model.encode(review) for review in hotel_reviews]
        hotel_embeddings[hotel_id] = {"embedding": np.mean(embeddings, axis=0)}

    # 사용자 질문과 리뷰 임베딩 간 유사도 계산
    similarities = {}
    for hotel_id, data in hotel_embeddings.items():
        sim = cosine_similarity([question_embedding], [data["embedding"]]).flatten()[0]
        similarities[hotel_id] = sim

    # 최종 호텔 추천
    recommended_hotel_id = max(similarities, key=similarities.get)
    return recommended_hotel_id


# main 함수
if __name__ == "__main__":
    question = "깨끗하고 친절한 호텔을 찾고 있어요"
    recommended_hotel_id = recommend_hotel(
        question, reviews_df, sentiment_model, sbert_model
    )
    print(f"추천 호텔 ID: {recommended_hotel_id}")
