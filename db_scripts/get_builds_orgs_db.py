import psycopg2
import json
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
def fetch_buildings_and_organizations():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Получаем здания с адресами
    cur.execute("""
            SELECT  
                a.id as address_id,
                a.full_address AS address_full,
                a.lat AS lat,
                a.lon AS lon,
                a.house AS house,
                s.name AS street_name,
                s.type AS street_type,
                s.district AS district,
                b.id as build_id,
                b.build_name,
                b.full_name,
                b.type_build,
                b.purpose_code,
                b.purpose_name,
                b.floors_ground,
                b.entity_count,
                b.elevators_count,
                b.services,
                b.providers,
                b.year_of_construction,
                b.material,
                b.general_rating,
                b.general_review_count,
                b.general_review_with_stars,
                b.nearest_stations_name,
                b.nearest_stations_distance
            FROM buildings b
            JOIN addresses a ON b.address_id = a.id
            JOIN streets s ON a.street_id = s.id
        """)
    buildings_raw = cur.fetchall()

    # Преобразование в словарь
    address_keys = [
        "address_id",
        "address_full",
        "lat",
        "lon",
        "house",
        "street_name",
        "street_type",
        "district",
    ]

    columns = [desc[0] for desc in cur.description]
    buildings = {}

    for row in buildings_raw:
        row_dict = dict(zip(columns, row))
        building_id = row_dict["build_id"]

        buildings[building_id] = {
            "address_info": {k: row_dict[k] for k in address_keys},
            "build_info": {k: row_dict[k] for k in columns if k not in address_keys},
            "organizations": []
        }

    # Получаем организации с привязкой к зданиям
    cur.execute("""
        SELECT
            o.id,
            o.build_id AS build_id,
            o.name,
            o.primary_rubric_id,
            r.name AS primary_rubric_name,
            o.general_rating,
            o.general_review_count,
            o.general_review_count_with_stars,
            o.poi_category,
            o.type
        FROM organizations o
        JOIN buildings b ON o.build_id = b.id
        LEFT JOIN rubrics r ON o.primary_rubric_id = r.id
    """)

    org_rows = cur.fetchall()
    org_columns = [desc[0] for desc in cur.description]

    organizations = []
    for row in org_rows:
        org_data = dict(zip(org_columns, row))
        organizations.append(org_data)

    for org_data in organizations:
        building_id = org_data["build_id"]
        if building_id in buildings:
            buildings[building_id]["organizations"].append(org_data)

    cur.close()
    conn.close()

    return list(buildings.values())


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    merged_data = fetch_buildings_and_organizations()
    save_to_json(merged_data, "../data/buildings_with_organizations.json")
    print("✅ Объединённые данные сохранены в buildings_with_organizations.json")
