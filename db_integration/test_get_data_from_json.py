import json
import re

# Чтение JSON-файла
def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def extract_data(data):
     # 1. Адрес
    address_name = data["result"]["items"][0]["address_name"]

    # 2. Свердловский район
    district_name = None
    for adm_div in data["result"]["items"][0]["adm_div"]:
        if adm_div["type"] == "district":
            district_name = adm_div["name"]
            break

    # 3. Геометрия
    geometry = data["result"]["items"][0]["geometry"]["centroid"]

    # Использование регулярного выражения для извлечения чисел
    match = re.match(r"POINT\(([-\d.]+)\s([-\d.]+)\)", geometry)

    longitude = float(match.group(1))  # Долгота
    latitude = float(match.group(2))   # Широта

    # 4. Назначение
    purpose_name = data["result"]["items"][0]["purpose_name"]

    # Вывод извлечённых данных
    print(f"Address Name: {address_name}")
    print(f"District Name: {district_name}")
    print(f"longitude: {longitude}")
    print(f"latitude: {latitude}")
    print(f"Purpose Name: {purpose_name}")

if __name__ == "__main__":
    json_file_path = "building_1.json"  # Путь к вашему JSON-файлу
    data = read_json(json_file_path)
    extract_data(data)