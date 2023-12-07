from selenium import webdriver
from selenium.webdriver.common.by import By
import time

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
        time.sleep(3)
        break
    last_height = new_height

# 호텔 링크 추출
hotel_ids = []
selectors = [
    "#__next > div.StyleComponent_container__1jS9A.list_listContainer__2kL99.list_bottomPadding__xvWzu > section.PlaceListBody_placeListBodyContainer__1u70R > div > div > a",
    "#__next > div.StyleComponent_container__1jS9A.list_listContainer__2kL99.list_bottomPadding__xvWzu > section.PlaceListBody_placeListBodyContainer__1u70R > div > section > div > div > a",
]

for selector in selectors:
    hotel_links = driver.find_elements(By.CSS_SELECTOR, selector)
    for link in hotel_links:
        href = link.get_attribute("href")
        if href:  # href 속성이 None이 아닌 경우에만 처리
            hotel_id = href.split("/")[-1]
            hotel_ids.append(hotel_id)

hotel_ids = list(set(hotel_ids))  # 중복 제거

# 드라이버 종료
driver.quit()

# 결과 출력
print(hotel_ids)
print("Total Hotels:", len(hotel_ids))
