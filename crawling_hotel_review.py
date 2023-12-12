import concurrent.futures
import time
import re
import pyodbc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def process_review_page(driver, hotel_id):
    try:
        print(f"Processing reviews for hotel ID: {hotel_id}")
        url = f"https://place-site.yanolja.com/places/{hotel_id}/review"
        driver.get(url)

        # 스크롤 다운하여 모든 리뷰 로드
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # 페이지 로드 대기
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        reviews = []
        index = 1
        print(f"Review found for index {index}")
        while True:
            try:
                rating_selector = f"#__next > div > div > main > div > div:nth-child(4) > div:nth-child(1) > div:nth-child({index}) > div > div > div.css-176xgwq > div:nth-child(1) > div > div.css-ledymh > div"
                comment_selector = f"#__next > div > div > main > div > div:nth-child(4) > div:nth-child(1) > div:nth-child({index}) > div > div > div.css-1v46kci > div > div"

                rating_elements = driver.find_elements(By.CSS_SELECTOR, rating_selector)
                rating = calculate_rating(rating_elements)

                comment_element = driver.find_element(By.CSS_SELECTOR, comment_selector)
                comment = comment_element.text

                reviews.append((hotel_id, rating, comment))

                index += 1
            except NoSuchElementException:
                print(f"No more reviews found at index {index}, moving to next hotel")
                break  # 모든 리뷰 처리 완료
        return reviews
    except Exception as e:
        print(f"Error processing reviews for hotel ID {hotel_id}: {e}")
    print(f"Completed reviews for hotel ID: {hotel_id}")


def calculate_rating(rating_elements):
    star_count = 0
    for star in rating_elements:
        if "fdbd00" in star.get_attribute("innerHTML"):
            star_count += 1
    return star_count


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


def main():
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
    cursor.execute("SELECT HOTEL_ID FROM HOTEL")
    hotel_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    cnxn.close()

    options = Options()
    options.add_argument("--incognito")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for hotel_id in hotel_ids:
            driver = webdriver.Chrome(options=options)  # 각 스레드에 독립적인 드라이버 인스턴스 할당
            future = executor.submit(process_review_page, driver, hotel_id)
            futures.append(future)

        # 작업 결과를 수집하여 데이터베이스에 저장
        for future in concurrent.futures.as_completed(futures):
            reviews = future.result()
            if reviews:
                save_reviews_to_database(reviews, server, username, password)

    print("All review processing tasks completed.")


if __name__ == "__main__":
    main()
