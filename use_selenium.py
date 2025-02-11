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
    def __init__(self, file_path, headless=False):
        self.file_path = file_path
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

    def intercept_network_requests(self):
        """ Перехватывает сетевые запросы и извлекает building_id """
        try:
            logs = self.driver.get_log("performance")
            for entry in logs:
                log_message = json.loads(entry["message"])["message"]
                if log_message["method"] == "Network.responseReceived":
                    request_id = log_message["params"]["requestId"]
                    response_url = log_message["params"]["response"]["url"]

                    if "suggests" in response_url:
                        self.extract_building_id(request_id)

                    if self.building_id and f"byid={self.building_id}" in response_url:
                        self.extract_building_info(request_id)

                    if self.building_id and "organizations/list" in response_url:
                        self.extract_organizations(request_id)

        except Exception as e:
            print(f"Ошибка перехвата запросов: {e}")

    def extract_building_id(self, request_id):
        """ Извлекает building_id из ответа API """
        try:
            response = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            data = json.loads(response["body"])
            items = data.get("result", {}).get("items", [])

            for item in items:
                if "address" in item and "building_id" in item["address"]:
                    self.building_id = item["address"]["building_id"]
                    print(f"🏠 Найден building_id: {self.building_id}")
                    break

        except Exception as e:
            print(f"Ошибка получения building_id: {e}")

    def extract_building_info(self, request_id):
        """ Извлекает информацию о здании """
        try:
            response = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            data = json.loads(response["body"])
            items = data.get("result", {}).get("items", [])

            if items:
                print("🏢 Информация о здании:")
                print(items[0])
                # print(self.extract_data(items[0]))

        except Exception as e:
            print(f"Ошибка получения информации о здании: {e}")

    def extract_organizations(self, request_id):
        """ Извлекает список организаций, находящихся в здании """
        try:
            response = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            data = json.loads(response["body"])
            organizations = data.get("result", {}).get("items", [])

            if organizations:
                print("📌 Найденные организации в здании:")
                for org in organizations:
                    print(f"📍 Название: {org.get('name', 'Неизвестно')}")
                    print(f"🕒 Расписание: {org.get('schedule', 'Не указано')}")
                    print("-" * 30)

        except Exception as e:
            print(f"Ошибка получения списка организаций: {e}")

    def search_address(self, address):
        """ Выполняет поиск адреса на 2GIS """
        self.current_address = address
        self.building_id = None
        driver = self.driver
        driver.get("https://2gis.ru/irkutsk")

        try:
            # Ожидание загрузки поля ввода
            input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input._h7eic2")))
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
            with open(self.file_path, "r", encoding="utf-8") as file:
                addresses = file.read().splitlines()

            for address in addresses:
                if address.strip():
                    print(f"\n🔍 Обрабатываем: {address}")
                    self.search_address(address)
                    time.sleep(2)  # Пауза между запросами

        except FileNotFoundError:
            print(f"❌ Файл {self.file_path} не найден")

        finally:
            self.driver.quit()  # Закрываем браузер


if __name__ == "__main__":
    file_path = "irkutsk_addresses_sorted.txt"
    parser = AddressParser(file_path=file_path, headless=False)
    parser.run()