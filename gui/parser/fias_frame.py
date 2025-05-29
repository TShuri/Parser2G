import threading
import tkinter as tk

from scripts.parse_2gis import get_build_orgs
from parsers.fias.get_streets import get_streets
from parsers.fias.get_houses_street import get_addresses


class FiasFrame(tk.LabelFrame):
    def __init__(self, parent, log_func):
        super().__init__(parent, text="ФИАС", padx=10, pady=10)
        self.log = log_func
        self.get_streets_func = get_streets
        self.parse_addresses_func = get_addresses

        self.streets = []
        self.addresses = []

        input_frame = tk.Frame(self)
        input_frame.pack(fill="x", pady=(0, 10))

        tk.Label(input_frame, text="🔗 Ссылка:").pack(side="left", padx=5)
        self.url_entry = tk.Entry(input_frame, width=60)
        self.url_entry.pack(side="left", padx=10, fill="x", expand=True)

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(fill="x")

        self.streets_button = tk.Button(self, text="📍 Получить улицы", command=self.run_streets)
        self.streets_button.pack(side="left", padx=5)

        self.addresses_button = tk.Button(self, text="🏠 Получить адреса", command=self.run_addresses, state="disabled")
        self.addresses_button.pack(side="left", padx=5)

        self.build_orgs_button = tk.Button(self, text="🏢 Парсинг зданий и организаций", state="disabled")
        self.build_orgs_button.pack(side="left", padx=5)

    def run_streets(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("⚠️ Пожалуйста, введите ссылку из Fias-alta.")
            return
        self.log(f"🔄 GINFO: Запуск парсинга улиц: ")

        def task():
            try:
                self.streets = self.get_streets_func(log_func=self.log, url=url)
                self.log(f"✅ Парсинг завершён. Найдено улиц: {len(self.streets)}")
                self.log(f"✅ {len(self.streets)} улиц записано в базу данных")
                self.addresses_button.config(state="normal")
            except Exception as e:
                self.log(f"❌ Ошибка при парсинге улиц: {e}")

        threading.Thread(target=task, daemon=True).start()

    def run_addresses(self):
        self.log(f"🔄 GINFO: Запуск парсинга адресов: ")

        def task():
            try:
                if self.parse_addresses_func:
                    self.addresses = get_addresses(streets=self.streets, log_func=self.log)
                    self.log(f"✅ Парсинг завершён. Найдено адресов: {len(self.addresses)}")
                    self.log(f"✅ {len(self.addresses)} адресов записано в базу данных")
                    self.build_orgs_button.config(state="normal")
                else:
                    self.log("⚠️ Функция парсинга адресов не задана.")
            except Exception as e:
                self.log(f"❌ Ошибка при парсинге адресов: {e}")

        threading.Thread(target=task, daemon=True).start()

    def run_builds_orgs(self):
        def task():
            try:
                get_build_orgs(self.log)
                self.log(f"✅ Парсинг завершён")

            except Exception as e:
                self.log(f"❌ Ошибка при парсинге зданий и организаций: {e}")

        threading.Thread(target=task, daemon=True).start()
