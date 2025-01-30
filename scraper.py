import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime, timedelta
#get url
driver = webdriver.Chrome()
driver.get('https://travel.yandex.ru/avia/')

#choose departure/arrival

clean_button = driver.find_element(By.CSS_SELECTOR, "button[type='button']")
clean_button.click()
time.sleep(2)
departure = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
departure.send_keys('РЩН')
time.sleep(2)
arrival = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[5]/div/div/div[2]/form/div[3]/label/div/div[2]/input')
arrival.send_keys('NUX')
time.sleep(2)
#choose date
date1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[5]/div/div/div[2]/form/div[4]/label[1]/div[1]')
date1.click()

today = datetime.now().strftime('%Y-%m-%d')

choosedate = driver.find_element(By.CSS_SELECTOR, f'div[data-qa="calendar-day-{today}"]')
choosedate.click()
time.sleep(3)

search = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
search.click()

time.sleep(5)


#try to change date via formating link
base_url = driver.current_url
start_date = datetime.now()  
end_date = start_date + timedelta(days=10)  # 3 monts date
current_date = start_date

while current_date <= end_date:
    date_str = current_date.strftime('%Y-%m-%d')
    new_url = base_url[0:-10] + date_str
    driver.get(new_url)
    time.sleep(5)
    current_date += timedelta(days=1)
