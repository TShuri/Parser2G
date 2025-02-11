import time
import re
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright
from pathlib import Path

def extract_data(data):
     # Адрес
    address_name = data["address_name"]

    # Район
    district_name = None
    for adm_div in data["adm_div"]:
        if adm_div["type"] == "district":
            district_name = adm_div["name"]
            break

    # Геометрия
    geometry = data["geometry"]["centroid"]

    # Использование регулярного выражения для извлечения чисел
    match = re.match(r"POINT\(([-\d.]+)\s([-\d.]+)\)", geometry)

    longitude = float(match.group(1))  # Долгота
    latitude = float(match.group(2))   # Широта

    # 4. Назначение
    purpose_name = data["purpose_name"]

    data = {
        'address_name': address_name,
        'district_name': district_name,
        'longitude': longitude,
        'latitude': latitude,
        'purpose_name': purpose_name
    }

    return data


current_state="INFO"
current_address=""

def on_response(response):
    global id,current_state,current_address
    match current_state:
        case "INPUT":
            if "suggests" in response.url:
                parsed_url = urlparse(response.url)
                query_params = parse_qs(parsed_url.query)
                if query_params.get('q', [None])[0] == current_address:
                    try:
                        data = response.json()
                        items = data.get('result', {}).get('items', [])
                        if items:
                            for i in range(len(items)):
                                if items[i]["address"]["components"][0]["number"].lower() == current_address.split(", ")[1].lower():
                                    id = items[i]["address"]["building_id"]
                                    element_index=0
                                    break
                            if id == None: print('nothing right for us');id=""
                        else:
                            print("NOTHING FOUND " * 4)
                            id=""
                    except Exception as e:
                        print(f"ERROR: {e}")
                        id=""

        case "HOUSE_INFO":
            if "byid" in response.url and id in response.url:
                try:
                    data=response.json()
                    items = data.get('result',{}).get('items',[])[0]
                    if items:
                        # branches = items.get('links',{}).get('branches',{}).get('count',0)
                        print(extract_data(items))
                        current_state="ORGANIZATIONS"      
                    else: print('no items')
                except Exception as e:
                    print(f"ERROR: {e}")
        case "ORGANIZATIONS":
            if "list" in response.url and id in response.url:
                try:
                    data=response.json()
                    for i in data['result']['items']:
                        print(f"Название: {i['name']} Расписание: {i['schedule']}")
                        
                except Exception as e:
                    print(f"ERROR: {e}")

def input_text(page, selector, text):
    try:
        field = page.query_selector(selector)
        if field:
            field.click()
            page.fill(selector, text)
            print(f"Successfully inputted text: {text}")
        else:
            print(f"Selector not found: {selector}")
    except Exception as e:
        print(f"Error occurred: {e}")

class AddressParser:
    def __init__(self, file_path, headless=False):
        self.file_path = Path(file_path)
        self.headless = headless
        self.current_address = None
        self.clicked_once = False
        self.timeout = 10000  # 10 секунд таймаут

    def parse_address(self, address):
        address = address.lower().strip()
        match = re.match(r"([\w\s]+?),?\s*(\d+/?\d*)?", address)
        if match:
            street = match.group(1).strip()
            number = match.group(2).strip() if match.group(2) else ""
            return street, number
        return address, ""

    def init_browser(self, playwright):
        browser = playwright.chromium.launch(headless=self.headless)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            java_script_enabled=True,
        )
        context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            """
        )
        return browser, context


    def process_address(self, page, address):
        global current_state, current_address
        current_address = address
        self.clicked_once = False
        
        try:
            current_state="INPUT"
            page.goto("https://2gis.ru/irkutsk", timeout=self.timeout)
            page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            input_selector = "input._cu5ae4"
            # Очистка и ввод адреса
            input_text(page, input_selector, current_address)
            
            page.locator("li._1914vup").nth(0).click()
            print("Clicked on the first address suggestion.")
            current_state="HOUSE_INFO"
            # Ожидание обработки
            start_time = time.time()
            while self.clicked_once and (time.time() - start_time) < 20:
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Ошибка обработки адреса {current_address}: {e}")
            return False
        return True

    def run(self):
        if not self.file_path.exists():
            print(f"Файл {self.file_path} не найден")
            return

        addresses = self.file_path.read_text(encoding='utf-8').splitlines()
        
        with sync_playwright() as playwright:
            browser, context = self.init_browser(playwright)
            page = context.new_page()
            page.on("response", on_response)

            
            for address in addresses:
                if not address.strip():
                    continue
                
                print(f"\nОбработка адреса: {address}")
                success = self.process_address(page, address)
                
                if not success:
                    print("Повторная попытка через 10 секунд...")
                    time.sleep(10)
                    self.process_address(page, address)
                
                time.sleep(2)  # Пауза между запросами
            
            browser.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Путь к файлу с адресами")
    parser.add_argument("--headless", action="store_true", help="Запуск в headless режиме")
    args = parser.parse_args()
    
    parser = AddressParser(args.file_path, headless=args.headless)
    parser.run()