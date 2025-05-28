import json
import csv
from db_scripts.gets.get_builds_orgs_new import fetch_buildings_and_organizations

def export_data(path, fmt, filters=None):
    data = fetch_buildings_and_organizations(filters)

    if fmt == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    elif fmt == "csv":
        rows = []
        for b in data:
            row = {
                **b["address_info"],
                **b["build_info"],
                "organizations": json.dumps(b["organizations"], ensure_ascii=False)
            }
            rows.append(row)

        if rows:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    return len(data)
