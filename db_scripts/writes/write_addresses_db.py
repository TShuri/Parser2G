import psycopg2
from psycopg2.extras import execute_batch
import json

from db_scripts.gets.get_streets_db import fetch_id_street

# Подключение к БД
DB_CONFIG = {
    "host": "localhost",
    "database": "urbdata",
    "user": "postgres",
    "password": "postgres",
    "port": "5433"
}

# Путь к JSON-файлу
DISTRICT = "Свердловский"
JSON_FILE_PATH = f"../data/ginfo_extra/irkutsk_houses_coords_{DISTRICT.lower()}.json"

def load_addresses_from_json(filepath):
    """Читает JSON-файл со списком адресов"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Не удалось прочитать JSON: {e}")
        return []

def insert_all_addresses(conn, data):
    """Вставка улиц в таблицу addresses"""
    query = """
        INSERT INTO addresses (street_id, house, full_address, lat, lon)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    try:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                query,
                [(fetch_id_street(name=item["street"], type=item["street_type"], district=DISTRICT),
                  item["house"], item["full_address"], item["lat"], item["lon"]) for item in data]
            )
            conn.commit()
            print(f"Успешно вставлено {len(data)} записей.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке: {e}")

def insert_address(item):
    query = """
            INSERT INTO addresses (street_id, house, full_address, lat, lon)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
    """

    street_id = fetch_id_street(name=item["street"], type=item["street_type"], district=DISTRICT)
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query, (street_id, item["house"], item["full_address"], item["lat"], item["lon"]))
        conn.commit()
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def main():
    try:
        # Загрузка данных из JSON
        addresses_data = load_addresses_from_json(JSON_FILE_PATH)

        for idx, item in enumerate(addresses_data, start=1):
            print(f"Обработка: {idx}/{len(addresses_data)}")
            insert_address(item)

    except Exception as e:
        print(f"Ошибка подключения или обработки: {e}")

if __name__ == "__main__":
    main()
