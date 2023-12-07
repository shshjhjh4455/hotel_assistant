from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyodbc


# Chrome 옵션 설정
options = Options()

# 시크릿 모드로 실행
options.add_argument("--incognito")

# 예시 옵션: 헤드리스 모드로 실행 (브라우저 UI 없이 실행)
options.add_argument("--headless")

# WebDriver 서비스
service = Service(ChromeDriverManager().install())

# WebDriver 인스턴스 생성
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.yanolja.com/hotel/1000105156"

driver.get(url)

# 페이지 로드 대기
time.sleep(5)  # 웹페이지가 완전히 로드될 때까지 기다리는 시간 (조정 필요)

# 예: 호텔 이름, 위치 등 추출
hotel_id = url.split("/")[-1]
hotel_name = driver.find_element(
    By.CSS_SELECTOR,
    "#__next > div > div > main > article > div.css-1cc3d9 > div.css-6pnu6y > div.css-11vo59c > div.css-1g3ik0v",
).text
hotel_location = driver.find_element(
    By.CSS_SELECTOR,
    "#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(2) > section > div > div > div.css-cxbger > div.address.css-18ufud2 > span",
).text
hotel_rating = driver.find_element(
    By.CSS_SELECTOR,
    "#__next > div > div > main > article > div.css-1cc3d9 > div.css-6pnu6y > div.css-14lo8yk > div.css-ubovjv > span.css-1decpwd",
).text
hotel_mainreview = driver.find_element(
    By.CSS_SELECTOR,
    "#__next > div > div > main > article > div.css-1cc3d9 > div.css-6pnu6y > div.css-bpv7fg > div.css-x90eyc > div > div.css-1eclj0b > div:nth-child(1) > div > div > div",
).text

driver.find_element(
    By.CSS_SELECTOR,
    "#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(5) > div > div > div.css-14fkj0f > div > button",
).click()
hotel_infomation = driver.find_element(
    By.CSS_SELECTOR,
    "#BOTTOM_SHEET > div.css-gqqlqe > div.css-1ulzvpi > div",
).text


# 데이터베이스 연결 설정
server = "localhost"
username = "sa"
password = "Hotelchat44"
database = "master"
timeout = 30

cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
    + server
    # + ";DATABASE="
    # + database
    + ";UID="
    + username
    + ";PWD="
    + password
    + ";TIMEOUT="
    + str(timeout)
)

cursor = cnxn.cursor()

# SQL 쿼리 작성
sql = """
INSERT INTO HOTEL (HOTEL_ID, NAME, LOCATION, RATING, MAINREVIEW, INFORMATION)
VALUES (?, ?, ?, ?, ?, ?)
"""

# SQL 쿼리 실행
cursor.execute(
    sql,
    hotel_id,
    hotel_name,
    hotel_location,
    hotel_rating,
    hotel_mainreview,
    hotel_infomation,
)

# 변경사항 저장
cnxn.commit()

# 데이터베이스 연결 종료
cursor.close()
cnxn.close()
