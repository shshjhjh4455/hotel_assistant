import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyodbc


def process_hotel_page(hotel_id, server, username, password):
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    try:
        url = f"https://www.yanolja.com/hotel/{hotel_id}"
        driver.get(url)
        time.sleep(5)

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
        review_count_element = driver.find_element(
            By.CSS_SELECTOR, "span.css-1sg2lsz"
        ).text
        review_count = int(re.sub(r"[^\d]", "", review_count_element))

        # 데이터베이스에 저장
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
        MERGE INTO HOTEL AS target
        USING (VALUES (?, ?, ?, ?, ?)) AS source (HOTEL_ID, NAME, LOCATION, RATING, REVIEW_COUNT)
        ON target.HOTEL_ID = source.HOTEL_ID
        WHEN MATCHED THEN
            UPDATE SET
                NAME = source.NAME,
                LOCATION = source.LOCATION,
                RATING = source.RATING,
                REVIEW_COUNT = source.REVIEW_COUNT
        WHEN NOT MATCHED THEN
            INSERT (HOTEL_ID, NAME, LOCATION, RATING, REVIEW_COUNT)
            VALUES (source.HOTEL_ID, source.NAME, source.LOCATION, source.RATING, source.REVIEW_COUNT);
        """
        cursor.execute(
            sql, hotel_id, hotel_name, hotel_location, hotel_rating, review_count
        )
        cnxn.commit()
        cursor.close()
        cnxn.close()
        print(f"Hotel ID {hotel_id} processed successfully.")  # 호텔 페이지 처리 완료

    except Exception as e:
        print(f"Error processing hotel ID {hotel_id}: {e}")
    finally:
        driver.quit()


def main():
    server = "127.0.0.1"
    username = "sa"
    password = "Hotelchat44"

    # 데이터베이스에서 HOTEL_ID 조회
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

    # 병렬 처리
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_hotel_page, hotel_id, server, username, password)
            for hotel_id in hotel_ids
        ]
        print("Waiting for hotel page processing to complete...")
        for future in concurrent.futures.as_completed(futures):
            future.result()
            print("Hotel page processing complete.")


if __name__ == "__main__":
    main()
