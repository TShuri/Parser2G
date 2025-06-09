import psycopg2

# Данные для подключения
DB_CONFIG = {
    "host": "localhost",
    "database": "urbdata",
    "user": "postgres",
    "password": "postgres",
    "port": "5433"
}

def fetch_id_street(name, type, district):
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Выполняем SELECT-запрос
        street_name = name
        street_type = type
        district_name = district

        cursor.execute("""
            SELECT id
            FROM streets 
            WHERE name = %s AND type = %s AND district = %s;
        """, (street_name, street_type, district_name))

        answer = cursor.fetchone()

    except Exception as e:
        print("Ошибка при выполнении запроса:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()
            # print("Соединение закрыто")
        return answer[0]

def fetch_all_streets(district):
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Выполняем SELECT-запрос
        district_name = district
        cursor.execute("SELECT id, name, type, district FROM streets WHERE district = %s ORDER BY name;",
                       (district_name,))

        answer = cursor.fetchall()

    except Exception as e:
        print("Ошибка при выполнении запроса:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()
            # print("Соединение закрыто")
        return answer

if __name__ == "__main__":
    streets = fetch_all_streets("Октябрьский")
    print(streets)
    #id = fetch_id_street(name="Березка", type="СНТ", district="Свердловский")
    #print(id)
