import json
import os
import concurrent.futures

from parsers.dadata.suggestion import DadataSuggestion
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

def parse_2gis(address, parser: TwoGisParser):
    build_data = None
    orgs_data = None

    parser.run(address)
    build_data_raw = parser.get_build()
    orgs_data_raw = parser.get_organizations()
    if build_data_raw is not None:
        build_data = json.loads(build_data_raw)
        if orgs_data_raw is not None:
            orgs_data = json.loads(orgs_data_raw)

    return build_data, orgs_data

def parse_minzhkh(address, parser: MinzhkhParser):
    parser.run(address)
    build_info = parser.get_build()
    return build_info

def parse_dadata(address, parser: DadataSuggestion):
    address_info = parser.process_address(address)
    return address_info

if __name__ == "__main__":
    path_addresses = "other/test_addresses.txt"
    addresses = load_addresses_from_file(path_addresses)

    dadata = DadataSuggestion()
    parserMinzhkh = MinzhkhParser()
    parserTwogis = TwoGisParser()

    for num, address in enumerate(addresses, start=1):
        print(f"\n🔍 Обрабатываем: {address} ({num}/{len(addresses)})")
        address_data = parse_dadata(address, dadata)
        address_value = dadata.get_value()
        address_city = dadata.get_city()
        address_street = dadata.get_name_street()
        address_house = dadata.get_house()

        # Запускаем два парсера в отдельных потоках
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_2gis = executor.submit(parse_2gis, address_value, parserTwogis)
            future_minzhkh = executor.submit(parse_minzhkh, address, parserMinzhkh)

            # Ждём, пока оба завершатся
            build_data, orgs_data = future_2gis.result()
            build_info = future_minzhkh.result()


