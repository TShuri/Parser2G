import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://irkutsk.ginfo.ru"
DISTRICT = "Свердловский"
INPUT_FILE = f"../../data/ginfo_extra/irkutsk_streets_{DISTRICT.lower()}.json"
OUTPUT_FILE = f"../../data/ginfo_extra/irkutsk_houses_coords_{DISTRICT.lower()}.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_coords(house_url):
    try:
        response = requests.get(house_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        coord_cell = soup.find("th", string="Координаты")
        if coord_cell and coord_cell.find_next_sibling("td"):
            coords_text = coord_cell.find_next_sibling("td").text.strip()
            lat, lon = map(float, coords_text.split(","))
            return lat, lon
    except Exception as e:
        print(f"Ошибка при получении координат ({house_url}): {e}")
    return None, None

def get_houses(street_name, street_type, street_url):
    houses = []
    try:
        response = requests.get(street_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        house_links = soup.select("a.dom_link")
        for a in house_links:
            house_number = a.text.strip()
            house_rel_url = a["href"]
            house_url = BASE_URL + house_rel_url

            lat, lon = get_coords(house_url)

            houses.append({
                "full_address": f"{street_type} {street_name} д. {house_number}",
                "street_type": street_type,
                "street": street_name,
                "house": house_number,
                "lat": lat,
                "lon": lon
            })

            time.sleep(0.2)  # Чтобы не нагружать сайт
    except Exception as e:
        print(f"Ошибка при обработке {street_name} ({street_url}): {e}")
    return houses

def get_addresses(streets, log_func, mock=False):
    # with open(INPUT_FILE, "r", encoding="utf-8") as f:
    #     streets = json.load(f)
    if mock:
        return get_addresses_mock(log_func)

    streets = streets[:3]
    all_data = []

    for i, street in enumerate(streets, 1):
        street_name = street["name"]
        street_type = street["type"]

        # Исправляем двойной BASE_URL
        if street["url"].startswith("http"):
            street_url = street["url"]
        else:
            street_url = BASE_URL + street["url"]

        log_func(f"[{i}/{len(streets)}] Обрабатываем: {street_name}")
        street_data = get_houses(street_name, street_type, street_url)
        all_data.extend(street_data)

        # # Сохраняем прогресс
        # with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        #     json.dump(all_data, f, ensure_ascii=False, indent=2)

        time.sleep(0.5)
    return all_data
    # print(f"Готово! Сохранено {len(all_data)} адресов с координатами в {OUTPUT_FILE}")

def get_addresses_mock(log_func):
    try:
        addresses = []
        with open("../../data/ginfo/irkutsk_houses_coords_октябрьский.json", "r", encoding="utf-8") as f:
            addresses = json.load(f)

        for i, address in enumerate(addresses, 1):
            log_func(f"[{i}/{len(addresses)}] Обрабатываем: {address['street']}")

        return addresses

    except Exception as e:
        print(f"Ошибка при получении списка улиц: {e}")
        return []


if __name__ == "__main__":
    pass
    # main()
