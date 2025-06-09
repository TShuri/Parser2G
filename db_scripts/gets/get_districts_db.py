import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT")
}

def get_districts_for_city(city_name):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    query = """
        SELECT DISTINCT s.district
        FROM streets s
        JOIN cities c ON s.city_id = c.id
        WHERE c.name = %s
        ORDER BY s.district
    """
    cur.execute(query, (city_name,))
    districts = [row[0] for row in cur.fetchall() if row[0]]
    cur.close()
    conn.close()
    return districts
