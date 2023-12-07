from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pyodbc

# 데이터베이스 연결 설정
server = "127.0.0.1"
username = "sa"
password = "Hotelchat44"

cnxn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
    + server
    + ";UID="
    + username
    + ";PWD="
    + password
)
cursor = cnxn.cursor()

# Chrome 드라이버 초기화 및 웹 페이지 열기
driver = webdriver.Chrome()
driver.get("https://www.yanolja.com/hotel/r-900582?advert=AREA&topAdvertiseMore=0")

# 페이지 끝까지 스크롤 다운
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # 페이지 로드를 기다리는 시간 증가
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 호텔 ID 추출 및 데이터베이스에 저장
hotel_ids = []
for i in range(1, 8):  # 7개 파트 반복
    section_selector = f"#__next > div.StyleComponent_container__1jS9A.list_listContainer__2kL99.list_bottomPadding__xvWzu > section.PlaceListBody_placeListBodyContainer__1u70R > div:nth-child({i})"
    hotel_links = driver.find_elements(
        By.CSS_SELECTOR, f"{section_selector} > div > div > a"
    )
    for link in hotel_links:
        href = link.get_attribute("href")
        if href:
            hotel_id = href.split("/")[-1]
            hotel_ids.append(hotel_id)

hotel_ids = list(set(hotel_ids))  # 중복 제거

# 드라이버 종료
driver.quit()

# 결과 출력 및 데이터베이스에 저장
for hotel_id in hotel_ids:
    # 해당 HOTEL_ID가 존재하는지 확인
    cursor.execute("SELECT COUNT(*) FROM HOTEL WHERE HOTEL_ID = ?", hotel_id)
    if cursor.fetchone()[0] == 0:
        # 존재하지 않으면 새로운 행 삽입
        cursor.execute("INSERT INTO HOTEL (HOTEL_ID) VALUES (?)", hotel_id)
        cnxn.commit()

cursor.close()
cnxn.close()

print("Total Hotels:", len(hotel_ids))
