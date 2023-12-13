from transformers import BertModel, BertTokenizer
import torch


class HotelQuestionClassifier:
    def __init__(self):
        self.model_name = "monologg/kobert"
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertModel.from_pretrained(self.model_name)

    def classify(self, question):
        inputs = self.tokenizer(
            question, return_tensors="pt", max_length=512, truncation=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        # 여기에서 출력을 분석하여 질문이 호텔 관련 여부를 판단
        # 예시 코드는 단순히 출력의 첫 번째 요소를 사용
        # 실제 구현에서는 학습된 분류기 레이어 또는 로직이 필요
        return outputs.last_hidden_state[0, 0, :].item() > 0  # 예시 임계값


# 사용 예
classifier = HotelQuestionClassifier()
question = "서울에 좋은 호텔 추천해줄래?"
is_hotel_related = classifier.classify(question)
print(f"호텔 관련 질문: {is_hotel_related}")
