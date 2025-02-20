import os
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Пути к директориям
RAW_DATA_DIR = "../data_raw/2gis"  # Папка с необработанными данными
PROCESSED_DATA_DIR = "../data_clean/processed_data"  # Папка куда сохраняются обработанные данные


def load_json(filepath):
    """ Загрузка JSON-файла """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка чтения {filepath}: {e}")
        return None


def extract_building_data(raw_data):
    """ Извлечение данных о здании """
    building_info = raw_data.get("result", {}).get("items", [{}])[0]
    return {
        "id": building_info.get("address", {}).get("building_id"),
        "name": building_info.get("address", {}).get("building_name"),
        "address": building_info.get("address_name"),
        "postcode": building_info.get("address", {}).get("postcode"),
        "district": next((adm["name"] for adm in building_info.get("adm_div", []) if adm["type"] == "district"), None),
        "lat": building_info.get("point", {}).get("lat"),
        "lon": building_info.get("point", {}).get("lon"),
    }


def extract_orgs_data(raw_data):
    """ Извлечение списка организаций в здании """
    orgs = []
    for org in raw_data.get("result", {}).get("items", []):
        orgs.append({
            "id": org.get("org", {}).get("id"),
            "name": org.get("name_ex", {}).get("primary"),
            "branch_count": org.get("org", {}).get("branch_count"),
            "category": [rubric.get("name") for rubric in org.get("rubrics", [])],
            "schedule": org.get("schedule"),
            "lat": org.get("point", {}).get("lat"),
            "lon": org.get("point", {}).get("lon"),
        })
    return orgs


def process_district(district):
    """ Обработка всех зданий и организации в районе """
    district_raw_path = os.path.join(RAW_DATA_DIR, district)
    district_processed_path = os.path.join(PROCESSED_DATA_DIR, district)

    # Создаются папки, если их нет
    os.makedirs(os.path.join(district_processed_path, "buildings"), exist_ok=True)
    os.makedirs(os.path.join(district_processed_path, "organizations"), exist_ok=True)

    buildings_json_path = os.path.join(district_raw_path, "builds_json")
    orgs_json_path = os.path.join(district_raw_path, "orgs_in_builds_json")

    all_buildings = []

    # Проход по файлам зданий
    for filename in os.listdir(buildings_json_path):
        file_path = os.path.join(buildings_json_path, filename)
        raw_data = load_json(file_path)
        if not raw_data:
            continue

        # Обрабатываем данные о здании
        building_data = extract_building_data(raw_data)
        all_buildings.append(building_data)

        # Сохранение очищенного JSON для здания
        output_file = os.path.join(district_processed_path, "buildings", filename)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(building_data, f, ensure_ascii=False, indent=4)

    all_organizations = []

    # Проход по файлам организаций
    for filename in os.listdir(orgs_json_path):
        file_path = os.path.join(orgs_json_path, filename)
        raw_data = load_json(file_path)
        if not raw_data:
            continue

        # Обрабатываем организации
        orgs_data = extract_orgs_data(raw_data)
        all_organizations.extend(orgs_data)

        # Сохранение очищенного JSON для организаций
        output_file = os.path.join(district_processed_path, "organizations", filename)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(orgs_data, f, ensure_ascii=False, indent=4)

    # Сохранение общего JSON с очищенными данными для района
    output_json = os.path.join(district_processed_path, "processed_data.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "buildings": all_buildings,
            "organizations": all_organizations,
        }, f, ensure_ascii=False, indent=4)

    logging.info(f"✅ Данные для района {district} обработаны и сохранены в {output_json}")

    return all_buildings, all_organizations


def main():
    """ Основная функция обработки всех районов """
    # Проход по районам
    for district in os.listdir(RAW_DATA_DIR):
        district_path = os.path.join(RAW_DATA_DIR, district)
        if not os.path.isdir(district_path):
            continue  # Пропускаем файлы, если вдруг они есть

        logging.info(f"Обрабатываем район: {district}")
        process_district(district)


if __name__ == "__main__":
    main()
