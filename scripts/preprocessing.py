import os
import json

RAW_DIR = "raw_data"
OUT_FILE = "data/combined_data.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_address(address_raw):
    return {
        "value": address_raw.get("value"),
        "unrestricted_value": address_raw.get("unrestricted_value"),
        "postal_code": address_raw.get("data").get("postal_code"),
        "federal_district": address_raw.get("data").get("federal_district"),
        "region_type_full": address_raw.get("data").get("region_type_full"),
        "region": address_raw.get("data").get("region"),
        "city_type_full": address_raw.get("data").get("city_type_full"),
        "city": address_raw.get("data").get("city"),
        "settlement_type_full": address_raw.get("data").get("settlement_type_full"),
        "settlement": address_raw.get("data").get("settlement"),
        "street_type_full": address_raw.get("data").get("street_type_full"),
        "street": address_raw.get("data").get("street"),
        "stead_type_full": address_raw.get("data").get("stead_type_full"),
        "stead": address_raw.get("data").get("stead"),
        "house_type_full": address_raw.get("data").get("house_type_full"),
        "house": address_raw.get("data").get("street"),
        "lat": address_raw.get("data").get("geo_lat"),
        "lon": address_raw.get("data").get("geo_lon")
    }

def extract_build_data(build_raw):
    """ Извлечение данных о здании """
    building_info = build_raw.get("result", {}).get("items", [{}])[0]
    return {
        "id": building_info.get("address", {}).get("building_id"),
        "postcode": building_info.get("address", {}).get("postcode"),
        "address_name": building_info.get("address_name"),
        "district": next((adm["name"] for adm in building_info.get("adm_div", []) if adm["type"] == "district"), None),
        "lat": building_info.get("point", {}).get("lat"),
        "lon": building_info.get("point", {}).get("lon"),
        "building_name": building_info.get("building_name"),
        "full_name": building_info.get("full_name"),
        "purpose_code": building_info.get("purpose_code"),
        "purpose_name": building_info.get("purpose_name"),
        "floors_ground": building_info.get("floors", {}).get("ground_count"),
        "entity_count": sum(1 for e in building_info.get("links", {}).get("database_entrances", []) if e.get("entity_number")),
        "nearest_stations_name": building_info.get("links", {}).get("nearest_stations", [{}])[0].get("name"),
        "nearest_stations_distance": building_info.get("links", {}).get("nearest_stations", [{}])[0].get("distance"),
        "branches": building_info.get("links", {}).get("branches", {}).get("count"),
        "servicing": building_info.get("links", {}).get("servicing", {}).get("count"),
        "providers": building_info.get("links", {}).get("providers", {}).get("count"),
        "general_rating": building_info.get("reviews", {}).get("general_rating"),
        "general_review_count": building_info.get("reviews", {}).get("general_review_count"),
        "general_review_count_with_stars": building_info.get("reviews", {}).get("general_review_count_with_stars"),
        "type": building_info.get("type"),
        "elevators_count": building_info.get("structure_info", {}).get("elevators_count"),
        "gas_type": building_info.get("structure_info", {}).get("gas_type"),
        "material": building_info.get("structure_info", {}).get("material"),
        "year_of_construction": building_info.get("structure_info", {}).get("year_of_construction"),
        "schedule": building_info.get("schedule")
    }

def extract_orgs_data(orgs_raw):
    orgs = []
    for org in orgs_raw.get("result", {}).get("items", []):
        orgs.append({
            "id": org.get("org", {}).get("id"),
            "name": org.get("name"),
            "name_ex": org.get("name_ex", {}).get("primary"),
            "rubric_primary": next((rubric["name"] for rubric in org.get("rubrics", []) if rubric["kind"] == "primary"), None),
            "rubric_id_primary": next((rubric["id"] for rubric in org.get("rubrics", []) if rubric["kind"] == "primary"), None),
            "rubrics": [rubric.get("name") for rubric in org.get("rubrics", [])],
            "rubrics_id": [rubric.get("id") for rubric in org.get("rubrics", [])],
            "general_rating": org.get("reviews", {}).get("general_rating"),
            "general_review_count": org.get("reviews", {}).get("general_review_count"),
            "general_review_count_with_stars": org.get("reviews", {}).get("general_review_count_with_stars"),
            "poi_category": org.get("poi_category"),
            "type": org.get("type"),
            "lat": org.get("point", {}).get("lat"),
            "lon": org.get("point", {}).get("lon"),
            "schedule": org.get("schedule"),
        })
    return orgs

def extract_minzhkh(minzhkh_raw):
    pass

def preprocess(address_raw=None, build_raw=None, orgs_raw=None, minzhkh_raw=None):
    if address_raw is None and build_raw is None and orgs_raw is None and minzhkh_raw is None:
        return None
    data = {}
    if address_raw:
        data["address"] = extract_address(address_raw)
    if build_raw:
        data["build"] = extract_build_data(build_raw)
    if minzhkh_raw:
        data["minzhkh"] = minzhkh_raw
    if orgs_raw:
        data["orgs"] = extract_orgs_data(orgs_raw)

    return data


if __name__ == "__main__":
    input_file_build = "../data/output/buildings/build_2.json"
    input_file_orgs = "../data/output/organizations/orgs_2.json"
    input_file_minzhkh = "../data/output/minzhkh/build_2.json"
    output_file = "../data/preprocessing/extract_build.json"

    build_file = load_json(input_file_build)
    orgs_file = load_json(input_file_orgs)
    minzhkh_file = load_json(input_file_minzhkh)
    build_data = preprocess(build_raw=build_file, orgs_raw=orgs_file, minzhkh_raw=minzhkh_file)

    with open(output_file, "w", encoding="utf-8") as out_f:
        json.dump(build_data, out_f, ensure_ascii=False, indent=2)