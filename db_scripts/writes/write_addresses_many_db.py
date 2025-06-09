import psycopg2
from psycopg2.extras import execute_values
import json
from db_scripts.gets.get_streets_db import fetch_all_streets

# Подключение к БД
DB_CONFIG = {
    "host": "localhost",
    "database": "urbdata",
    "user": "postgres",
    "password": "postgres",
    "port": "5433"
}

# ID города по умолчанию (поставь актуальный)
DEFAULT_CITY_ID = 1

# Путь к JSON-файлу
DISTRICT = "Октябрьский"
JSON_FILE_PATH = f"../data/ginfo_extra/irkutsk_houses_coords_{DISTRICT.lower()}.json"

def load_addresses_from_json(filepath):
    """Читает JSON-файл со списком адресов"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Не удалось прочитать JSON: {e}")
        return []

def insert_addresses_batch(cur, address_list, street_id):
    values = [
        (
            addr.get("full_address"),
            addr.get("lat"),
            addr.get("lon"),
            addr.get("house"),
            street_id
        )
        for addr in address_list
    ]

    query = """
        INSERT INTO addresses (full_address, lat, lon, house, street_id)
        VALUES %s
        RETURNING id
    """

    execute_values(cur, query, values)

def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        addresses_data = load_addresses_from_json(JSON_FILE_PATH)
        streets = fetch_all_streets(DISTRICT)

        for idx, item in enumerate(streets, start=1):
            obj_street = {
                "id": item[0],
                "name": item[1],
                "type": item[2]
            }

            matching_addresses = [
                addr for addr in addresses_data
                if addr.get("street") == obj_street["name"]
                   and addr.get("street_type") == obj_street["type"]
            ]

            print(f"id_street({obj_street['id']}): {obj_street['type']} {obj_street['name']} — найдено {len(matching_addresses)} адресов")

            if matching_addresses:
                insert_addresses_batch(cur, matching_addresses, obj_street["id"])
                print(f"  ✅ Вставлено {len(matching_addresses)} адресов")

        conn.commit()

    except Exception as e:
        print(f"Ошибка подключения или обработки: {e}")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
