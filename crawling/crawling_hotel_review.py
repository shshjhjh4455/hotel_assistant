import concurrent.futures
import time
import re
import pyodbc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor


def process_review_page(driver, hotel_id):
    try:
        print(f"Processing reviews for hotel ID: {hotel_id}")
        url = f"https://place-site.yanolja.com/places/{hotel_id}/review"
        driver.get(url)
        time.sleep(3)
        # 스크롤 다운 로직
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # 페이지 로드 대기
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # 페이지 상단으로 스크롤
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    break
            last_height = new_height

        reviews = []

        # 페이지의 모든 섹션을 반복
        section_index = 1
        while True:
            try:
                # 섹션 내의 리뷰 아이템 반복
                for item_index in range(1, 21):
                    comment_selector = f"#__next > div > div > main > div > div:nth-child(4) > div:nth-child({section_index}) > div:nth-child({item_index}) > div > div > div.css-1v46kci"
                    rating_selector = f"#__next > div > div > main > div > div:nth-child(4) > div:nth-child({section_index}) > div:nth-child({item_index}) > div > div > div.css-176xgwq > div:nth-child(1) > div > div.css-ledymh > div"

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, comment_selector)
                        )
                    )
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, rating_selector)
                        )
                    )

                    comment_element = driver.find_element(
                        By.CSS_SELECTOR, comment_selector
                    )
                    rating_element = driver.find_element(
                        By.CSS_SELECTOR, rating_selector
                    )

                    comment = comment_element.text
                    rating = calculate_rating(rating_element)

                    reviews.append((hotel_id, rating, comment))
                    print(f"Review {item_index} in section {section_index} added")

                section_index += 1

            except TimeoutException:
                print(
                    f"No more reviews to load in section {section_index}, moving to next section"
                )
                break

    except Exception as e:
        print(f"Error processing reviews for hotel ID {hotel_id}: {e}")
    finally:
        driver.quit()
        print(f"Completed reviews for hotel ID: {hotel_id}")

    return reviews


def calculate_rating(rating_element):
    # 별 모양의 HTML을 가져옴
    star_html = rating_element.get_attribute("outerHTML")

    # 각 <path> 태그 내의 'fill="#fdbd00"' 빈도 계산
    filled_stars_count = 0
    for path_tag in star_html.split("<path"):
        if 'fill="#fdbd00"' in path_tag:
            filled_stars_count += 1

    return filled_stars_count


def save_reviews_to_database(reviews, server, username, password):
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    cursor = cnxn.cursor()

    sql = """
    INSERT INTO REVIEW (HOTEL_ID, RATING, COMMENT)
    VALUES (?, ?, ?);
    """
    for review in reviews:
        cursor.execute(sql, review)
    cnxn.commit()
    cursor.close()
    cnxn.close()


from concurrent.futures import ThreadPoolExecutor


def main():
    server = "127.0.0.1"
    username = "sa"
    password = "Hotelchat44"

    # 데이터베이스에서 호텔 ID 목록을 가져옴
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    cursor = cnxn.cursor()
    cursor.execute("SELECT HOTEL_ID FROM HOTEL")
    hotel_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    cnxn.close()

    # 병렬 처리를 위한 ThreadPoolExecutor 설정
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for hotel_id in hotel_ids:
            futures.append(
                executor.submit(process_review, hotel_id, server, username, password)
            )

        # 모든 작업이 완료될 때까지 기다림
        for future in concurrent.futures.as_completed(futures):
            print(future.result())


def process_review(hotel_id, server, username, password):
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    try:
        reviews = process_review_page(driver, hotel_id)
        if reviews:
            save_reviews_to_database(reviews, server, username, password)
        return f"Completed processing for hotel ID: {hotel_id}"
    except Exception as e:
        return f"Error processing hotel ID {hotel_id}: {e}"
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
