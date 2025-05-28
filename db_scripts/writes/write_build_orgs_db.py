import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json

# Конфиг подключения к БД
load_dotenv()
DB_CONFIG = {
    'dbname': os.getenv("DB_NAME"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT")
}

def check_keys_build(build):
    REQUIRED_KEYS = [
        "id", "address_id", "building_name", "full_name", "type", "purpose_code", "purpose_name",
        "floors_ground", "entity_count", "elevators_count", "servicing", "providers",
        "year_of_construction", "material", "general_rating", "general_review_count",
        "general_review_count_with_stars", "nearest_stations_name", "nearest_stations_distance", "schedule"
    ]

    for key in REQUIRED_KEYS:
        build.setdefault(key, None)

    return build

def check_keys_org(org):
    REQUIRED_KEYS = [
        "name", "primary_rubric_id", "general_rating", "general_review_count",
        "general_review_count_with_stars", "poi_category", "type", "lat", "lon", "schedule"
    ]

    for key in REQUIRED_KEYS:
        org.setdefault(key, None)

    return org

def update_coords_address(cur, build):
    cur.execute("""
        UPDATE addresses
            SET lat = %(lat)s, lon = %(lon)s
            WHERE id = %(address_id)s
    """, build)

def insert_building(cur, build):
    params = dict(build)
    params['schedule'] = Json(params['schedule'])
    cur.execute("""
        INSERT INTO buildings (
            address_id, build_name, full_name, type_build, purpose_code, purpose_name,
            floors_ground, entity_count, elevators_count, services, providers,
            year_of_construction, material, general_rating, general_review_count,
            general_review_with_stars, nearest_stations_name, nearest_stations_distance, schedule
        ) VALUES (
            %(address_id)s, %(building_name)s, %(full_name)s, %(type)s, %(purpose_code)s, %(purpose_name)s,
            %(floors_ground)s, %(entity_count)s, %(elevators_count)s, %(servicing)s, %(providers)s,
            %(year_of_construction)s, %(material)s, %(general_rating)s, %(general_review_count)s,
            %(general_review_count_with_stars)s, %(nearest_stations_name)s, %(nearest_stations_distance)s, %(schedule)s
        )
        ON CONFLICT (address_id) DO NOTHING
        RETURNING id
    """, params)
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        # Получаем id уже существующего здания по address_id
        cur.execute("SELECT id FROM buildings WHERE address_id = %s", (build['address_id'],))
        return cur.fetchone()[0]

def insert_rubrics(cur, rubric_ids, rubric_names):
    for rubric_id, rubric_name in zip(rubric_ids, rubric_names):
        cur.execute("""
            INSERT INTO rubrics (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (rubric_id, rubric_name))

def insert_organization(cur, org):
    params = dict(org)
    params['schedule'] = Json(params['schedule'])
    cur.execute("""
        INSERT INTO organizations (
            name, primary_rubric_id, general_rating, general_review_count,
            general_review_count_with_stars, poi_category, type, lat, lon, build_id, schedule
        ) VALUES (
            %(name)s, %(rubric_id_primary)s, %(general_rating)s, %(general_review_count)s,
            %(general_review_count_with_stars)s, %(poi_category)s, %(type)s, %(lat)s, %(lon)s, %(build_id)s, %(schedule)s
        )
        RETURNING id
    """, params)
    return cur.fetchone()[0]

def insert_organization_rubrics(cur, org_id, rubrics_id):
    for rubric_id in rubrics_id:
        cur.execute("""
            INSERT INTO organizations_rubrics (organization_id, rubric_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (org_id, rubric_id))

def save_data_to_db(data):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    save = False
    try:
        build_id = None

        # 1. Вставляем здание
        if data.get('build'):
            build = check_keys_build(data['build'])
            update_coords_address(cur, build)
            build_id = insert_building(cur, build)

        # 2. Вставляем организации и их рубрики
        if data.get('orgs') and (build_id is not None):
            for org_d in data['orgs']:
                org = check_keys_org(org_d)
                org["build_id"] = build_id
                if org.get('rubrics_id') and org.get('rubrics'):
                    insert_rubrics(cur, org['rubrics_id'], org['rubrics'])
                org_id = insert_organization(cur, org)
                if org_id and org.get('rubrics_id'):
                    insert_organization_rubrics(cur, org_id, org['rubrics_id'])

        conn.commit()
        print("Data saved in DataBase successfully")
        save = True
    except Exception as e:
        conn.rollback()
        print("Error saved to DataBase:", e)
    finally:
        cur.close()
        conn.close()
        return save

if __name__ == "__main__":
    pass