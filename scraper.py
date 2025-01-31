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
time.sleep(2)

departure = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
departure.send_keys('РЩН')
departure_button = driver.find_element(By.XPATH, '//*[@id="suggest-0"]')
departure_button.click()
# time.sleep(2)

arrival = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[3]/label/div/div[2]/input')
arrival.send_keys('NUX')
arrival_button = driver.find_element(By.XPATH, '//*[@id="suggest-0"]')
arrival_button.click()

# choose date
date1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[4]/label[1]/div[1]')
date1.click()

today = datetime.now().strftime('%Y-%m-%d')

choosedate = driver.find_element(By.CSS_SELECTOR, f'div[data-qa="calendar-day-{today}"]')
choosedate.click()
# time.sleep(3)

search = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
search.click()

# time.sleep(5)


# try to change date via formatting link
base_url = driver.current_url
start_date = datetime.now()  
end_date = start_date + timedelta(days=10)  # 3 months date
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
    time.sleep(3)

    date_str = current_date.strftime('%Y-%m-%d')
    new_url = base_url[0:-10] + date_str
    driver.get(new_url)

    # time.sleep(5)
    current_date += timedelta(days=1)
