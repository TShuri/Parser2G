import psycopg2

# Подключение к БД
DB_CONFIG = {
    "host": "localhost",
    "database": "urbdata",
    "user": "postgres",
    "password": "postgres",
    "port": "5433"
}


def get_addresses_by_district(district):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.full_address
            FROM addresses a
            JOIN streets s ON a.street_id = s.id
            WHERE s.district = %s
            ORDER BY a.id;
        """, (district,))

        addresses = cursor.fetchall()
        return addresses
    except Exception as e:
        print("Ошибка при выполнении запроса:", e)
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()


def main():
    district_name = "Свердловский"
    addresses = get_addresses_by_district(district_name)
    for idx, address in enumerate(addresses, start=1):
        print(f"{idx}: {address} ")

if __name__ == "__main__":
    main()
