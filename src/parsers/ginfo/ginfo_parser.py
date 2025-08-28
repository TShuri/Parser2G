import requests
from bs4 import BeautifulSoup
import json
import os

headers = {"User-Agent": "Mozilla/5.0"}


class GinfoParser:
    def __init__(self, log, base_url="https://irkutsk.ginfo.ru"):
        self.log = log
        self.BASE_URL = base_url

    # --- Извлечение районов ---
    def get_districts(self):
        """
        Returns:
            List(Dict('name', 'url')): Возваращает список словаря с названием и url района
        """
        try:
            self.log("Поиск районов")
            url = self.BASE_URL + "/rayoni"
            self.log(f"{url}")
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            districts = []
            for idx, a in enumerate(soup.find_all("a", class_="rayon_link"), start=1):
                name = a.text.strip()
                url = self.BASE_URL + a["href"]
                districts.append({"name": name, "url": url})
                self.log(f"[{idx}] Найден район: {name}")
            self.save_to_temp("districts", districts)  # Сохраняем в файл
            self.log(f"Найдено районов: {len(districts)}")

            return districts
        except Exception as e:
            self.log(f"Ошибка при получении районов: {e}")

    # --- Извлечение url улиц ---
    def get_streets(self, district_url):
        """
        Args:
            district_url (str): URL страницы района, для которого нужно получить список url улиц
        Returns:
            list(str): Список url улиц
        """
        try:
            # Получаем страницу района
            response = requests.get(district_url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Находим на странице ссылку на "все улицы" и переходим по ней, если она есть
            show_all_a = soup.find(
                "a",
                class_="show_all",
                string=lambda s: s and "все улицы" in s.lower(),
            )
            url = self.BASE_URL + show_all_a["href"]
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            streets_links = []
            for idx, a in enumerate(soup.find_all("a", class_="ulica_link"), start=1):
                url = self.BASE_URL + a["href"]
                streets_links.append(url)
                self.log(f"[{idx}] Найдена улица: {url}")
            return streets_links

        except Exception as e:
            self.log(f"Ошибка при получении url улиц: {e}")

    def get_street_info(self, street_url):
        """
        Args:
            street_url (str): url страницы уилцы.

        Returns:
            Dict: Словарь содеражщий информацию об улице тип, название, город, район, 
            протяженность, коль-во строений, коль-во перекресток и список домов.
        """
        try:
            # Здесь логика парсинга отдельной страницы улицы
            response = requests.get(street_url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            info_block = soup.find("table", class_="ulica_info")

            type_street_th = info_block.find("th", string="Тип")
            name_th = info_block.find("th", string="Название")
            city_th = info_block.find("th", string="Город")
            district_th = info_block.find("th", string="Округ")
            length_th = info_block.find("th", string="Протяженность")
            buildings_th = info_block.find("th", string="Кол-во строений")
            crossroads_th = info_block.find("th", string="Перекрестки")

            type_street = None
            name = None
            city = None
            district = None
            length = None
            count_buildings = None
            crossroads = None

            if type_street_th and type_street_th.find_next_sibling("td"):
                type_street = type_street_th.find_next_sibling("td").text
            if name_th and name_th.find_next_sibling("td"):
                name = name_th.find_next_sibling("td").text
            if city_th and city_th.find_next_sibling("td"):
                city = city_th.find_next_sibling("td").text
            if district_th and district_th.find_next_sibling("td"):
                district = district_th.find_next_sibling("td").text
            if length_th and length_th.find_next_sibling("td"):
                length = length_th.find_next_sibling("td").text
            if buildings_th and buildings_th.find_next_sibling("td"):
                count_buildings = buildings_th.find_next_sibling("td").text
            if crossroads_th and crossroads_th.find_next_sibling("td"):
                crossroads = crossroads_th.find_next_sibling("td").text

            # Собираем все номера домов с class="dom_link"
            numbers_houses = []
            for dom_a in soup.find_all("a", class_="dom_link"):
                dom_text = dom_a.text.strip()
                if dom_text:
                    numbers_houses.append(dom_text)

            return {
                "type_street": type_street,
                "name": name,
                "city": city,
                "district": district,
                "length": length,
                "count_buildings": count_buildings,
                "crossroads": crossroads,
                "numbers_houses": numbers_houses,
            }

        except Exception as e:
            self.log(f"Ошибка при парсинге страницы улицы {street_url}: {e}")

    def save_to_temp(self, name_file, data, append=False):
        """
        Сохраняет список данных в указанный JSON-файл во временной папке.
        Если append=True, данные будут добавлены к существующему списку.
        """
        name_file = f"{name_file}.json"
        temp_dir = os.path.join(os.path.dirname(__file__), "../../../data/temp/ginfo")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, name_file)
        try:
            if append and os.path.exists(temp_file):
                with open(temp_file, "r", encoding="utf-8") as f:
                    try:
                        existing_data = json.load(f)
                    except Exception:
                        existing_data = []
                # Дозапись только для списков
                if isinstance(existing_data, list):
                    data = existing_data + data
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.log(f"Ошибка при сохранении данных: {e}")

    def clear_temp_file(self, name_file):
        """
        Очищает указанный JSON-файл во временной папке (делает его пустым списком).
        """
        name_file = f"{name_file}.json"
        temp_dir = os.path.join(os.path.dirname(__file__), "../../../data/temp/ginfo")
        temp_file = os.path.join(temp_dir, name_file)
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            self.log(f"Файл {temp_file} очищен.")
        except Exception as e:
            self.log(f"Ошибка при очистке файла: {e}")


if __name__ == "__main__":
    ginfo_parser = GinfoParser()

    districts = ginfo_parser.get_districts()

    for district in districts:
        ginfo_parser.get_streets(district["url"])
