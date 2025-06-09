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

def fetch_buildings_and_organizations(filters=None):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = """
        SELECT  
            a.id as address_id,
            a.full_address AS address_full,
            a.lat AS lat,
            a.lon AS lon,
            a.house AS house,
            s.name AS street_name,
            s.type AS street_type,
            s.district AS district,
            c.name AS city_name,
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
        JOIN cities c ON s.city_id = c.id
    """

    conditions = []
    params = []

    if filters:
        if "city" in filters:
            conditions.append("c.name = %s")
            params.append(filters["city"])
        if "district" in filters:
            conditions.append("s.district = %s")
            params.append(filters["district"])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cur.execute(query, params)
    buildings_raw = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    buildings = {}

    for row in buildings_raw:
        row_dict = dict(zip(columns, row))
        building_id = row_dict["build_id"]
        buildings[building_id] = buildings.get(building_id, {
            "address_info": {
                "address_id": row_dict["address_id"],
                "address_full": row_dict["address_full"],
                "lat": row_dict["lat"],
                "lon": row_dict["lon"],
                "house": row_dict["house"],
                "street_name": row_dict["street_name"],
                "street_type": row_dict["street_type"],
                "district": row_dict["district"],
                "city_name": row_dict["city_name"],
            },
            "build_info": {},
            "organizations": []
        })
        # Заполняем build_info, можно обновлять, если нужно
        buildings[building_id]["build_info"] = {
            k: row_dict[k] for k in row_dict if k not in buildings[building_id]["address_info"]
        }

    # Получаем организации для выбранных зданий
    building_ids = list(buildings.keys())
    if building_ids:
        format_ids = ','.join(['%s'] * len(building_ids))
        cur.execute(f"""
            SELECT
                o.id,
                o.build_id,
                o.name,
                o.primary_rubric_id,
                r.name AS primary_rubric_name,
                o.general_rating,
                o.general_review_count,
                o.general_review_count_with_stars,
                o.poi_category,
                o.lat,
                o.lon,
                o.schedule
            FROM organizations o
            LEFT JOIN rubrics r ON o.primary_rubric_id = r.id
            WHERE o.build_id IN ({format_ids})
        """, building_ids)

        org_rows = cur.fetchall()
        org_columns = [desc[0] for desc in cur.description]

        for row in org_rows:
            org_data = dict(zip(org_columns, row))
            build_id = org_data["build_id"]
            if build_id in buildings:
                buildings[build_id]["organizations"].append(org_data)

    cur.close()
    conn.close()
    return list(buildings.values())
