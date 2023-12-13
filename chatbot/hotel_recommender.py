def recommend_hotel(question):
    """
    사용자의 질문에 기반하여 호텔을 추천합니다.

    Parameters:
    question (str): 사용자의 질문

    Returns:
    str: 추천 호텔에 대한 정보
    """
    # 실제 구현에서는 여기에 데이터베이스 쿼리나 추천 알고리즘을 사용할 수 있습니다.
    # 임시 로직: 사용자의 질문에 따라 다른 호텔 추천
    if "서울" in question:
        return "추천 호텔: 서울 파크 호텔"
    elif "부산" in question:
        return "추천 호텔: 부산 마린 호텔"
    elif "제주" in question:
        return "추천 호텔: 제주 아일랜드 호텔"
    else:
        return "특정 지역에 대한 추천 호텔을 찾을 수 없습니다. 지역을 명시해주세요."


if __name__ == "__main__":
    # 테스트 코드
    test_questions = [
        "서울에 좋은 호텔 추천해줄래?",
        "부산 근처에 가족과 함께 갈만한 숙소 있을까?",
        "제주도 여행 갈 때 좋은 호텔 추천해줘",
        "강릉에 있는 호텔 알려줘",
    ]

    for question in test_questions:
        recommendation = recommend_hotel(question)
        print(f"질문: {question}\n -> {recommendation}\n")
