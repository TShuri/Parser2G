import json
import logging
import os
import time
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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
    def __init__(self, address=None, headless=False):
        self.address = address
        self.build = False
        self.organizations = False
        self.headless = headless
        self.driver = None

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
        logging.info("Browser initialized")

    def set_address(self, address):
        self.address = address

    def get_build(self):
        return self.build

    def get_organizations(self):
        return self.organizations

    def get_response_body(self, request_id):
        return self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}).get("body")

    def intercept_network_requests(self, building_id, have_organizations):
        logging.info("Intercept_network_requests")
        try:
            time.sleep(3)
            logs = self.driver.get_log("performance")

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
                    self.build = byid_data

                if have_organizations and entry_orgs in url:
                    orgs_data = self.get_response_body(request_id)
                    self.organizations = orgs_data

            logging.info("Finish cycle for log in logs")

        except Exception as e:
            print(f"Error while intercepting requests: {e}")

    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def extract_building_id(self, href):
        match = re.search(r"/irkutsk/[^/]+/(\d+)", href)
        return match.group(1) if match else None

    def handle_suggestions(self, address):
        logging.info("Start handle_suggestions")
        input_box = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input._cu5ae4")))
        input_box.clear()
        input_box.send_keys(address)

        suggestion = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li._1914vup")))
        suggestion.click()
        logging.info("Finished handle_suggestions")

    def handle_building_info(self):
        logging.info("Start handle_building_info")
        info_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='Инфо']")))
        logging.info("Finished handle_building_info")
        return info_element.get_attribute("href")

    def check_organizations_in_building(self):
        logging.info("Start check_organizations_in_building")
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[text()='В здании']"))).click()
            return True
        except:
            print("No organizations in the building")
            return False
        finally:
            logging.info("Finished check_organizations_in_building")

    def process_address(self, address):
        logging.info(f"{'-' * 40} Processing address {address} {'-' * 40}")
        self.driver.get("https://2gis.ru/irkutsk")
        self.wait_for_page_load()

        try:
            self.handle_suggestions(address)
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
            return False

    def run(self, address=None, max_attempts=2):
        if address:
            self.set_address(address)

        for attempt in range(1, max_attempts + 1):
            if self.process_address(address):
                return

    def close(self):
        if self.driver:
            self.driver.quit()


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("No address provided. Usage: python script.py \"address\"")
#         sys.exit(1)
#
#     input_address = sys.argv[1]
#     parser = AddressParser(address=input_address, headless=False)
#     parser.run()

