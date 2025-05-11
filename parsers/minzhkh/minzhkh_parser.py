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
        self.dadata = DadataSuggestion()
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

    def get_build(self): # Возвращает полученную информацию о здании
        return self.info

    def open_site(self):  # Открытие сайта
        url = "https://dom.mingkh.ru/irkutskaya-oblast/irkutsk/"
        logging.info(f"Открытие сайта: {url}")
        self.driver.get(url)
        self.wait_for_page_load(timeout=30)

    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def input_address(self): # Ввод адреса в поле поиска
        logging.info(f"Ввод адреса: {self.address}")
        input_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "address")))
        input_box.clear()
        input_box.send_keys(self.address)
        input_box.send_keys(Keys.ENTER)
        self.wait_for_page_load()

    def search_address(self): # Поиск адреса в таблице
        logging.info(f"Поиск адреса из таблицы:")
        rows = WebDriverWait(self.driver, timeout=10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
        #rows = self.driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')

        self.dadata.set_address(self.address)
        self.dadata.process_address()
        target_value = self.dadata.get_value() # Полное название улицы
        target_city = self.dadata.get_city() # Искомое название города
        target_street = self.dadata.get_street() # Искомое название улицы
        target_house = self.dadata.get_house() # Искомый дом

        # Проходим по каждой строке и достаем адрес (3-я колонка, индекс 2)
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 3: # Проверка наличия 3 и более ячеек в таблице
                city_cell = cells[1].text.strip()
                address_cell = cells[2].text.strip()
                if target_city.lower() in city_cell.lower(): # Проверка соответствия города
                    if target_street.lower() in address_cell.lower() and target_house in address_cell: # Проверка вхождения адреса и дома
                        td_city_address = f"{target_city}, {address_cell}"
                        self.dadata.set_address(td_city_address)
                        self.dadata.process_address()
                        value = self.dadata.get_value()
                        if target_value == value: # Сравниваем найденный адрес с целевым
                            try:
                                link = row.find_element(By.TAG_NAME, "a")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                                time.sleep(0.5)
                                link.click()
                                return True
                            except Exception as e:
                                logging.error(f"Ошибка при клике на адрес, {e}")
        return False

    def parse_page(self):
        logging.info("Парсинг данных")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        data = {}

        # Ищем все строки таблиц
        table_rows = soup.select("table.table.table-striped tr")

        for row in table_rows:
            cells = row.find_all("td")
            if len(cells) == 3:
                key = cells[0].get_text(strip=True)
                value = cells[2].get_text(strip=True)
                data[key] = value

        logging.info(f"Извлечённые данные: {data}")
        return data

    def run(self):
        try:
            self.open_site()
            self.input_address()
            if self.search_address():
                self.info = self.parse_page()
        except Exception as e:
            logging.error(f"Ошибка при обработке адреса {address}: {e}")

    def close(self):
        if self.driver:
            self.driver.quit()
            logging.info("Браузер закрыт")

if __name__ == "__main__":
    address = "Иркутск, Ленина, 15"
    parser = MinzhkhParser(headless=False)
    parser.set_address(address)
    parser.run()

