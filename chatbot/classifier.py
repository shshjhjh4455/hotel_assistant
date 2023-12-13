def classify_question(question):
    """
    사용자의 질문을 분석하여 호텔 추천과 관련된 질문인지 판별합니다.

    Parameters:
    question (str): 사용자의 질문

    Returns:
    bool: 질문이 호텔 추천과 관련되었는지 여부
    """
    # 호텔 추천과 관련된 키워드 목록
    hotel_related_keywords = ["호텔", "숙박", "예약", "숙소", "투숙", "룸", "객실"]

    # 질문 내에서 키워드가 있는지 확인
    return any(keyword in question for keyword in hotel_related_keywords)


if __name__ == "__main__":
    # 테스트 코드
    test_questions = [
        "서울에 좋은 호텔 추천해줄래?",
        "내일 날씨 어때?",
        "부산 근처에 가족과 함께 갈만한 숙소 있을까?",
        "오늘 저녁 메뉴 추천해줘",
    ]

    for question in test_questions:
        result = classify_question(question)
        print(f"질문: {question}\n -> 호텔 추천 관련 질문: {result}\n")

