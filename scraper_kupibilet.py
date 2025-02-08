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

#Начальные настройки
start_date = datetime.now().strftime('%Y-%m-%d')
print(start_date)

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
driver.get(f'https://www.kupibilet.ru/search?adult=1&cabinClass=Y&child=0&childrenAges=[]&filter=%7B%22transportKind%22:%7B%22Airplane%22:true%7D%7D&infant=0&route[0]=iatax:TJM_{start_date}_date_{start_date}_iatax:NUX&v=2')
wait = WebDriverWait(driver, 90)
time.sleep(20)