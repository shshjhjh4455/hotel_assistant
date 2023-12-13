import os
import openai


def get_gpt_response(question):
    # ./.env 파일에서 OPENAI_API_KEY 불러오기
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-003", prompt=question, max_tokens=150
    )
    return response.choices[0].text.strip()
