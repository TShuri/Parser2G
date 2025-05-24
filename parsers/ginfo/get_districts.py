import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://irkutsk.ginfo.ru"
START_URL = f"{BASE_URL}/ulicy/?okrug=32"
OUTPUT_FILE = "../../data/irk_ginfo/irkutsk_streets_ленинский.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_streets_with_links():
    try:
        response = requests.get(START_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        street_links = soup.select("a.ulica_link")
        streets = []

        for a in street_links:
            span = a.find("span")
            if span and span.next_sibling:
                street_name = span.next_sibling.strip()
                href = a.get("href", "").strip()
                if href:
                    street_url = BASE_URL + href
                    streets.append({
                        "name": street_name,
                        "url": street_url
                    })

        return streets

    except Exception as e:
        print(f"Ошибка при получении списка улиц: {e}")
        return []

def main():
    streets = get_streets_with_links()

    if streets:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(streets, f, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(streets)} улиц в файл {OUTPUT_FILE}")
    else:
        print("Не удалось получить список улиц.")

if __name__ == "__main__":
    main()
