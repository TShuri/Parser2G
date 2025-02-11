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
    def __init__(self, headless=False):
        self.headless = headless
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

    def clear_cache_and_cookies(self):
        """ Очистка кеш и куки """
        try:
            self.driver.execute_cdp_cmd("Network.clearBrowserCache", {})
            self.driver.execute_cdp_cmd("Network.clearBrowserCookies", {})
            print("🧹 Кэш и куки очищены")

        except Exception as e:
            print(f"⚠ Ошибка при очистке кэша и логов: {e}")

    def intercept_network_requests(self, building_id):
        """ Перехват нужного byid-запроса """
        try:
            time.sleep(3)  # Время для загрузки запросов
            logs = self.driver.get_log("performance")

            target_byid_request = None
            target_request_id = None
            entry_byid = f"byid?id={building_id}"

            for log in logs:
                log_json = json.loads(log["message"])["message"]

                if log_json["method"] == "Network.responseReceived":
                    request_id = log_json["params"]["requestId"]
                    response_url = log_json["params"]["response"]["url"]

                    if entry_byid in response_url: # Если URL содержит нужный "byid", сохраняем его
                        target_byid_request = response_url
                        target_request_id = request_id
                        break

            if target_byid_request and target_request_id:
                print(f"✅ Найденный byid-запрос: {target_byid_request}")

                # Получаем тело ответа в виде JSON
                response = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": target_request_id})
                data = json.loads(response["body"])

                # Сохраняем JSON в файл
                with open("byid_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                print("✅ Данные сохранены в byid_data.json")

        except Exception as e:
            print(f"❌ Ошибка при перехвате запросов: {e}")

    def search_address(self, address):
        """ Поиск адреса в 2GIS """
        self.driver.get("https://2gis.ru/irkutsk")

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
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a._rdxuhv3"))
            )

            # Получение id здания из ссылки элемента Инфо
            href = info_element.get_attribute("href")
            match = re.search(r"/irkutsk/\w+/(\d+)(?:\?|$)", href)
            if match:
                building_id = match.group(1)
                print(f"✅ Найден building_id: {building_id}")
                self.intercept_network_requests(building_id)
            else:
                print("❌ Не удалось найти building_id в ссылке!")

            self.clear_cache_and_cookies()

        except Exception as e:
            print(f"❌ Ошибка обработки адреса {address}: {e}")

    def run(self):
        """ Запуск парсера """
        try:
            address = "улица Лермонтова, 83"
            # address = "крылатый 4"
            print(f"\n🔍 Обрабатываем: {address}")
            self.search_address(address)
            time.sleep(2)

        except Exception as e:
            print(f"❌ Ошибка: {e}")

        finally:
            self.driver.quit()


if __name__ == "__main__":
    parser = AddressParser(headless=False)
    parser.run()
