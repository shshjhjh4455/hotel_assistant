# chatbot/classifier.py

from transformers import BertForSequenceClassification, BertConfig
from tokenization_morp import BertTokenizerWithMorp
import torch


class HotelQuestionClassifier:
    def __init__(self):
        self.model_path = "data/"
        self.tokenizer = BertTokenizerWithMorp(vocab_file="data/vocab.korean_morp.list")
        self.config = BertConfig.from_json_file("data/bert_config.json")
        self.model = BertForSequenceClassification(self.config)
        self.model.load_state_dict(
            torch.load("data/pytorch_model.bin", map_location="cpu")
        )

    def classify(self, question):
        inputs = self.tokenizer.encode(
            question, return_tensors="pt", max_length=512, truncation=True
        )
        with torch.no_grad():
            outputs = self.model(inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1)
        return probabilities[0][1].item() > 0.5  # 임계값 설정


# 사용 예시
if __name__ == "__main__":
    classifier = HotelQuestionClassifier()
    question = "서울에 좋은 호텔 추천해줄래?"
    is_hotel_related = classifier.classify(question)
    print(f"호텔 관련 질문: {is_hotel_related}")
