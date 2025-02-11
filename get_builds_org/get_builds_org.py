import json
import time
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class AddressParser:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = self.init_browser()

        self.current_address = None
        self.building_id = None

    def init_browser(self):
        """ Инициализация Selenium WebDriver """
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        if self.headless:
            options.add_argument("--headless")

        # Включаем логирование сетевых запросов
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()

        return driver

    def intercept_network(self):
        pass

    def search_address(self, address):
        """ Выполняет поиск адреса на 2GIS """
        self.current_address = address
        self.building_id = None
        driver = self.driver
        driver.get("https://2gis.ru/irkutsk")

        try:
            # Ожидание загрузки поля ввода
            input_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input._h7eic2")))
            input_box.clear()
            input_box.send_keys(address)
            time.sleep(2)  # Ожидание загрузки подсказок

            # Клик по первой подсказке
            suggestion = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li._1914vup")))
            suggestion.click()
            time.sleep(3)  # Ожидание загрузки страницы дома

            # Перехватываем сетевые запросы и извлекаем данные
            self.intercept_network_requests()

        except Exception as e:
            print(f"Ошибка обработки адреса {address}: {e}")

    def run(self):
        """ Читает адреса из файла и обрабатывает их """
        try:
            address = "улица Ленина, 15"
            if address.strip():
                print(f"\n🔍 Обрабатываем: {address}")
                self.search_address(address)
                time.sleep(2)  # Пауза между запросами

        except Exception as e:
            print(f"❌ Ошибка с адресом {e}")

        finally:
            self.driver.quit()  # Закрываем браузер


if __name__ == "__main__":
    parser = AddressParser(headless=False)
    parser.run()