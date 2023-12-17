from flask import Flask, request, jsonify, render_template
from hotel_recommender import recommend_hotel
from hotel_question_classifier_gpt_api import is_hotel_related

app = Flask(__name__)


@app.route("/")
def home():
    # 홈페이지를 렌더링하는 라우트
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    question = request.json.get("question")
    if is_hotel_related(question):
        answer = recommend_hotel(question)
    else:
        # 호텔 관련 질문이 아닌 경우, 사용자에게 호텔 관련 질문을 유도하는 메시지 반환
        answer = "호텔에 대해 물어보세요. 예를 들어, '서울에서 좋은 호텔 추천해줘'와 같이 말이죠."
    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(debug=True)
