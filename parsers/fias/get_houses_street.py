import requests
from bs4 import BeautifulSoup
import json
import time

INPUT_FILE = "../../data/fias/irkutsk_name_streets.json"
OUTPUT_FILE = "../../data/fias/irkutsk_houses.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_houses(street_name, street_type, street_url):
    if street_url.startswith("http"): # Если ссылка абсолютная (начинается с http), используем как есть, иначе добавляем домен
        url = street_url
    else:
        url = "https://fias.alta.ru" + street_url

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        house_links = soup.select("a.kladrs-objects__number")
        addresses = []
        for a in house_links:
            house = a.text.strip()
            full_address = f"{street_type} {street_name} {house}"
            address = {
                "full_address": full_address,
                "street_type": street_type,
                "street": street_name,
                "house": house
            }
            addresses.append(address)
        return addresses
    except Exception as e:
        print(f"Ошибка при обработке {street_name} ({url}): {e}")
        return []

def get_addresses(streets, log_func=None):
    all_data = []
    for i, street in enumerate(streets, 1):
        street_name = street["name"]
        street_type = street["type"]
        street_url = street["url"]
        if log_func: log_func(f"[{i}/{len(streets)}] Обрабатываем: {street_name}")
        data = get_houses(street_name, street_type, street_url)
        all_data.extend(data)
        time.sleep(0.5)  # пауза, чтобы не перегружать сервер

if __name__ == "__main__":
    addr1 = {'name': '3-я Железнодорожная',
             'type': 'Улица',
             'url': 'https://fias.alta.ru/fd65992f-9aaa-4bdc-bfd8-ac8da86e7d90/'}
    addr2 = {'name': '3-я Карьерная',
             'type': 'Улица',
             'url': 'https://fias.alta.ru/21693fea-947f-41ed-b091-5d19dead9c2a/'}
    addr3 = {'name': '3-я Кировская',
             'type': 'Улица',
             'url': 'https://fias.alta.ru/b3a17b9f-6170-4c7b-82c5-03aba077f5a9/'}
    streets = [addr1]
    get_addresses(streets)
