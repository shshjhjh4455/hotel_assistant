from flask import Flask, request, jsonify, render_template
from hotel_recommender import recommend_hotel
from gpt_api import get_gpt_response
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
        answer = get_gpt_response(question)
    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(debug=True)
