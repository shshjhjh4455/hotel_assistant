import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pyodbc
import re


def process_hotel_page(hotel_id):
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        url = f"https://www.yanolja.com/hotel/{hotel_id}"
        driver.get(url)
        time.sleep(1)

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
        print(f"Completed processing hotel ID: {hotel_id}")

        return hotel_id, hotel_name, hotel_location, hotel_rating, review_count

    except Exception as e:
        print(f"Error processing hotel ID {hotel_id}: {e}")
        return hotel_id, None, None, None, None
    finally:
        driver.quit()


def update_database(hotel_data):
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

    for hotel_id, hotel_name, hotel_location, hotel_rating, review_count in hotel_data:
        if hotel_name:  # Only update if data is valid
            cursor.execute(
                sql, hotel_id, hotel_name, hotel_location, hotel_rating, review_count
            )
    print("Database update completed.")  # 데이터베이스 업데이트 완료

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

    hotel_data = []
    print("Starting hotel data processing...")  # 크롤링 시작
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_hotel = {
            executor.submit(process_hotel_page, hotel_id): hotel_id
            for hotel_id in hotel_ids
        }
        for future in concurrent.futures.as_completed(future_to_hotel):
            result = future.result()
            hotel_data.append(result)
    print("All hotel data processing completed.")  # 크롤링 완료
    update_database(hotel_data)


if __name__ == "__main__":
    main()
