import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class AddressParser:
    def __init__(self, file_path, headless=False):
        self.file_path = file_path
        self.headless = headless
        # Общие счетчики
        self.counter = {
            "build": 0,
            "orgs_in_build": 0,
            "parsed_build": 0,
            "parsed_orgs_in_build": 0,
            "saved_build_json": 0,
            "saved_orgs_in_build_json": 0,

            "error_address_processing": 0,
            "error_intercept_network": 0,
            "error_not_found_build_id": 0,
            "many_files_orgs_in_build": 0
        }
        self.driver = self.init_browser()

    def init_browser(self):
        """ Инициализация Selenium WebDriver с DevTools """
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        if self.headless:
            options.add_argument("--headless")

        options.set_capability("goog:loggingPrefs", {"performance": "ALL"}) # Включаем перехват сетевых запросов

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()

        return driver

    def wait_for_page_load(self, timeout=10):
        """Ожидание полной загрузки страницы"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def clear_cache_and_cookies(self):
        """ Очистка кеш и куки """
        try:
            self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})
            self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
            print("🧹 Кэш и куки очищены")

        except Exception as e:
            print(f"⚠ Ошибка при очистке кэша и логов: {e}")

    def intercept_network_requests(self, building_id, have_organizations):
        """ Перехват нужного byid-запроса """
        try:
            time.sleep(3)  # Время для загрузки запросов
            logs = self.driver.get_log("performance")

            target_byid_request = None
            target_byid_request_id = None
            target_orgs_request = None
            target_orgs_request_id = None

            entry_byid = f"byid?id={building_id}"
            # entry_orgs_pattern = re.compile(r"list\?key.*building_id=" + str(building_id))
            entry_orgs = "list?key"

            count_entry_list = 0

            for log in logs:
                log_json = json.loads(log["message"])["message"]

                if log_json["method"] == "Network.responseReceived":
                    request_id = log_json["params"]["requestId"]
                    response_url = log_json["params"]["response"]["url"]

                    if entry_byid in response_url: # Если URL содержит нужный "byid", сохраняем его
                        target_byid_request = response_url
                        target_byid_request_id = request_id
                        self.counter["parsed_build"] += 1

                    if have_organizations and (entry_orgs in response_url): # Если URL содержит нужный "list"
                        target_orgs_request = response_url
                        target_orgs_request_id = request_id
                        self.counter["parsed_orgs_in_build"] += 1
                        count_entry_list += 1

            if count_entry_list > 1:
                self.counter["many_files_orgs_in_build"] += 1

            # print(f"Количество логов при одном перехвате: {len(logs)}")
            # print(f"Количество лога list?key при одном перехвате: {count_entry_list}")

            # Получение JSON здания и сохранение в файл
            if target_byid_request and target_byid_request_id:
                response = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": target_byid_request_id})
                data = json.loads(response["body"])

                with open("byid_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                self.counter["saved_build_json"] += 1
                print("✅ Данные о здании сохранены в byid_data.json")

            # Получение JSON организаций и сохранение в файл
            if target_orgs_request and target_orgs_request_id:
                response = self.driver.execute_cdp_cmd("Network.getResponseBody",{"requestId": target_orgs_request_id})
                data = json.loads(response["body"])

                with open("organizations_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                print("✅ Данные об организациях сохранены в organizations_data.json")
                self.counter["saved_orgs_in_build_json"] += 1

        except Exception as e:
            self.counter["error_intercept_network"] += 1
            print(f"❌ Ошибка при перехвате запросов: {e}")

    @staticmethod
    def extract_building_id(href):
        """ Извлечение ID здания из ссылки """
        match = re.search(r"/irkutsk/[^/]+/(\d+)", href)
        if match:
            return match.group(1)
        return None

    def process_address(self, address):
        """ Поиск адреса в 2GIS """
        self.driver.get("https://2gis.ru/irkutsk")
        self.wait_for_page_load()

        try:
            # Элемент Поле поиска
            input_box = WebDriverWait(self.driver, 10).until(
                # EC.presence_of_element_located((By.CSS_SELECTOR, "input._h7eic2"))
                EC.presence_of_element_located((By.CSS_SELECTOR, "input._cu5ae4"))
            )
            input_box.clear()
            input_box.send_keys(address)

            # Элемент Подсказок поиска
            suggestion = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li._1914vup"))
            )
            suggestion.click()

            # Элемент Инфо
            info_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='Инфо']"))
            )
            href = info_element.get_attribute("href")

            # Наличие организаций в здании
            have_organizations = False
            try:
                # Элемент В здании (организации)
                in_building = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[text()='В здании']"))
                )
                in_building.click()
                have_organizations = True
                print("✅ Есть организации в данном здании")

            except Exception as eOrganizationsNotFound:
                print("⭕ Организаций в данном здании нет")

            building_id = self.extract_building_id(href)
            if building_id:
                self.counter["build"] += 1
                if have_organizations:
                    self.counter["orgs_in_build"] += 1

                print(f"✅ Найден building_id: {building_id}")
                self.intercept_network_requests(building_id, have_organizations)
            else:
                self.counter["error_not_found_build_id"] += 1
                print("❌ Не удалось найти building_id в ссылке!")

            #self.clear_cache_and_cookies()

        except Exception as e:
            print(f"❌ Ошибка обработки адреса {address}: {e}")
            return False

        return True

    def run(self):
        """ Запуск парсера """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                addresses = file.read().splitlines()

            for address in addresses:
                if address.strip():
                    print(f"\n🔍 Обрабатываем: {address}")
                    success = self.process_address(address)

                    if not success:
                        print("⭕ Не удалось обработать адрес, повторная попытка через 10 секунд")
                        time.sleep(10)
                        self.process_address(address)

                time.sleep(2)

        except FileNotFoundError as e:
            print(f"❌ Файл {self.file_path} не найден")

        finally:
            print(self.counter)
            self.driver.quit()


if __name__ == "__main__":
    file_path = "irkutsk_addresses_sorted.txt"
    parser = AddressParser(file_path=file_path, headless=False)
    parser.run()
