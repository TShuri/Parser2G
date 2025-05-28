import psycopg2
import os

from dotenv import load_dotenv

try:
    # пытаемся подключиться к базе данных
    # Конфиг подключения к БД
    # DB_CONFIG = {
    #     "host": "localhost",
    #     "database": "urbdata",
    #     "user": "postgres",
    #     "password": "postgres",
    #     "port": "5433"
    # }
    load_dotenv()
    print(os.getenv("DB_NAME"))
    print(os.getenv("DB_USER"))
    print(os.getenv("DB_PASSWORD"))
    print(os.getenv("DB_HOST"))
    print(os.getenv("DB_PORT"))

    DB_CONFIG = {
        'dbname': os.getenv("DB_NAME"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'host': os.getenv("DB_HOST"),
        'port': os.getenv("DB_PORT")
    }

    conn = psycopg2.connect(**DB_CONFIG)
    print('Successfully connect')
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')