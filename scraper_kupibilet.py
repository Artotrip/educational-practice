import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime, timedelta

# Загрузка маршрутов
routes = pd.read_csv('routes.csv').values

airport_codes = {
    "РЩН": "TJM",
    "НУР": "NUX",
    "ДМД": "DME",
    "УФА": "UFA",
    "МРВ": "MRV",
    "СОЧ": "AER"
}

color_to_airline = {
    "#203484": "Аэрофлот",
    "#E31F24": "ЮВТ Аэро",
    "#003594": "Utair",
    "#74c6fa": "Победа",
    "#CE2633": "Red Wings",
    "#2AABE8": "ИрАэро",
    "#cd202c": "Nordwind Airlines",
    "#330072": "Smartavia",
    "#b3d643": "S7 Airlines",
    "#0c4594": "Ямал",
}

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 60)

# Основной цикл по маршрутам.
for route in routes:
    departure_code, arrival_code = route
    departure_id = airport_codes.get(departure_code, departure_code)
    arrival_id = airport_codes.get(arrival_code, arrival_code)

    initial_url = (
        f"https://www.kupibilet.ru/search?adult=1&cabinClass=Y&child=0&childrenAges=[]&filter=%7B%22transportKind%22:%7B%22Airplane%22:true%7D%7D"
        f"&infant=0&route[0]=iatax:{departure_id}_{datetime.now().strftime('%Y-%m-%d')}_date_{datetime.now().strftime('%Y-%m-%d')}_iatax:{arrival_id}&v=2")

    driver.get(initial_url)
    time.sleep(3)

    try:
        sort_by_price_button = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'svg[class="styled__IconSvg-sc-o1jnik-0 kgTPiW"]')))
        sort_by_price_button.click()
        time.sleep(2)

        filter_price = driver.find_elements(By.CSS_SELECTOR, "div[class='styled__ListItem-sc-1ikpqvc-3 etgatP']")
        if len(filter_price) > 2:
            filter_price[2].click()
            time.sleep(2)
    except Exception as e:
        print(f"Ошибка при установке фильтра: {e}")

    for day_offset in range(90):  # 90 дней вперёд
        current_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')

        search_url = (
            f"https://www.kupibilet.ru/search?adult=1&cabinClass=Y&child=0&childrenAges=[]&filter=%7B%22transportKind%22:%7B%22Airplane%22:true%7D%7D"
            f"&infant=0&route[0]=iatax:{departure_id}_{current_date}_date_{current_date}_iatax:{arrival_id}&v=2")

        try:
            driver.get(search_url)
        except Exception as e:
            print(f"Ошибка загрузки страницы: {e}")
            continue

        try:
            flights = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div[data-testid="serp-ticket-item"]')))

            for flight in flights:
                try:
                    airline_logos = flight.find_elements(By.CSS_SELECTOR, 'img[class*="styled__AirlineIcon"]')
                    airline_names = []
                    skip_flight = False

                    for logo in airline_logos:
                        airline_color = logo.get_attribute('color')
                        airline_name = color_to_airline.get(airline_color, "Неизвестная авиакомпания")
                        if airline_name == "Ямал" or airline_name == "Неизвестная авиакомпания":
                            skip_flight = True
                            break
                        airline_names.append(airline_name)

                    if skip_flight or not airline_names:
                        continue

                    departure_time = flight.find_elements(By.CSS_SELECTOR, 'span[class="styled__StyledTypography-sc-1ym9bng-0 hHAquu"]')[0].text
                    arrival_time = flight.find_elements(By.CSS_SELECTOR, 'span[class="styled__StyledTypography-sc-1ym9bng-0 hHAquu"]')[1].text
                    price = flight.find_element(By.CSS_SELECTOR,
                                                'div[class="styled__StyledPrice-sc-1f1e4zh-2 ciWuwV"]').text
                    price_cleaned = int(''.join(filter(str.isdigit, price)))

                    flight_data = {
                        "Дата": (datetime.now() + timedelta(days=day_offset)).strftime('%d.%m.%Y'),
                        "Аэропорт вылета": departure_code,
                        "Аэропорт прилёта": arrival_code,
                        "Время вылета": departure_time,
                        "Время прилета": arrival_time,
                        "Авиакомпания(и)": ", ".join(airline_names),
                        "Минимальная цена билета": price_cleaned,
                    }

                    with open('flights_data_kupibilet.csv', mode='a', encoding='utf-8', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=flight_data.keys())
                        if file.tell() == 0:
                            writer.writeheader()
                        writer.writerow(flight_data)

                    print(f"Рейс добавлен: {flight_data}")
                    break
                except Exception as e:
                    print(f"Ошибка при обработке рейса: {e}")
        except Exception as e:
            print(f"Ошибка при извлечении информации о рейсах: {e}")
            continue

driver.quit()
