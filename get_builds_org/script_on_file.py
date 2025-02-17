import json
import logging
import time
import re
import datetime
import os
import sys
import signal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Настройка логирования
LOG_FILE = "parser.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

class AddressParser:
    def __init__(self, filepath, out_folder, headless=False):
        self.filepath = filepath
        self.out_folder = out_folder
        self.headless = headless
        self.addresses = []
        self.driver = None

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

            "start_time": datetime.datetime.now().isoformat(),
            "end_time": 0
        }
        self.init_browser()

    def configure_browser_options(self):
        """ Настройка параметров браузера """
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        if self.headless:
            options.add_argument("--headless")

        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2
        })
        options.set_capability("goog:loggingPrefs", {"performance": "INFO"})
        return options

    def init_browser(self):
        """ Инициализация Selenium WebDriver """
        logging.info("Start init browser")
        options = self.configure_browser_options()
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        logging.info("browser initialized")

    def load_addresses_from_file(self):
        """ Загрузка адресов из файла с адресами """
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                self.addresses = file.read().splitlines()
                logging.info(f"Loaded {len(self.addresses)} addresses from {self.filepath}")
        except FileNotFoundError:
            print("Ошибка, файл с адресами не найден!")
            logging.error("File with addresses not found!")
            sys.exit(0)

    def save_json_data(self, filename, data):
        """ Сохранение данных в JSON-файл """
        logging.info(f"Start save_json_data to {filename}")
        filepath = os.path.join(self.out_folder, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json.loads(data), f, ensure_ascii=False, indent=4)
        logging.info(f"Finished save_json_data in {filepath}")

    def get_response_body(self, request_id):
        """ Получение тела ответа запроса """
        return self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}).get("body")

    def intercept_network_requests(self, building_id, have_organizations):
        """Перехват сетевых запросов."""
        logging.info("Intercept_network_requests")
        try:
            time.sleep(3)
            logs = self.driver.get_log("performance")

            byid_data, orgs_data = None, None
            entry_byid = f"byid?id={building_id}"
            entry_orgs = "list?"

            logging.info("Start cycle for log in logs")
            for log in logs:
                message = json.loads(log["message"])["message"]
                if message["method"] != "Network.responseReceived":
                    continue

                request_id = message["params"]["requestId"]
                url = message["params"].get("response", {}).get("url", "")

                if entry_byid in url:
                    byid_data = self.get_response_body(request_id)
                    self.counter["parsed_build"] += 1

                if have_organizations and entry_orgs in url:
                    orgs_data = self.get_response_body(request_id)
                    self.counter["parsed_orgs_in_build"] += 1
            logging.info("Finish cycle for log in logs")

            if byid_data:
                self.save_json_data(f"builds_json/byid_{building_id}.json", byid_data)
                self.counter["saved_build_json"] += 1
                print(f"✅ Данные о здании сохранены (ID: {building_id})")

            if orgs_data:
                self.save_json_data(f"orgs_in_builds_json/list_{building_id}.json", orgs_data)
                self.counter["saved_orgs_in_build_json"] += 1
                print(f"✅ Данные об организациях сохранены (ID: {building_id})")

        except Exception as e:
            self.counter["error_intercept_network"] += 1
            print(f"❌ Ошибка при перехвате запросов: {e}")

    def wait_for_page_load(self, timeout=10):
        """ Ожидание полной загрузки страницы """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def extract_building_id(self, href):
        """ Извлечение ID здания из ссылки """
        match = re.search(r"/irkutsk/[^/]+/(\d+)", href)
        return match.group(1) if match else None

    def handle_suggestions(self, address):
        """ Ввод адреса в поле поиска и выбор подсказки """
        logging.info("Start handle_suggestions")
        input_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input._cu5ae4"))
        )
        input_box.clear()
        input_box.send_keys(address)

        suggestion = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li._1914vup"))
        )
        suggestion.click()
        logging.info("Finished handle_suggestions")

    def handle_building_info(self):
        """ Получение ссылки на здание """
        logging.info("Start handle_building_info")
        info_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Инфо']"))
        )
        logging.info("Finished handle_building_info")
        return info_element.get_attribute("href")


    def check_organizations_in_building(self):
        """ Проверка наличия организаций в здании """
        logging.info("Start check_organizations_in_building")
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//a[text()='В здании']"))
            ).click()
            print("✅ Есть организации в здании")
            return True
        except:
            print("⭕ Организаций нет")
            return False
        finally:
            logging.info("Finished check_organizations_in_building")

    def process_address(self, address):
        """ Обработка адреса в 2GIS """
        logging.info(f"{'-' * 40} Processing address {address} {'-' * 40}")
        self.driver.get("https://2gis.ru/irkutsk")
        self.wait_for_page_load()

        try:
            self.handle_suggestions(address)
            href = self.handle_building_info()
            have_organizations = self.check_organizations_in_building()

            building_id = self.extract_building_id(href)
            if building_id:
                self.counter["build"] += 1
                if have_organizations:
                    self.counter["orgs_in_build"] += 1
                self.intercept_network_requests(building_id, have_organizations)
            else:
                self.counter["error_not_found_build_id"] += 1
                print("❌ Не удалось найти building_id!")
                logging.warning(f"Not founded building_id for {address}")
            return True
        except Exception as e:
            self.counter["error_address_processing"] += 1
            print(f"❌ Ошибка обработки адреса {address}: {e}")
            logging.error(f"Error process_address {address}: {e}")
            return False

    def run(self):
        """ Запуск парсера """
        try:
            self.load_addresses_from_file()

            count_addresses = len(self.addresses)
            for num, address in enumerate(self.addresses, start=1):
                print(f"\n🔍 Обрабатываем: {address} ({num}/{count_addresses})")
                self.try_process_address(address)

        except Exception as e:
            print(f"❌ Ошибка выполнения парсера: {e}")

        finally:
            self.shutdown()

    def try_process_address(self, address, max_attempts=2):
        """ Пытается обработать адрес несколько раз при неудаче """
        for attempt in range(1, max_attempts + 1):
            if self.process_address(address):
                return
            print(
                f"⭕ Попытка {attempt} не удалась. Повторная попытка..." if attempt < max_attempts else "❌ Отказ от обработки.")

    def save_statistics(self):
        """ Сохраняет статистику в JSON перед выходом """
        self.counter["end_time"] = datetime.datetime.now().isoformat()
        with open("parser_stats.json", "w", encoding="utf-8") as f:
            json.dump(self.counter, f, ensure_ascii=False, indent=4)
        print("📊 Статистика сохранена в parser_stats.json")

    def shutdown(self):
        """ Завершение работы парсера: сохранение статистики и закрытие браузера """
        print("\n🛑 Завершение работы парсера...")
        self.save_statistics()
        if self.driver:
            self.driver.quit()
        sys.exit(0)  # Завершаем программу


if __name__ == "__main__":
    file_addresses = "../addresses_свердловский административный округ.txt"
    folder_name = "Свердловский"
    parser = AddressParser(filepath=file_addresses, out_folder=folder_name, headless=False)

    def handle_exit_signal(sig, frame):
        """ Обработчик сигнала SIGINT (Ctrl+C) и SIGTERM """
        print("\n🛑 Остановка по сигналу, завершаем работу...")
        parser.shutdown()

    signal.signal(signal.SIGINT, handle_exit_signal)
    signal.signal(signal.SIGTERM, handle_exit_signal)

    parser.run() # Запуск парсера