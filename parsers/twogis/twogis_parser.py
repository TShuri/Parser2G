import json
import logging
import os
import time
import re
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Настройка логирования
# Создание абсолютного пути к лог-файлу рядом со скриптом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "twogis_parser.log")

# Убедимся, что директория для лога существует
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

class TwoGisParser:
    def __init__(self, headless=False, limit_restart=300):
        self.headless = headless
        self.limit_restart = limit_restart
        self.address = None
        self.build = None
        self.organizations = None
        self.driver = None
        self.restart_counter = 0
        self.stats = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "total": 0,
            "extracted_success": 0,
            "found_buildings": 0,
            "found_organizations": 0,
            "not_match_address": 0,
            "error_intercepting": 0,
            "not_found_id": 0,
            "error_process": 0,
        }
        self.init_browser()

    def configure_browser_options(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2
        })
        options.set_capability("goog:loggingPrefs", {"performance": "INFO"})
        return options

    def init_browser(self):
        logging.info("Start init browser")
        options = self.configure_browser_options()
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.open_site()
        logging.info("Browser initialized")

    def restart_browser(self):
        try:
            if self.driver:
                self.driver.quit()
            logging.info("Перезапуск браузера...")
            self.init_browser()
            self.restart_counter = 0  # сбрасываем счётчик
        except Exception as e:
            logging.error(f"Ошибка при перезапуске браузера: {e}")

    def get_build(self):
        return self.build

    def get_organizations(self):
        return self.organizations

    def get_response_body(self, request_id):
        return self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}).get("body")

    def intercept_network_requests(self, building_id, have_organizations):
        logging.info("Intercept_network_requests")
        try:
            time.sleep(2)
            logs = self.driver.get_log("performance")

            entry_byid = f"byid?id={building_id}"
            entry_orgs = "list?"

            for log in logs:
                message = json.loads(log["message"])["message"]
                if message["method"] != "Network.responseReceived":
                    continue

                request_id = message["params"]["requestId"]
                url = message["params"].get("response", {}).get("url", "")

                if entry_byid in url:
                    byid_data = self.get_response_body(request_id)
                    self.build = byid_data
                    self.stats["found_buildings"] += 1

                if have_organizations and entry_orgs in url:
                    orgs_data = self.get_response_body(request_id)
                    self.organizations = orgs_data
                    self.stats["found_organizations"] += 1

            logging.info("Data extracted success")
            self.stats["extracted_success"] += 1
        except Exception as e:
            logging.error(f"Error while intercepting requests: {e}")
            self.stats["error_intercepting"] += 1

    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def extract_building_id(self, href):
        match = re.search(r"/irkutsk/[^/]+/(\d+)", href)
        return match.group(1) if match else None

    def open_site(self):
        self.driver.get("https://2gis.ru/irkutsk")
        self.wait_for_page_load()

    def handle_input(self, address):
        logging.info("handle_input")
        input_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Поиск в 2ГИС']")))
        input_box.send_keys(Keys.CONTROL + "a")
        input_box.send_keys(Keys.BACKSPACE)
        input_box.send_keys(address)
        input_box.send_keys(Keys.ENTER)

    def handle_not_match(self):
        logging.info("handle_not_match")
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[1][text()='Точных совпадений нет. Посмотрите похожие места или измените запрос.']")))
            return True
        except TimeoutException:
            return False

    def handle_count_found(self):
        logging.info("handle_count_found")
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div/div[1]/header/div[3]/div/div[1]/div/h2/a/span")))
        count = int(element.text.strip())
        return count

    def handle_suggestions(self):
        logging.info("handle_suggestions")
        suggestion = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div[1]/div")))
        suggestion.click()

    def handle_building_info(self):
        logging.info("handle_building_info")
        info_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[text()='Инфо']")))
        return info_element.get_attribute("href")

    def check_organizations_in_building(self):
        logging.info("check_organizations_in_building")
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[text()='В здании']"))).click()
            return True
        except:
            return False

    def process_address(self, address):
        logging.info(f"{'-' * 40} Processing address {address} {'-' * 40}")
        self.stats["total"] += 1
        try:
            self.handle_input(address)
            if self.handle_not_match():
                logging.info("Not founded address in 2gis")
                self.stats["not_match_address"] += 1
                return True
            # if self.handle_count_found() > 1:
            self.handle_suggestions()
            href = self.handle_building_info()
            have_organizations = self.check_organizations_in_building()
            building_id = self.extract_building_id(href)
            if building_id:
                self.intercept_network_requests(building_id, have_organizations)
            else:
                logging.warning(f"Not found building_id for {address}")
            return True
        except Exception as e:
            logging.error(f"Error process_address {address}: {e}")
            self.stats["error_process"] += 1
            return False

    def save_stats_to_json(self, filename=None):
        try:
            self.stats["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"twogis_stats.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=4, ensure_ascii=False)
        except Exception as e:
            pass

    def run(self, address, max_attempts=2):
        self.address = address
        self.build = None
        self.organizations = None
        for attempt in range(1, max_attempts + 1):
            if self.process_address(address):
                break

        self.save_stats_to_json()
        self.restart_counter += 1
        if self.restart_counter >= self.limit_restart:
            logging.info(f"Достигнут лимит в {self.limit_restart} адресов — перезапуск браузера")
            self.restart_browser()

    def close(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    addresses = ['Иркутск, Ленина, 15', 'Иркутск, крылатый, 4', 'Иркутск, Лермонтова 83, ', 'Иркутск, Советская 33']
    parser = TwoGisParser(limit_restart=2)
    for address in addresses:
        parser.run(address)

