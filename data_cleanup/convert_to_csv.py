import os
import json
import csv

# Пути к файлам
PROCESSED_JSON_PATH = "../data_cleanup/test_data/processed_data.json"
CSV_OUTPUT_DIR = "../data_cleanup/test_data/csv_exports"

# Создаем папку для CSV, если ее нет
os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)


def load_json(filepath):
    """ Загрузка JSON-файла """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def export_buildings_to_csv(data):
    """ Экспорт данных зданий в CSV """
    csv_file = os.path.join(CSV_OUTPUT_DIR, "buildings.csv")
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "address", "postcode", "district", "lat", "lon"])  # Заголовки

        for district, content in data.items():
            for building in content.get("buildings", []):
                writer.writerow([
                    building.get("id"),
                    building.get("name"),
                    building.get("address"),
                    building.get("postcode"),
                    building.get("district"),
                    building.get("lat"),
                    building.get("lon")
                ])
    print(f"✅ Buildings exported to {csv_file}")


def export_organizations_to_csv(data):
    """ Экспорт данных организаций в CSV """
    csv_file = os.path.join(CSV_OUTPUT_DIR, "organizations.csv")
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "category", "schedule", "lat", "lon"])  # Заголовки

        for district, content in data.items():
            for org in content.get("organizations", []):
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
    if not os.path.exists(PROCESSED_JSON_PATH):
        print(f"❌ Файл {PROCESSED_JSON_PATH} не найден!")
        return

    data = load_json(PROCESSED_JSON_PATH)
    export_buildings_to_csv(data)
    export_organizations_to_csv(data)
    print("✅ Экспорт завершен!")


if __name__ == "__main__":
    main()
