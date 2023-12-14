from transformers import BertForSequenceClassification
from sentence_transformers import SentenceTransformer
import torch
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from kobert_tokenizer import KoBERTTokenizer
from tqdm import tqdm

# 예시 호텔 2개만 사용하여 진행, 추후 로직 업데이트 필요

def recommend_hotel(question):
    # 감성 분석 모델 로드
    model_path = (
        "/content/drive/MyDrive/자연어처리/hotel_assistant/chatbot/data/kobert_finetuned.bin"
    )
    sentiment_model = BertForSequenceClassification.from_pretrained(
        "skt/kobert-base-v1",
        num_labels=2,
        state_dict=torch.load(model_path, map_location=torch.device("cuda")),
    )

    # 호텔 리뷰 데이터 로드
    reviews_df = pd.read_csv(
        "/content/drive/MyDrive/자연어처리/hotel_assistant/crawling/data/reivew_table.csv"
        #change directory
    )

    # 호텔 테이블 로드
    hotels_df = pd.read_csv(
        "/content/drive/MyDrive/자연어처리/hotel_assistant/crawling/data/hotel_table.csv"
        #change directory
    )

    # SBERT 모델 로드
    sbert_model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

    # KoBERT 토크나이저 로드
    tokenizer = KoBERTTokenizer.from_pretrained("skt/kobert-base-v1")

    # 내부 함수: 감성 점수 계산
    def get_sentiment_score(review):
        inputs = tokenizer.encode_plus(
            review,
            add_special_tokens=True,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding="max_length",
        )
        outputs = sentiment_model(**inputs)
        sentiment_score = torch.sigmoid(outputs.logits)[0][1].item()
        return sentiment_score

    # 사용자 질문 임베딩
    question_embedding = sbert_model.encode(question)

    # 호텔별 리뷰 임베딩 및 감성 점수 계산 (선택된 호텔 ID만 사용)
    selected_hotel_ids = [1000100245, 10048715]
    hotel_scores = {}
    for hotel_id in tqdm(selected_hotel_ids, desc="Analyzing selected hotels"):
        hotel_reviews = reviews_df[reviews_df["HOTEL_ID"] == hotel_id]["COMMENT"]
        embeddings = [sbert_model.encode(review) for review in hotel_reviews]
        sentiment_scores = [get_sentiment_score(review) for review in hotel_reviews]

        avg_embedding = np.mean(embeddings, axis=0) 
        avg_sentiment_score = np.mean(sentiment_scores) 
        sim = cosine_similarity([question_embedding], embeddings).flatten()[0] 

        # 유사도와 감성 점수를 개별적으로 곱하여 최종 점수 계산
        combined_scores = [sim * score for score in sentiment_scores]
        result_score = np.mean(combined_scores)
        hotel_scores[hotel_id] = result_score
        print(f"호텔 ID: {hotel_id}, 평균 유사도: {sim}, 평균 감성 점수: {avg_sentiment_score}, 추천 스코어: {result_score}")


    # 최종 호텔 추천
    recommended_hotel_id = max(hotel_scores, key=hotel_scores.get)
    recommended_hotel_name = hotels_df.loc[hotels_df['HOTEL_ID'] == recommended_hotel_id, 'NAME'].iloc[0]

    print(f"\n추천 호텔 ID: {recommended_hotel_id}, 이름: {recommended_hotel_name}")
    return recommended_hotel_name


# main 함수 (테스트용)
if __name__ == "__main__":
    question = "깨끗하고 친절한 호텔을 찾고 있어요"
    best_hotel_id = recommend_hotel(question)
    print(f"\n최종 추천 호텔 ID: {best_hotel_id}")
