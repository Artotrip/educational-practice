import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
import os

# Загружаем маршруты
routes = pd.read_csv('routes.csv').values

# Инициализируем веб-драйвер
driver = webdriver.Chrome()
driver.get('https://travel.yandex.ru/avia/')
wait = WebDriverWait(driver, 40)

# Основной цикл по направлениям
for n, route in enumerate(routes):
    departure_code, arrival_code = route  # Разбираем пару направлений

    # Очистка и ввод данных в поля
    clean_button = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Очистить поле']")
    clean_button[0].click()

    departure = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[0]
    departure.send_keys(departure_code)
    time.sleep(3)

    arrival = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[1]
    arrival.send_keys(arrival_code)
    clean_button = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Очистить поле']")
    clean_button[1].click()
    arrival.send_keys(arrival_code)
    time.sleep(3)

    # Выбираем дату
    data1 = driver.find_elements(By.CLASS_NAME, 'INYOI')
    driver.execute_script("arguments[0].click();", data1[2])
    time.sleep(2)

    today = datetime.now().strftime('%Y-%m-%d')
    choosedate = driver.find_element(By.CSS_SELECTOR, f'div[data-qa="calendar-day-{today}"]')
    choosedate.click()

    search = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    search.click()
    time.sleep(5)

    # Формируем даты для поиска
    base_url = driver.current_url
    # Удаляем все, что идет после #
    parsed_url = urlsplit(base_url)
    cleaned_url = urlunsplit(parsed_url._replace(fragment=""))
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    current_date = start_date

    while current_date <= end_date:
        wait.until_not(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[5]/div/div[3]")))


        # Прокрутка страницы
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Извлечение информации
        #wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="EhCXF k1OFp"]')))
        flights = driver.find_elements(By.CSS_SELECTOR, 'div[class="EhCXF k1OFp"]')

        flights_data = []
        for flight in flights:
            airlines = flight.find_element(By.CSS_SELECTOR, 'span[class="Eqn7e b9-76"]').text
            airline = [airline.strip() for airline in airlines.split(' • ')]
            departure_time = flight.find_element(By.CSS_SELECTOR, 'span[class="tKp9d XFySC b9-76"]').text
            arrival_time = flight.find_element(By.CSS_SELECTOR, 'span[class="XFySC b9-76"]').text
            price = flight.find_element(By.CSS_SELECTOR,'button[class="WvMZr Bnnv4 -ZlQV dsupm Uvwrs ACjs5 OSwqi"]').text

            price_cleaned = re.sub(r'[^\d]', '', price)

            flights_data.append({
                "Дата": current_date.strftime('%d.%m.%Y'),
                "Время вылета": departure_time,
                "Время прилета": arrival_time,
                "Минимальная цена": price_cleaned,
                "Авиакомпания": ", ".join(airline),
                "Откуда": departure_code,
                "Куда": arrival_code
            })

        if flights_data:
            min_price_flight = min(flights_data, key=lambda x: int(x["Минимальная цена"]))  # Находим рейс с минимальной ценой

            # Собираем все авиакомпании за день (убираем дубли, приводим к единому формату)
            all_airlines = sorted(
                set(airline.strip() for flight in flights_data for airline in flight["Авиакомпания"].split(", ")))

            # Обновляем данные перед записью
            min_price_flight["Авиакомпания"] = ", ".join(all_airlines)

            # Проверяем, существует ли файл, чтобы добавить заголовки только в начале
            file_exists = os.path.exists('flights_data3.csv')

            csv_file = 'flights_data3.csv'

            # Запись в CSV
            with open('flights_data3.csv', mode='a', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Дата", "Откуда", "Куда", "Авиакомпания", "Время вылета",
                                                          "Время прилета", "Минимальная цена"])
                if not file_exists:  # Если файл только создается, записываем заголовки
                    writer.writeheader()

                writer.writerow(min_price_flight)  # Записываем только один рейс с минимальной ценой


        # Переход на следующую дату
        current_date += timedelta(days=1)


        def update_url_date(url, new_date):
            parsed_url = urlsplit(url)
            query_params = parse_qs(parsed_url.query)

            # Обновляем параметр даты
            query_params["when"] = [new_date]

            # Собираем URL обратно
            new_query = urlencode(query_params, doseq=True)
            new_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, parsed_url.path, new_query, ""))
            return new_url


        # Создаём новую дату
        date_str = current_date.strftime('%Y-%m-%d')
        new_url = update_url_date(base_url, date_str)

        driver.get(new_url)

# Закрываем драйвер после завершения
driver.quit()
