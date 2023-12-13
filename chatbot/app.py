from flask import Flask, request
from classifier import classify_question
from hotel_recommender import recommend_hotel
from gpt_api import get_gpt_response

app = Flask(__name__)


@app.route("/chatbot", methods=["POST"])
def chat():
    question = request.json.get("question")
    if classify_question(question):
        return recommend_hotel(question)
    else:
        return get_gpt_response(question)


if __name__ == "__main__":
    app.run(debug=True)
