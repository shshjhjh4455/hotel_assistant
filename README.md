https://github.com/SKTBrain/KoBERT?tab=readme-ov-file#tokenizer 사용

using in colab notebook

edit path for dataset in hotel_recommender.py

you need to register openai api key in your environment variable

kobert_finetuned.bin dataset is not uploaded

```markdown
# 호텔 추천 챗봇

이 프로젝트는 사용자의 요구에 따라 적합한 호텔을 추천하는 챗봇입니다. 사용자의 질문을 분석하여 호텔 추천에 관련된 질문인 경우, 적합한 호텔을 추천합니다.

## 시작하기

이 지침은 프로젝트를 로컬 컴퓨터에서 실행하기 위한 것으로, 개발 및 테스트 목적으로 사용됩니다.

### 전제 조건

이 프로젝트를 실행하기 위해서는 Python이 설치되어 있어야 합니다. 프로젝트에 필요한 외부 라이브러리는 `requirements.txt`를 통해 설치할 수 있습니다.

### 설치

1. 프로젝트를 클론합니다:
```

git clone https://github.com/shshjhjh4455/hotel_assistant.git

```

2. 필요한 패키지를 설치합니다:

```

pip install -r requirements.txt

```
### 실행

프로젝트를 실행하기 위해 다음 명령어를 사용합니다:

flask run

```

python app.py

```

```

도커 sql 사용방법
docker pull mcr.microsoft.com/azure-sql-edge
docker run -d --name sql_server_demo -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=yourStrong(!)Password' -p 1433:1433 mcr.microsoft.com/azure-sql-edge

brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew upgrade
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18

```



## 사용 방법

프로그램을 실행한 후, 사용자는 챗봇에게 질문을 하여 호텔을 추천받을 수 있습니다. 예를 들어, "깨끗한 호텔을 추천해주세요"와 같은 질문을 할 수 있습니다.

## 기여하기

기여를 원하시는 분들은 ...

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 제공됩니다.

```
