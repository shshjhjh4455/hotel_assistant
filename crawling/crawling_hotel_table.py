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
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_hotel_page(hotel_id, server, username, password):
    print(f"Processing hotel ID: {hotel_id}")  # 로그: 호텔 처리 시작
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    try:
        url = f"https://www.yanolja.com/hotel/{hotel_id}/?checkInDate=2023-12-15&checkOutDate=2023-12-16&adultPax=2"
        driver.get(url)
        time.sleep(5)
        # 부라우저 맨 아래로 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 호텔 정보 추출
        hotel_name, hotel_location, hotel_rating = extract_hotel_info(driver)

        # 객실 정보 추출
        room_info = extract_room_info(driver, hotel_id)

        # 데이터베이스에 저장
        save_hotel_data(
            hotel_id,
            hotel_name,
            hotel_location,
            hotel_rating,
            room_info,
            server,
            username,
            password,
        )
        print(f"Data saved for hotel ID: {hotel_id}")  # 로그: 데이터 저장 완료

    except Exception as e:
        print(f"Error processing hotel ID {hotel_id}: {e}")
    finally:
        driver.quit()


def extract_hotel_info(driver):
    # 호텔 이름, 위치, 평점 추출
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
    return hotel_name, hotel_location, hotel_rating


def extract_room_info(driver, hotel_id):
    # 페이지에서 모든 객실 컨테이너를 찾음
    room_containers = driver.find_elements(
        By.CSS_SELECTOR,
        "#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div",
    )

    room_info = []
    for index in range(1, len(room_containers) + 1):
        try:
            # 각 객실 컨테이너에 대한 CSS 선택자를 동적으로 생성
            type_selector = f"#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child({index}) > div > section.css-1tykgzp > div.css-dhr6qk > div.css-deizzc"
            price_selector = f"#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(1) > div > section.css-1qwzivr > div"
            link_selector = f"#__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child({index}) > div > section.css-1qwzivr > div > a"
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(1) > div > section.css-1tykgzp > div.css-ryy6up > section > div:nth-child(1) > div > div > div > div > span > img
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(1) > div > section.css-1tykgzp > div.css-ryy6up > section > div:nth-child(1) > div
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(1) > div > section.css-1tykgzp > div.css-ryy6up
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(1) > div > section.css-1tykgzp > div.css-ryy6up
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(1) > div > section.css-1tykgzp > div.css-ryy6up > section > div:nth-child(1) > div > div > div > div > span > img
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(2) > div > section.css-1tykgzp > div.css-ryy6up > section > div:nth-child(1) > div > div > div.swiper-slide.swiper-slide-visible > div > span > img
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(3) > div > section.css-1tykgzp > div.css-ryy6up > section > div:nth-child(1) > div > div > div.swiper-slide.swiper-slide-visible.swiper-slide-active > div > span > img
                            #__next > div > div > main > article > div.css-c45a2y > div > section > div:nth-child(1) > div > div.css-1z06rwl > div:nth-child(3) > div > section.css-1tykgzp > div.css-ryy6up > section > div:nth-child(1) > div > div > div.swiper-slide.swiper-slide-visible.swiper-slide-active > div > span > img

            # 명시적 대기를 사용하여 요소가 로드될 때까지 기다림
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, type_selector))
            )
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))
            )
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, link_selector))
            )

            # 해당 선택자로부터 정보 추출
            type_element = driver.find_element(By.CSS_SELECTOR, type_selector)
            price_element = driver.find_element(By.CSS_SELECTOR, price_selector)
            link_element = driver.find_element(By.CSS_SELECTOR, link_selector)

            type = type_element.text
            price = int(re.sub(r"[^\d]", "", price_element.text))
            link = link_element.get_attribute("href")

            room_info.append((hotel_id, type, price, link))
        except TimeoutException:
            print(
                f"Timed out waiting for room elements for hotel ID {hotel_id}, Room Index {index}"
            )
            continue
        except Exception as e:
            print(
                f"Error extracting room info for hotel ID {hotel_id}, Room Index {index}: {e}"
            )
            continue

    return room_info


def save_hotel_data(
    hotel_id,
    hotel_name,
    hotel_location,
    hotel_rating,
    room_info,
    server,
    username,
    password,
):
    cnxn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    cursor = cnxn.cursor()
    # 호텔 데이터 저장
    sql_hotel = """
    MERGE INTO HOTEL AS target
    USING (VALUES (?, ?, ?, ?)) AS source (HOTEL_ID, NAME, LOCATION, RATING)
    ON target.HOTEL_ID = source.HOTEL_ID
    WHEN MATCHED THEN
        UPDATE SET
            NAME = source.NAME,
            LOCATION = source.LOCATION,
            RATING = source.RATING
    WHEN NOT MATCHED THEN
        INSERT (HOTEL_ID, NAME, LOCATION, RATING)
        VALUES (source.HOTEL_ID, source.NAME, source.LOCATION, source.RATING);
    """
    cursor.execute(sql_hotel, hotel_id, hotel_name, hotel_location, hotel_rating)
    cnxn.commit()

    # 객실 데이터 저장
    sql_room = """
    INSERT INTO ROOM (HOTEL_ID, TYPE, PRICE, RESERVATION_LINK)
    VALUES (?, ?, ?, ?);
    """
    for room in room_info:
        cursor.execute(sql_room, room)
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

    # ThreadPoolExecutor를 사용하여 병렬 처리 구현
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_hotel = {
            executor.submit(
                process_hotel_page, hotel_id, server, username, password
            ): hotel_id
            for hotel_id in hotel_ids
        }

        for future in as_completed(future_to_hotel):
            hotel_id = future_to_hotel[future]
            try:
                future.result()
            except Exception as exc:
                print(f"{hotel_id} generated an exception: {exc}")


if __name__ == "__main__":
    main()
