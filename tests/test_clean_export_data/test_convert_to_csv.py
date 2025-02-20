import os
import json
import csv

# Пути к директориям
PROCESSED_DATA_DIR = "../test_clean_export_data/processed_data"  # Папка с обработанными данными
EXPORT_DATA_DIR = "../test_clean_export_data/export_data"  # Папка для экспорта CSV

# Создаем папку для экспорта, если ее нет
os.makedirs(EXPORT_DATA_DIR, exist_ok=True)


def load_json(filepath):
    """ Загрузка JSON-файла """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def export_buildings_to_csv(data, district):
    """ Экспорт данных зданий в CSV """
    csv_file = os.path.join(EXPORT_DATA_DIR, district, "buildings.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)  # Создаем папку для района

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "address", "postcode", "district", "lat", "lon"])  # Заголовки

        for building in data.get("buildings", []):
            writer.writerow([
                building.get("id"),
                building.get("name"),
                building.get("address"),
                building.get("postcode"),
                district,  # Используем название района
                building.get("lat"),
                building.get("lon")
            ])
    print(f"✅ Buildings exported to {csv_file}")


def export_organizations_to_csv(data, district):
    """ Экспорт данных организаций в CSV """
    csv_file = os.path.join(EXPORT_DATA_DIR, district, "organizations.csv")
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)  # Создаем папку для района

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "category", "schedule", "lat", "lon"])  # Заголовки

        for org in data.get("organizations", []):
            writer.writerow([
                org.get("id"),
                org.get("name"),
                ", ".join(org.get("category", [])),  # Категории через запятую
                org.get("schedule"),
                org.get("lat"),
                org.get("lon")
            ])
    print(f"✅ Organizations exported to {csv_file}")


def main():
    """ Главная функция для экспорта JSON в CSV """
    # Проход по районам
    for district in os.listdir(PROCESSED_DATA_DIR):
        district_path = os.path.join(PROCESSED_DATA_DIR, district)
        json_path = os.path.join(district_path, "processed_data.json")

        if os.path.isdir(district_path) and os.path.exists(json_path):
            data = load_json(json_path)
            export_buildings_to_csv(data, district)
            export_organizations_to_csv(data, district)
        else:
            print(f"❌ Файл {json_path} не найден!")

    print("✅ Экспорт завершен!")


if __name__ == "__main__":
    main()
