from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyodbc

# 데이터베이스 연결 설정
server = "127.0.0.1"
username = "sa"
password = "Hotelchat44"
# database = "your_database_name"  # 본인의 데이터베이스 이름으로 변경

cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
    + server
    + ";DATABASE="
    # + database
    + ";UID="
    + username
    + ";PWD="
    + password
)
cursor = cnxn.cursor()

# HOTEL_ID 조회
cursor.execute("SELECT HOTEL_ID FROM HOTEL")
hotel_ids = cursor.fetchall()

# Chrome 옵션 설정
options = Options()
options.add_argument("--incognito")

# WebDriver 서비스
service = Service(ChromeDriverManager().install())

# WebDriver 인스턴스 생성
driver = webdriver.Chrome(service=service, options=options)

for hotel_id in hotel_ids:
    hotel_id = hotel_id[0]  # 첫 번째 열이 HOTEL_ID
    url = f"https://www.yanolja.com/hotel/{hotel_id}"

    driver.get(url)
    time.sleep(5)  # 웹페이지 로드 대기

    # 호텔 정보 추출
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

    # 호텔 추가 정보 추출
    driver.find_element(
        By.CSS_SELECTOR,
        "#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(5) > div > div > div.css-14fkj0f > div > button",
    ).click()
    time.sleep(3)  # 추가 정보 로드 대기
    hotel_infomation = driver.find_element(
        By.CSS_SELECTOR, "#BOTTOM_SHEET > div.css-gqqlqe > div.css-1ulzvpi > div"
    ).text

    # 데이터베이스에 저장
    sql = """
    MERGE INTO HOTEL AS target
    USING (VALUES (?, ?, ?, ?, ?, ?)) AS source (HOTEL_ID, NAME, LOCATION, RATING, MAINREVIEW, INFOMATION)
    ON target.HOTEL_ID = source.HOTEL_ID
    WHEN MATCHED THEN
        UPDATE SET
            NAME = source.NAME,
            LOCATION = source.LOCATION,
            RATING = source.RATING,
            MAINREVIEW = source.MAINREVIEW,
            INFOMATION = source.INFOMATION
    WHEN NOT MATCHED THEN
        INSERT (HOTEL_ID, NAME, LOCATION, RATING, MAINREVIEW, INFOMATION)
        VALUES (source.HOTEL_ID, source.NAME, source.LOCATION, source.RATING, source.MAINREVIEW, source.INFOMATION);
    """
    cursor.execute(
        sql,
        hotel_id,
        hotel_name,
        hotel_location,
        hotel_rating,
        hotel_mainreview,
        hotel_infomation,
    )
    cnxn.commit()

# 드라이버 및 데이터베이스 연결 종료
driver.quit()
cursor.close()
cnxn.close()
