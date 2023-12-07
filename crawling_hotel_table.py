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


def extract_element_text(driver, css_selector):
    """요소의 텍스트를 추출하거나 빈 문자열을 반환합니다."""
    try:
        return driver.find_element(By.CSS_SELECTOR, css_selector).text
    except:
        return ""


for hotel_id in hotel_ids:
    hotel_id = hotel_id[0]  # 첫 번째 열이 HOTEL_ID
    url = f"https://www.yanolja.com/hotel/{hotel_id}"

    driver.get(url)
    time.sleep(1)  # 웹페이지 로드 대기

    # 호텔 정보 추출 (예외 처리 추가)
    hotel_name = extract_element_text(
        driver,
        "#__next > div > div > main > article > div.css-1cc3d9 > div.css-6pnu6y > div.css-11vo59c > div.css-1g3ik0v",
    )
    hotel_location = extract_element_text(
        driver,
        "#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(2) > section > div > div > div.css-cxbger > div.address.css-18ufud2 > span",
    )
    hotel_rating = extract_element_text(
        driver,
        "#__next > div > div > main > article > div.css-1cc3d9 > div.css-6pnu6y > div.css-14lo8yk > div.css-ubovjv > span.css-1decpwd",
    )
    hotel_mainreview_xpath = "/html/body/div/div/div/main/article/div[1]/div[1]/div[5]/div[3]/div/div/div[1]/div/div/div"
    try:
        hotel_mainreview = driver.find_element(By.XPATH, hotel_mainreview_xpath).text
    except:
        hotel_mainreview = ""  # XPath를 찾을 수 없는 경우 빈 문자열 사용

    # 호텔 추가 정보 추출 (예외 처리 추가)
    try:
        driver.find_element(
            By.CSS_SELECTOR,
            "#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(5) > div > div > div.css-14fkj0f > div > button",
        ).click()
        time.sleep(1)  # 추가 정보 로드 대기
        hotel_infomation = extract_element_text(
            driver, "#BOTTOM_SHEET > div.css-gqqlqe > div.css-1ulzvpi > div"
        )
    except:
        hotel_infomation = ""

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
