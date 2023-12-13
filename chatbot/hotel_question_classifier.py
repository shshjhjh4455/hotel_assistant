from transformers import BertModel, BertTokenizer
import torch
import torch.nn as nn

class HotelQuestionClassifier:
    def __init__(self):
        self.model_name = 'monologg/kobert'
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.model = BertModel.from_pretrained(self.model_name)
        # 선형 분류 레이어 추가
        self.classifier = nn.Linear(768, 1)

    def classify(self, question):
        inputs = self.tokenizer(question, return_tensors='pt', max_length=512, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            avg_pool = torch.mean(outputs.last_hidden_state, dim=1)
            logits = self.classifier(avg_pool)
            probabilities = torch.sigmoid(logits)
        return probabilities.item() > 0.1  # 임계값 설정

# 사용 예
classifier = HotelQuestionClassifier()
question = "배고파"
is_hotel_related = classifier.classify(question)
print(f"호텔 관련 질문: {is_hotel_related}")
