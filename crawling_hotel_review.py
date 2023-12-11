import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyodbc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def process_hotel_page(hotel_id, server, username, password):
    print(f"Processing hotel ID: {hotel_id}")
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    try:
        url = f"https://place-site.yanolja.com/places/{hotel_id}/review"
        driver.get(url)
        time.sleep(10)  # 페이지 로딩 대기

        review_info = []
        max_reviews = 500
        collected_reviews = 0

        while collected_reviews < max_reviews:
            new_reviews = extract_review_info(
                driver, hotel_id, collected_reviews, max_reviews
            )
            if not new_reviews:
                break  # 추가 리뷰가 없으면 종료

            review_info.extend(new_reviews)
            collected_reviews += len(new_reviews)

            # 스크롤 다운
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # 새로운 콘텐츠 로드 대기

        # 데이터베이스에 저장
        save_review_data(review_info, server, username, password)
        print(f"Data saved for hotel ID: {hotel_id}")

    except Exception as e:
        print(f"Error processing hotel ID {hotel_id}: {e}")
    finally:
        driver.quit()


def extract_review_info(driver, hotel_id, start_index, max_reviews):
    review_containers = driver.find_elements(
        By.CSS_SELECTOR, "#__next > div > div > main > div > div:nth-child(4) > div"
    )

    review_info = []
    for index, review in enumerate(
        review_containers[start_index:], start=start_index + 1
    ):
        if index > max_reviews:
            break  # 최대 리뷰 개수에 도달하면 중단

        try:
            rating_selector = f"#__next > div > div > main > div > div:nth-child(4) > div:nth-child({index}) > div > div > div.css-176xgwq > div:nth-child(1) > div > div.css-ledymh > div"
            comment_selector = f"#__next > div > div > main > div > div:nth-child(4) > div:nth-child({index}) > div > div > div.css-1v46kci > div > div"

            rating_element = driver.find_element(By.CSS_SELECTOR, rating_selector)
            comment_element = driver.find_element(By.CSS_SELECTOR, comment_selector)

            rating = calculate_rating(rating_element)
            comment = comment_element.text

            review_info.append((hotel_id, rating, comment))

        except Exception as e:
            print(
                f"Skipping review at index {index} for hotel ID {hotel_id} due to error: {e}"
            )

    return review_info


def calculate_rating(rating_element):
    stars = rating_element.find_elements(By.CSS_SELECTOR, "svg.css-189aa3t")
    filled_stars_count = 0

    for star in stars:
        if 'fill="#fdbd00"' in star.get_attribute("outerHTML"):
            filled_stars_count += 1

    return filled_stars_count


def save_review_data(review_info, server, username, password):
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    cursor = cnxn.cursor()

    sql_review = """
    INSERT INTO REVIEW (HOTEL_ID, RATING, COMMENT)
    VALUES (?, ?, ?);
    """
    for review in review_info:
        cursor.execute(sql_review, review)
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_hotel_page, hotel_id, server, username, password)
            for hotel_id in hotel_ids
        ]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
