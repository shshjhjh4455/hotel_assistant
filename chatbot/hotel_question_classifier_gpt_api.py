import openai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def is_hotel_related(question):
    """
    사용자의 질문이 호텔 추천과 관련되었는지 GPT API를 사용하여 판단합니다.

    Parameters:
    question (str): 사용자의 질문

    Returns:
    int: 질문이 호텔 추천과 관련되었다면 1, 아니라면 0
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"질문: '{question}'\n이 질문의 의도가 호텔과 연관이 있으면 1을 아니면 0으로 답변해줘?",
        max_tokens=50,
    )

    # API 응답에서 '1' 또는 '0'만 추출하여 반환
    return int(response.choices[0].text.strip())


# 함수 호출 예시
question = "배가 고파"
result = is_hotel_related(question)
print(f"호텔 관련 질문: {result}")  # 1 또는 0 출력
