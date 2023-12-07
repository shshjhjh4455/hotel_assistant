from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Chrome 드라이버 초기화 및 웹 페이지 열기
driver = webdriver.Chrome()
driver.get("https://www.yanolja.com/hotel/r-900582?advert=AREA&topAdvertiseMore=0")

# 페이지 끝까지 스크롤 다운
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # 페이지 로드를 기다리는 시간
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 호텔 링크(또는 ID) 추출
hotel_links = driver.find_elements(By.CSS_SELECTOR, "div.css-16z7q6k a")
hotel_ids = [link.get_attribute("href").split("/")[-1] for link in hotel_links]

# 드라이버 종료
driver.quit()

# 결과 출력
print(hotel_ids)
