import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re

# get url
driver = webdriver.Chrome()
driver.get('https://travel.yandex.ru/avia/')
wait = WebDriverWait(driver, 20)

# choose departure/arrival
clean_button = driver.find_element(By.CSS_SELECTOR, "button[type='button']")
clean_button.click()
time.sleep(2)

departure = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
departure.send_keys('РЩН')
time.sleep(4)

arrival = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[3]/label/div/div[2]/input')
arrival.send_keys('NUX')
time.sleep(4)

# choose date
date1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[4]/label[1]/div[1]')
date1.click()

today = datetime.now().strftime('%Y-%m-%d')

choosedate = driver.find_element(By.CSS_SELECTOR, f'div[data-qa="calendar-day-{today}"]')
choosedate.click()

search = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
search.click()

# try to change date via formatting link
base_url = driver.current_url
start_date = datetime.now()
end_date = start_date + timedelta(days=2)
current_date = start_date

all_flights_data = []

while current_date <= end_date:
    wait = WebDriverWait(driver, 20)
    wait.until_not(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[5]/div/div[3]")))
    time.sleep(10)

    # Прокрутка страницы
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Извлечение информации
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="EhCXF _274Q5 _4ZiVK"]')))
    flights = driver.find_elements(By.CSS_SELECTOR, 'div[class="EhCXF k1OFp"]')

    flights_data = []

    for flight in flights:
        airlines = flight.find_element(By.CSS_SELECTOR, 'span[class="Eqn7e b9-76"]').text
        airline = [airline.strip() for airline in airlines.split(' • ')]
        departure_time = flight.find_element(By.CSS_SELECTOR, 'span[class="tKp9d XFySC b9-76"]').text
        arrival_time = flight.find_element(By.CSS_SELECTOR, 'span[class="XFySC b9-76"]').text
        price = flight.find_element(By.CSS_SELECTOR, 'button[class="WvMZr Bnnv4 -ZlQV dsupm Uvwrs ACjs5 OSwqi"]').text

        # Очистка цены (убираем пробелы и знак рубля, оставляем только число)
        price_cleaned = re.sub(r'[^\d]', '', price)

        # Фильтрация рейсов
        if "Ямал" in airline:
            if len(airline) == 1:
                flights_data.append({
                    "Дата": current_date.strftime('%d.%m.%Y'),
                    "Время вылета": departure_time,
                    "Время прилета": arrival_time,
                    "Цена": price_cleaned,
                    "Авиакомпания": ", ".join(airline)
                })
        else:
            flights_data.append({
                "Дата": current_date.strftime('%d.%m.%Y'),
                "Время вылета": departure_time,
                "Время прилета": arrival_time,
                "Цена": price_cleaned,
                "Авиакомпания": ", ".join(airline)
            })

    for flight in flights_data:
        print(f"Дата: {flight['Дата']}, Авиакомпания: {flight['Авиакомпания']}, Время вылета: {flight['Время вылета']}, Время прилета: {flight['Время прилета']}, Цена: {flight['Цена']}")

    all_flights_data.extend(flights_data)

    #переход на след страницу
    current_date += timedelta(days=1)
    date_str = current_date.strftime('%Y-%m-%d')
    new_url = base_url[0:-10] + date_str
    driver.get(new_url)

# Сохранение в CSV формат
    csv_file = 'flights_data.csv'
    with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Дата", "Авиакомпания", "Время вылета", "Время прилета", "Цена"])
        writer.writeheader()
        writer.writerows(all_flights_data)
