import datetime
import subprocess

def load_addresses_from_file(filepath):
    """ Загрузка адресов из файла с адресами """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            out_addresses = file.read().splitlines()
            return out_addresses
    except FileNotFoundError as fe:
        print("❌ Ошибка, файл с адресами не найден!", fe)

def parse_2gis(addresses, script_path):
    counter = {
        "build": 0,
        "orgs_in_build": 0,
        "parsed_build": 0,
        "parsed_orgs_in_build": 0,
        "saved_build_json": 0,
        "saved_orgs_in_build_json": 0,

        "error_address_processing": 0,
        "error_intercept_network": 0,
        "error_not_found_build_id": 0,

        "start_time": datetime.datetime.now().isoformat(),
        "end_time": 0
    }

    try:
        count_addresses = len(addresses)
        for num, address in enumerate(addresses, start=1):
            print(f"\n🔍 Обрабатываем: {address} ({num}/{count_addresses})")

            # Вызов скрипта с передачей адреса
            result = subprocess.run(
                ["python", script_path, address],  # Укажи правильное имя скрипта
                capture_output=True,
                text=True
            )

            # Вывод результатов
            print(result.stdout)
            if result.stderr:
                print(f"⚠️ Ошибка:\n{result.stderr}")

    except Exception as e:
        print(f"❌ Ошибка выполнения парсера: {e}")


if __name__ == "__main__":
    # Путь к файлу с адресами
    # file_addresses = "/data_raw/osm/addresses_districts/октябрьский административный округ.txt"
    file_addresses = "other/test_addresses.txt"
    addresses = load_addresses_from_file(file_addresses)

    # Путь к скрипту
    script_path = "parsers/2gis/2gis_parser.py"
    parse_2gis(addresses, script_path)

