import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from parsers.dadata.suggestion import DadataSuggestion

# Настройка логирования
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "minzhkh_parser.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

class MinzhkhParser:
    def __init__(self, address=None, headless=False):
        self.headless = headless
        self.driver = None
        self.address = address
        self.info = None
        self.token = "80219668a6c5cf96def06462f6e05fd147e0223b"
        self.secret = "3091ba0b3524603295189105effb34c0ba675af3"
        self.dadata = DadataSuggestion(self.token, self.secret)
        self.init_browser()

    def configure_browser_options(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        return options

    def init_browser(self):
        logging.info("Инициализация браузера")
        options = self.configure_browser_options()
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()

    def set_address(self, address):
        self.address = address

    def get_build(self):
        return self.info

    def open_site(self):  # Заменить на актуальный URL МинЖКХ
        url = "https://dom.mingkh.ru/irkutskaya-oblast/irkutsk/"
        logging.info(f"Открытие сайта: {url}")
        self.driver.get(url)
        self.wait_for_page_load(timeout=20)

    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def input_address(self):
        logging.info(f"Ввод адреса: {self.address}")
        input_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "address")))
        input_box.clear()
        input_box.send_keys(self.address)
        input_box.send_keys(Keys.ENTER)
        self.wait_for_page_load()

    def search_address(self): # Поиск адреса в таблице
        self.dadata.set_address(self.address)
        self.dadata.process_address()
        target_street = self.dadata.get_street() # Искомое название улицы
        target_city = self.dadata.get_city() # Искомое название города
        target_value = self.dadata.get_value() # Полное название улицы

        """Проход по таблице и поиск вхождения street в строки столбца Адрес"""
        # Находим все строки в теле таблицы
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')

        # Проходим по каждой строке и достаем адрес (3-я колонка, индекс 2)
        print("Начало цикла прохода по строкам")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 3:
                td_address = cells[2].text.strip()
                if target_street.lower() in td_address.lower():
                    td_city_address = target_city + ', ' + td_address
                    self.dadata.set_address(td_city_address)
                    self.dadata.process_address()
                    value = self.dadata.get_value()
                    print(value)
                    if target_value == value:
                        link = row.find_element(By.TAG_NAME, "a")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(0.5)
                        link.click()
                        break

    def parse_page(self):
        logging.info("Парсинг данных")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        data = {}

        # Пример парсинга
        house_year = soup.find("div", class_="year-built")  # заменить на реальный класс
        uk_name = soup.find("div", class_="management-company")  # заменить на реальный класс

        data["year_built"] = house_year.text.strip() if house_year else "N/A"
        data["management_company"] = uk_name.text.strip() if uk_name else "N/A"

        return data

    def run(self, address):
        try:
            self.set_address(address)
            self.open_site()
            self.input_address()
            time.sleep(3)
            self.search_address()
            time.sleep(10)
            # return self.parse_page()
        except Exception as e:
            logging.error(f"Ошибка при обработке адреса {address}: {e}")
            return {}
        finally:
            self.close()

    def close(self):
        if self.driver:
            self.driver.quit()
            logging.info("Браузер закрыт")

if __name__ == "__main__":
    address = "Иркутск, Ленина, 15"
    parser = MinzhkhParser(headless=False)
    parser.run(address)

