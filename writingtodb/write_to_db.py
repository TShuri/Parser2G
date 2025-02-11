import json
import psycopg2
import re

# Функция для вставки данных в таблицу
def insert_data_into_db(data):
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(dbname='geobase_test', 
                                user='postgres', 
                                password='postgres', 
                                host='localhost', 
                                port='5433')
        
        cursor = connection.cursor()


        # Вставка данных в таблицу address
        insert_address_query = """
            INSERT INTO address (district, address_name)
            VALUES (%s, %s)
            RETURNING id;
        """
        cursor.execute(insert_address_query, (data['district_name'], data['address_name']))

        # Получаем id вставленного адреса
        address_id = cursor.fetchone()[0]

        # Вставка данных в таблицу building
        insert_building_query = """
            INSERT INTO building (address_id, type, latitude, longitude)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_building_query, (
            address_id, 
            data['purpose_name'], 
            data['latitude'], 
            data['longitude']
        ))

        # Подтверждение изменений
        connection.commit()

        print("Данные успешно добавлены в базу данных.")

    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
    finally:
        # Закрытие подключения
        if connection:
            cursor.close()
            connection.close()


# Чтение JSON-файла
def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_data(data):
     # Адрес
    address_name = data["result"]["items"][0]["address_name"]

    # Район
    district_name = None
    for adm_div in data["result"]["items"][0]["adm_div"]:
        if adm_div["type"] == "district":
            district_name = adm_div["name"]
            break

    # Геометрия
    geometry = data["result"]["items"][0]["geometry"]["centroid"]

    # Использование регулярного выражения для извлечения чисел
    match = re.match(r"POINT\(([-\d.]+)\s([-\d.]+)\)", geometry)

    longitude = float(match.group(1))  # Долгота
    latitude = float(match.group(2))   # Широта

    # 4. Назначение
    purpose_name = data["result"]["items"][0]["purpose_name"]

    data = {
        'address_name': address_name,
        'district_name': district_name,
        'longitude': longitude,
        'latitude': latitude,
        'purpose_name': purpose_name
    }

    return data

if __name__ == "__main__":
    json_file_path = "building_1.json"
    data = read_json(json_file_path)
    clean_data = extract_data(data)
    insert_data_into_db(clean_data)