import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://irkutsk.ginfo.ru"
START_URL = f"{BASE_URL}"
OUTPUT_FILE = "../../data/ginfo/irkutsk_districts.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_districts():
    try:
        response = requests.get(START_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Ищем div с классом main_block, в котором есть ссылки на районы
        main_block = soup.find("div", class_="main_block")
        if not main_block:
            #print("Не найден основной блок с районами")
            return []

        # Обычно ссылки на районы — внутри div после заголовка, либо просто в main_block
        # На всякий случай собираем все ссылки в main_block с href, содержащим '/rayoni/'
        district_links = []
        for a in main_block.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/rayoni/") and href != "/rayoni/":
                district_links.append(a)

        districts = []
        for a in district_links:
            name = a.text.strip()
            url = BASE_URL + a["href"]
            districts.append({"name": name, "url": url})

        return districts

    except Exception as e:
        #print(f"Ошибка при получении районов: {e}")
        return []

def main():
    districts = get_districts()

    if districts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(districts, f, ensure_ascii=False, indent=2)
        #print(f"Сохранено {len(districts)} районов в файл {OUTPUT_FILE}")
    else:
        pass
        #print("Не удалось получить список районов.")

    return districts

if __name__ == "__main__":
    main()
