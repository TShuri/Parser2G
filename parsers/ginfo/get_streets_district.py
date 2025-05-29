import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://irkutsk.ginfo.ru"
START_URL = f"{BASE_URL}/ulicy/"
OUTPUT_FILE = "../../data/ginfo/irkutsk_streets.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_name_type_street(street_url):
    try:
        response = requests.get(street_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        name_th = soup.find("th", string="Название")
        type_th = soup.find("th", string="Тип")
        name = None
        type = None

        if name_th and name_th.find_next_sibling("td"):
            name = name_th.find_next_sibling("td").text
        if type_th and type_th.find_next_sibling("td"):
            type = type_th.find_next_sibling("td").text

        return name, type
    except Exception as e:
        print(f"Ошибка при получении названии и типа улицы ({street_url}): {e}")
    return None, None


def get_href(url):
    response = requests.get(url)
    response.raise_for_status()  # Проверка на успешность запроса

    soup = BeautifulSoup(response.text, 'html.parser')

    a_tag = soup.find('a', class_='show_all')
    if a_tag and 'href' in a_tag.attrs:
        return a_tag['href']
    else:
        return None


def get_street_links(district_url, log_func, mock=False):
    if mock:
        return get_streets_mock(log_func)
    try:
        URL = f"{BASE_URL}{get_href(district_url)}"
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        street_links = soup.select("a.ulica_link")
        streets = []

        for idx, link in enumerate(street_links, start=1):
            href = link.get("href", "").strip()
            street_url = BASE_URL+href
            if href:
                name, type = get_name_type_street(street_url)
                log_func(f"[{idx}/{len(street_links)}] Найдено: {name}")
                street_obj = {
                    "name": name,
                    "type": type,
                    "url": street_url
                }
                streets.append(street_obj)

        return streets

    except Exception as e:
        print(f"Ошибка при получении списка улиц: {e}")
        return []

def get_streets_mock(log_func):
    try:
        streets = []
        with open("../../data/ginfo/irkutsk_streets_октябрьский.json", "r", encoding="utf-8") as f:
            streets = json.load(f)

        for idx, street in enumerate(streets, start=1):
            log_func(f"[{idx}/{len(streets)}] Найдено: {street['name']}")

        return streets

    except Exception as e:
        print(f"Ошибка при получении списка улиц: {e}")
        return []

def main():
    streets = get_street_links()

    if streets:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(streets, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(streets)} улиц в файл {OUTPUT_FILE}")
    else:
        print("Не удалось получить список улиц.")

if __name__ == "__main__":
    # main()
    # Пример использования
    url = 'https://irkutsk.ginfo.ru/rayoni/leninskiy_okrug/'  # замените на нужный URL
    href = get_href(url)
    print(href)

