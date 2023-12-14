from sentence_transformers import SentenceTransformer
import pyodbc
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 데이터베이스 연결 설정
server = "127.0.0.1"
username = "sa"
password = "Hotelchat44"

cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
    + server
    + ";UID="
    + username
    + ";PWD="
    + password
)

# SBERT 모델 로드
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# 데이터 로드
hotels_df = pd.read_sql("SELECT * FROM HOTEL", cnxn)
reviews_df = pd.read_sql("SELECT * FROM REVIEW", cnxn)

# 리뷰 임베딩 생성
review_embeddings = model.encode(
    reviews_df["COMMENT"].to_list(), show_progress_bar=True
)

# 호텔 별 평균 리뷰 임베딩 계산
hotel_avg_embeddings = {}
for hotel_id in hotels_df["HOTEL_ID"]:
    hotel_reviews = review_embeddings[reviews_df["HOTEL_ID"] == hotel_id]
    hotel_avg_embeddings[hotel_id] = np.mean(hotel_reviews, axis=0)

# 사용자의 질문 임베딩
question_embedding = model.encode("깨끗한 호텔에 가고 싶어")

# 유사도 계산 및 호텔 추천
hotel_ids = list(hotel_avg_embeddings.keys())
hotel_embeddings = list(hotel_avg_embeddings.values())
similarities = cosine_similarity([question_embedding], hotel_embeddings).flatten()
recommended_hotel_id = hotel_ids[np.argmax(similarities)]

# 추천된 호텔 정보
recommended_hotel = hotels_df[hotels_df["HOTEL_ID"] == recommended_hotel_id]

# 데이터베이스 연결 종료
cnxn.close()

# 결과 출력
print(f"추천 호텔: {recommended_hotel}")
