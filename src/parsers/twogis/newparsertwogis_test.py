import subprocess
import json
import os
from datetime import datetime
from urllib.parse import quote


class TwoGisCliParser:
    def __init__(self, output_dir="results", limit_restart=300):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.limit_restart = limit_restart
        self.restart_counter = 0
        self.stats = {
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "total": 0,
            "success": 0,
            "errors": 0
        }

    def run_cli(self, city: str, query: str, output_format: str = "json") -> list:
        """
        Запускает parser-2gis CLI и возвращает данные (список/словарь).
        """
        url = f"https://2gis.ru/{quote(city)}/search/{quote(query)}"
        outfile = os.path.join(self.output_dir, f"{quote(city)}_{quote(query)}.json")

        cmd = [
            "parser-2gis",
            "-i", url,
            "-o", outfile,
            "-f", output_format
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            with open(outfile, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.stats["success"] += 1
            return data
        except Exception as e:
            print(f"Ошибка при обработке {query}: {e}")
            self.stats["errors"] += 1
            return []

    def run(self, city: str, address: str):
        """
        Обрабатывает один адрес.
        """
        self.stats["total"] += 1
        result = self.run_cli(city, address)
        self.restart_counter += 1

        # Перезапуск через limit_restart (для долгих серий)
        if self.restart_counter >= self.limit_restart:
            self.restart_counter = 0
        return result

    def save_stats(self, filename="cli_stats.json"):
        """
        Сохраняет статистику в JSON.
        """
        self.stats["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    addresses = [
        "Иркутск, Ленина 15",
        "Иркутск, Лермонтова 83",
        "Иркутск, Советская 33"
    ]

    parser = TwoGisCliParser()
    for addr in addresses:
        data = parser.run("irkutsk", addr)
        print(f"Адрес: {addr}, найдено объектов: {len(data)}")

    parser.save_stats()
