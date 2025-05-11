import datetime
import subprocess
import json
import os
from parsers.twogis.twogis_parser import TwoGisParser
from parsers.minzhkh.minzhkh_parser import MinzhkhParser

def load_addresses_from_file(filepath):
    """ Загрузка адресов из файла с адресами """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            out_addresses = file.read().splitlines()
            return out_addresses
    except FileNotFoundError as fe:
        print("❌ Ошибка, файл с адресами не найден!", fe)

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_2gis(addresses):
    # counter = {
    #     "build": 0,
    #     "orgs_in_build": 0,
    #     "parsed_build": 0,
    #     "parsed_orgs_in_build": 0,
    #     "saved_build_json": 0,
    #     "saved_orgs_in_build_json": 0,
    #
    #     "error_address_processing": 0,
    #     "error_intercept_network": 0,
    #     "error_not_found_build_id": 0,
    #
    #     "start_time": datetime.datetime.now().isoformat(),
    #     "end_time": 0
    # }

    parser = TwoGisParser(headless=False)  # headless=False для отладки

    for num, address in enumerate(addresses, start=1):
        print(f"\n🔍 Обрабатываем: {address} ({num}/{len(addresses)})")

        parser.run(address)
        build_data_raw = parser.get_build()
        orgs_data_raw = parser.get_organizations()

        # Пропуск если не нашли данные
        if not build_data_raw:
            print("❌ Здание не найдено.")
            continue

        # Сохраняем здание
        try:
            build_data = json.loads(build_data_raw)
            build_filename = f"data/output/buildings/build_{num}.json"
            save_json(build_data, build_filename)
            print(f"✅ Сохранено здание: {build_filename}")
        except Exception as e:
            print(f"⚠️ Ошибка при сохранении здания: {e}")

        # Сохраняем организации
        if orgs_data_raw:
            try:
                orgs_data = json.loads(orgs_data_raw)
                orgs_filename = f"data/output/organizations/orgs_{num}.json"
                save_json(orgs_data, orgs_filename)
                print(f"✅ Сохранены организации: {orgs_filename}")
            except Exception as e:
                print(f"⚠️ Ошибка при сохранении организаций: {e}")

    parser.close()
    print("\n🏁 Завершено.")

def parse_minzhkh(addresses):
    parser = MinzhkhParser()

    for num, address in enumerate(addresses, start=1):
        print(f"\n🔍 Обрабатываем: {address} ({num}/{len(addresses)})")

        parser.run(address)
        build_info = parser.get_build()

        # Пропуск если не нашли данные
        if not build_info:
            print("❌ Здание не найдено.")
            continue

        # Сохраняем здание
        try:
            build_data = json.loads(build_info)
            build_filename = f"data/output/minzhkh/build_{num}.json"
            save_json(build_data, build_filename)
            print(f"✅ Сохранено здание: {build_filename}")
        except Exception as e:
            print(f"⚠️ Ошибка при сохранении здания: {e}")

    parser.close()
    print("\n🏁 Завершено.")


if __name__ == "__main__":
    path_addresses = "other/test_addresses.txt"
    addresses = load_addresses_from_file(path_addresses)

    if addresses:
        parse_minzhkh(addresses)
    else:
        print("❌ Нет адресов для обработки.")