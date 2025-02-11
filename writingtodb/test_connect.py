import psycopg2

# Функция для проверки подключения к базе данных
def connect_to_db():
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(dbname='geobase_db', 
                                user='postgres', 
                                password='postgres', 
                                host='localhost', 
                                port='5433')
      
        # Курсор для выполнения операций с базой данных
        cursor = connection.cursor()
        # Распечатать сведения о PostgreSQL
        print("Информация о сервере PostgreSQL")
        print(connection.get_dsn_parameters(), "\n")
        # Выполнение SQL-запроса
        cursor.execute("SELECT version();")
        # Получить результат
        record = cursor.fetchone()
        print("Есть соединение!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")

# Основной блок
if __name__ == "__main__":
    connect_to_db()
