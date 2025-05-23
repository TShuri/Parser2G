import requests
import xml.etree.ElementTree as ET

# URL Overpass API
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Overpass-запрос для поиска районов Иркутска
overpass_query = """
[out:xml][timeout:25];
area[name="Иркутск"]->.searchArea;
relation["boundary"="administrative"]["admin_level"="9"](area.searchArea);
out body;
"""

# Выполняем запрос к Overpass API
response = requests.get(OVERPASS_URL, params={"data": overpass_query})
if response.status_code != 200:
    print(f"Ошибка: не удалось получить данные (HTTP {response.status_code})")
    exit()

# Разбираем XML-ответ
root = ET.fromstring(response.content)

# Извлекаем названия районов
districts = []
for relation in root.findall(".//relation"):
    for tag in relation.findall("tag"):
        if tag.attrib.get("k") == "name":
            districts.append(tag.attrib.get("v"))

# Убираем дубликаты и сортируем список
sorted_districts = sorted(set(districts))

# Сохраняем в файл
txt_filename = "../../data/osm/districts/irkutsk_districts.txt"
with open(txt_filename, mode="w", encoding="utf-8") as txtfile:
    txtfile.write("\n".join(sorted_districts))

print(f"Список районов сохранен в {txt_filename}")