import requests
import xml.etree.ElementTree as ET
import re

# URL Overpass API
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Название района, который нужно спарсить
DISTRICT_NAME = "Октябрьский административный округ"

# Overpass-запрос для поиска зданий с адресами в указанном районе
overpass_query = f"""
[out:xml][timeout:25];
area[name="Иркутск"]->.cityArea;
area[name="{DISTRICT_NAME}"](area.cityArea)->.districtArea;
(
  node["addr:street"](area.districtArea);
  way["addr:street"](area.districtArea);
  relation["addr:street"](area.districtArea);
);
out body;
>;
out skel qt;
"""

# Выполняем запрос к Overpass API
response = requests.get(OVERPASS_URL, params={"data": overpass_query})
if response.status_code != 200:
    print(f"Ошибка: не удалось получить данные (HTTP {response.status_code})")
    exit()

# Разбираем XML-ответ
root = ET.fromstring(response.content)

# Извлекаем адреса
addresses = []
for element in root.findall(".//node") + root.findall(".//way") + root.findall(".//relation"):
    addr_street = None
    addr_housenumber = None

    for tag in element.findall("tag"):
        key = tag.attrib.get("k")
        value = tag.attrib.get("v")
        if key == "addr:street":
            addr_street = value
        elif key == "addr:housenumber":
            addr_housenumber = value

    if addr_street and addr_housenumber:
        addresses.append((addr_street, addr_housenumber))

# Функция для сортировки адресов
def extract_number(house):
    """Извлекает числовую часть из номера дома."""
    match = re.search(r'\d+', house)
    return int(match.group()) if match else float('inf')

# Сортируем по названию улицы и номеру дома
addresses = sorted(addresses, key=lambda x: (x[0], extract_number(x[1])))
formatted_addresses = [f"{street}, {housenumber}" for street, housenumber in addresses]

# Сохраняем в файл
txt_filename = f"addresses_{DISTRICT_NAME.lower()}.txt"
with open(txt_filename, mode="w", encoding="utf-8") as txtfile:
    txtfile.write("\n".join(formatted_addresses))

print(f"Адреса в районе {DISTRICT_NAME} сохранены в {txt_filename}")
