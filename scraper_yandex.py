import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.common.exceptions import StaleElementReferenceException
import re
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
import os

# Загружаем маршруты
routes = pd.read_csv('routes.csv').values
airport_codes = {
    "РЩН": "s9600384",
    "НУР": "s9623560",
    "ДМД": "s9600216",
    "УФА": "c172",
    "МРВ": "c11063",
    "СОЧ": "c239"
}

# Инициализируем веб-драйвер
driver = webdriver.Chrome()
driver.get('https://travel.yandex.ru/avia/')
wait = WebDriverWait(driver, 90)

# Основной цикл по направлениям
for n, route in enumerate(routes):
    departure_code, arrival_code = route  # Разбираем пару направлений
    departure_id = airport_codes.get(departure_code, departure_code)  # Преобразуем в ID аэропорта
    arrival_id = airport_codes.get(arrival_code, arrival_code)

    start_date = datetime.now()
    end_date = start_date + timedelta(days=90)
    current_date = start_date

    # Переход на страницу поиска с первым направлением
    base_url = "https://travel.yandex.ru/avia/search/result/?adult_seats=1&children_seats=0&infant_seats=0&klass=economy&oneway=1"

    def update_url(from_id, to_id, date):
        query_params = {
            "fromId": from_id,
            "toId": to_id,
            "when": date
        }
        return base_url + "&" + urlencode(query_params)

    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        new_url = update_url(departure_id, arrival_id, date_str)

        print(f"Переход по ссылке: {new_url}")  # Для отладки

        driver.get(new_url)  # Переход по сформированной ссылке

        # Подождем загрузки страницы
        wait.until_not(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[5]/div/div[3]")))

        # Прокрутка страницы
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Извлечение информации
        flights = driver.find_elements(By.CSS_SELECTOR, 'div[class="EhCXF k1OFp"]')

        flights_data = []
        processed_flights = 0
        for flight in flights:
            try:
                airlines = flight.find_element(By.CSS_SELECTOR, 'span[class="Eqn7e b9-76"]').text
                airline = [airline.strip() for airline in airlines.split(' • ')]

                # Проверка на наличие более одной авиакомпании и авиакомпании "Ямал"
                if len(airline) > 1 and "Ямал" in airline:
                    continue  # Пропускаем этот рейс

                departure_time = flight.find_element(By.CSS_SELECTOR, 'span[class="tKp9d XFySC b9-76"]').text
                max_retries = 3  # Количество попыток при возникновении ошибки
                arrival_time = "Ошибка"  # Значение по умолчанию, если не удастся получить данные

                for attempt in range(max_retries):
                    try:
                        arrival_time = WebDriverWait(flight, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[class="XFySC b9-76"]'))
                        ).text
                        break  # Если всё прошло успешно, выходим из цикла
                    except StaleElementReferenceException:
                        print(f"Попытка {attempt + 1}/{max_retries}: элемент устарел, пробуем снова...")
                        time.sleep(1)  # Ждём перед повторной попыткой
                    except Exception as e:
                        print(f"Ошибка при получении данных о прилёте: {e}")
                        break  # Прерываем попытки, но продолжаем работу скрипта

                price = flight.find_element(By.CSS_SELECTOR, 'button[class="WvMZr Bnnv4 -ZlQV dsupm Uvwrs ACjs5 OSwqi"]').text
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
                processed_flights += 1

            except Exception as e:
                print(f"Ошибка при обработке рейса: {e}")

        print(f"Дата {current_date.strftime('%d.%m.%Y')}: обработано рейсов - {processed_flights}")

        if flights_data:
            min_price_flight = min(flights_data, key=lambda x: int(x["Минимальная цена"]))  # Находим рейс с минимальной ценой

            # Собираем все авиакомпании за день (убираем дубли, приводим к единому формату)
            all_airlines = sorted(
                set(airline.strip() for flight in flights_data for airline in flight["Авиакомпания"].split(", ")))

            # Обновляем данные перед записью
            min_price_flight["Авиакомпания"] = ", ".join(all_airlines)

            # Проверяем, существует ли файл, чтобы добавить заголовки только в начале
            file_exists = os.path.exists('flights_data_yandex.csv')

            # Запись в CSV
            with open('flights_data_yandex.csv', mode='a', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Дата", "Откуда", "Куда", "Авиакомпания", "Время вылета",
                                                          "Время прилета", "Минимальная цена"])
                if not file_exists:  # Если файл только создается, записываем заголовки
                    writer.writeheader()

                writer.writerow(min_price_flight)  # Записываем только один рейс с минимальной ценой

        # Переход на следующую дату
        current_date += timedelta(days=1)

# Закрываем драйвер после завершения
driver.quit()
#