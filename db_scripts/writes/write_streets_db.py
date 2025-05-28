import psycopg2
from psycopg2.extras import execute_batch
import json

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
JSON_FILE_PATH = f"../data/ginfo_extra/irkutsk_streets_{DISTRICT.lower()}.json"

def load_streets_from_json(filepath):
    """Читает JSON-файл со списком улиц"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Не удалось прочитать JSON: {e}")
        return []

def insert_streets(conn, data):
    """Вставка улиц в таблицу streets"""
    query = """
        INSERT INTO streets (name, type, district, city_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    try:
        with conn.cursor() as cur:
            execute_batch(
                cur,
                query,
                [(item["name"], item["type"], DISTRICT, DEFAULT_CITY_ID) for item in data]
            )
            conn.commit()
            print(f"Успешно вставлено {len(data)} записей.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке: {e}")

def main():
    conn = None
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        print("Подключение к PostgreSQL успешно.")

        # Загрузка данных из JSON
        streets_data = load_streets_from_json(JSON_FILE_PATH)

        # Вставка в базу
        insert_streets(conn, streets_data)

    except Exception as e:
        print(f"❌ Ошибка подключения или обработки: {e}")
    finally:
        if conn:
            conn.close()
            print("Соединение закрыто.")

if __name__ == "__main__":
    main()
