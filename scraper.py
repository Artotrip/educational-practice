import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta


# get url
driver = webdriver.Chrome()
driver.get('https://travel.yandex.ru/avia/')
wait = WebDriverWait(driver, 20)

# choose departure/arrival
clean_button = driver.find_element(By.CSS_SELECTOR, "button[type='button']")
clean_button.click()
# time.sleep(2)

departure = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
departure.send_keys('РЩН')
#departure_button = driver.find_element(By.XPATH, '//*[@id="suggest-0"]')
#departure_button.click()
time.sleep(2)

arrival = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[3]/label/div/div[2]/input')
arrival.send_keys('NUX')
#arrival_button = driver.find_element(By.XPATH, '//*[@id="suggest-0"]')
#arrival_button.click()
time.sleep(2)

# choose date
date1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[4]/label[1]/div[1]')
date1.click()

today = datetime.now().strftime('%Y-%m-%d')

choosedate = driver.find_element(By.CSS_SELECTOR, f'div[data-qa="calendar-day-{today}"]')
choosedate.click()
# time.sleep(3)

search = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
search.click()


# try to change date via formatting link
base_url = driver.current_url
start_date = datetime.now()  
end_date = start_date + timedelta(days=3)  # 3 months date
current_date = start_date

while current_date <= end_date:

    """
    Добавил пример того, как можно использовать объект WebDriverWait.
    В качестве первого аргумента нужно передавать драйвер. Дальше - время ожидания.
    Опционально можно ещё добавить частоту обновления (в секундах) и игнорирование ошибок.
    
    Пример: WebDriverWait(driver, timeout=20, poll_frequency=2, ignored_exceptions=[NoSuchElementException]
    Ошибку нужно будет заранее импортировать, как и любой другой элемент из библиотеки.
    from selenium.common.exceptions import NoSuchElementException
    
    """

    wait = WebDriverWait(driver, 20)
    wait.until_not(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[5]/div/div[3]")))
    time.sleep(7)

    #wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="EhCXF k1OFp"]')))
    ## прокрутка страницы
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Прокрутка вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Небольшая пауза для подгрузки контента
        time.sleep(2)

        # Проверяем новый размер страницы
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Если высота страницы не изменилась, выходим из цикла
        last_height = new_height

    # извлечение информации
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[class="EhCXF _274Q5 _4ZiVK"]')))
    # нахождение рейсов
    flights = driver.find_elements(By.CSS_SELECTOR, 'div[class="EhCXF k1OFp"]')

    # Пустой список для сохранения данных
    flights_data = []

    # Обрабатываем каждый рейс
    for flight in flights:
        # Находим вложенные элементы (замените селекторы на подходящие)

        airline = flight.find_element(By.CSS_SELECTOR, 'span[class="Eqn7e b9-76"]').text
        departure_time = flight.find_element(By.CSS_SELECTOR, 'span[class="tKp9d XFySC b9-76"]').text
        arrival_time = flight.find_element(By.CSS_SELECTOR, 'span[class="XFySC b9-76"]').text
        price = flight.find_element(By.CSS_SELECTOR, 'button[class="WvMZr Bnnv4 -ZlQV dsupm Uvwrs ACjs5 OSwqi"]').text

        # Сохраняем данные в виде словаря
        flights_data.append({
            "airline": airline,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "price": price
        })

    # Выводим или обрабатываем собранные данные
    for flight in flights_data:
        print(
            f"Авиакомпания: {flight['airline']}, Время вылета: {flight['departure_time']}, Время прилета: {flight['arrival_time']}, Цена: {flight['price']}")

    #смена даты
    date_str = current_date.strftime('%Y-%m-%d')
    new_url = base_url[0:-10] + date_str
    driver.get(new_url)

    # time.sleep(5)
    current_date += timedelta(days=1)
