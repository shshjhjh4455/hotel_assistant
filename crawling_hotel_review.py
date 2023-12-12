import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyodbc


def process_review_page(hotel_id, server, username, password):
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    try:
        url = f"https://place-site.yanolja.com/places/{hotel_id}/review"
        driver.get(url)

        # 페이지를 계속 아래로 스크롤하여 리뷰 로드
        last_height = driver.execute_script("return document.body.scrollHeight")
        review_count = 0
        while review_count < 500:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # 페이지 로드 대기
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            review_elements = driver.find_elements(
                By.CSS_SELECTOR, "div.css-1v46kci > div > div"
            )
            review_count = len(review_elements)

        # 리뷰 정보 추출 및 저장
        save_review_data(driver, hotel_id, server, username, password)

    except Exception as e:
        print(f"Error processing review page for hotel ID {hotel_id}: {e}")
    finally:
        driver.quit()


def calculate_rating(rating_element):
    # 모든 별(SVG) 요소를 찾음
    stars = rating_element.find_elements(By.CSS_SELECTOR, "svg.css-189aa3t")
    filled_stars_count = 0

    # 색이 채워진 별의 개수를 세어 평점 계산
    for star in stars:
        if 'fill="#fdbd00"' in star.get_attribute("outerHTML"):
            filled_stars_count += 1

    return filled_stars_count


def save_review_data(driver, hotel_id, server, username, password):
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    cursor = cnxn.cursor()

    # 모든 리뷰 요소를 찾음
    review_blocks = driver.find_elements(
        By.CSS_SELECTOR,
        "#__next > div > div > main > div > div:nth-child(4) > div:nth-child(1) > div",
    )
    review_count = 0

    for review_block in review_blocks:
        if review_count >= 500:  # 최대 500개의 리뷰 처리
            break

        # 별점 추출
        rating_element = review_block.find_element(
            By.CSS_SELECTOR,
            f"__next > div > div > main > div > div:nth-child(4) > div:nth-child(1) > div:nth-child(1~여러개) > div > div > div.css-176xgwq > div:nth-child(1) > div > div.css-ledymh > div" ,
        )
        rating = calculate_rating(rating_element)

        # 코멘트 추출
        comment_element = review_block.find_element(
            By.CSS_SELECTOR, "div > div > div.css-1v46kci > div > div"
        )
        comment = comment_element.text

        # 데이터베이스에 저장
        cursor.execute(
            "INSERT INTO REVIEW (HOTEL_ID, RATING, COMMENT) VALUES (?, ?, ?)",
            hotel_id,
            rating,
            comment,
        )
        review_count += 1

    cnxn.commit()
    cursor.close()
    cnxn.close()


def calculate_rating(rating_element):
    stars = rating_element.find_elements(By.CSS_SELECTOR, "svg.css-189aa3t")
    filled_stars_count = 0

    for star in stars:
        if 'fill="#fdbd00"' in star.get_attribute("outerHTML"):
            filled_stars_count += 1

    return filled_stars_count


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

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_review_page, hotel_id, server, username, password)
            for hotel_id in hotel_ids
        ]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()
