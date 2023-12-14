# import os
# from openai import OpenAI

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def get_gpt_response(question):
#     # ./.env 파일에서 OPENAI_API_KEY 불러오기
#     response = client.completions.create(model="text-davinci-003", prompt=question, max_tokens=150)
#     return response.choices[0].text.strip()


# 코랩 버전
import openai

openai.api_key = "your_api_key"


def get_gpt_response(question):
    # GPT-3 모델을 사용하여 질문에 대한 응답을 생성합니다.
    response = openai.Completion.create(
        model="text-davinci-003", prompt=question, max_tokens=150
    )
    return response.choices[0].text.strip()
