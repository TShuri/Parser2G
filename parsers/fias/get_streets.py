import requests
from bs4 import BeautifulSoup


def get_streets(url, log_func=None):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", class_="mFastSearch_key")

        streets = []
        if log_func: log_func(f"Найдено адресов: {len(links)}")
        for idx, link in enumerate(links, start=1):
            address_name = link.text.strip()
            href = link.get("href")
            street_url = "https://fias.alta.ru" + href if href else ""

            parent_span = link.find_parent("span", class_="kladrs-objects__label")
            street_type = None

            if parent_span:
                next_sibling = parent_span.find_next_sibling("span", class_="gray")
                if next_sibling:
                    street_type = next_sibling.text.strip()

            streets.append({
                "name": address_name,
                "type": street_type,
                "url": street_url
            })
            if log_func: log_func(f"[{idx}/{len(links)}] Найдено: {address_name}")

        return streets

    except Exception as e:
        if log_func: log_func(f"❌ Ошибка при получении адресов: {e}")
        print("error", e)
        return []


# Пример использования
if __name__ == "__main__":
    URL = "https://fias.alta.ru/8eeed222-72e7-47c3-ab3a-9a553c31cf72/"
    streets = get_streets(url=URL)
    print(streets)
