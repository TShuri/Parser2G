import threading
import tkinter as tk
from parsers.ginfo.get_districts import get_districts
from parsers.ginfo.get_streets_district import get_street_links

class GinfoFrame(tk.LabelFrame):
    def __init__(self, parent, log_func):
        super().__init__(parent, text="GINFO (Для агломерации Иркутска)", padx=10, pady=10)
        self.log = log_func
        self.get_districts_func = get_districts

        self.parse_streets_func = get_street_links
        self.parse_addresses_func = None

        self.districts = []  # список районов после получения
        self.selected_district = tk.StringVar()
        self.selected_district.set("Выберите округ")
        self.url_selected_district = ''  # тут будет url выбранного района

        # Кнопка получить районы
        tk.Button(self, text="🗺️ Получить округи", command=self.run_districts).pack(side="left", padx=5)

        # Выпадающий список для выбора района
        self.district_menu = tk.OptionMenu(self, self.selected_district, ())
        self.district_menu.pack(side="left", padx=5)

        # Кнопки парсинга улиц и адресов
        tk.Button(self, text="📍 Получить улицы", command=self.run_streets).pack(side="left", padx=5)
        tk.Button(self, text="🏠 Получить адреса", command=self.run_addresses).pack(side="left", padx=5)

    def run_districts(self):
        self.log("🔄 GINFO: Получение округов города...")

        def task():
            try:
                self.districts = self.get_districts_func()

                # Обновление меню — нужно делать в основном потоке UI!
                def update_menu():
                    menu = self.district_menu["menu"]
                    menu.delete(0, "end")
                    self._district_name_to_url = {}

                    for district in self.districts:
                        name = district['name']
                        url = district.get('url', '')
                        self._district_name_to_url[name] = url

                        menu.add_command(
                            label=name,
                            command=lambda n=name: self._on_district_selected(n)
                        )

                    if self.districts:
                        first_name = self.districts[0]['name']
                        self.selected_district.set(first_name)
                        self.url_selected_district = self._district_name_to_url.get(first_name, '')

                    for district in self.districts:
                        self.log(f"{district['name']}")

                    self.log(f"✅ Найдено округов: {len(self.districts)}")

                # В Tkinter обновлять UI из другого потока нельзя — используем after
                self.district_menu.after(0, update_menu)

            except Exception as e:
                self.log(f"❌ Ошибка при получении округов: {e}")

        threading.Thread(target=task, daemon=True).start()

    def _on_district_selected(self, name):
        self.selected_district.set(name)
        self.url_selected_district = self._district_name_to_url.get(name, '')
        self.log(f"ℹ️ Выбран округ: {name}, url: {self.url_selected_district}")

    def run_streets(self):
        district = self.selected_district.get()
        if district == "Выберите округ":
            self.log("⚠️ Пожалуйста, выберите округ перед парсингом улиц.")
            return
        self.log(f"🔄 GINFO: Запуск парсинга улиц района: {district} (URL: {self.url_selected_district})...")

        def task():
            try:
                if self.parse_streets_func:
                    streets = self.parse_streets_func(self.url_selected_district, self.log)
                    self.log(f"✅ Парсинг завершён. Найдено улиц: {len(streets)}")
                    self.log(f"✅ {len(streets)} улиц записано в базу данных")
                    # Здесь можно обновить UI, например, показать улицы
                else:
                    self.log("⚠️ Функция парсинга улиц не задана.")
            except Exception as e:
                self.log(f"❌ Ошибка при парсинге улиц: {e}")

        threading.Thread(target=task, daemon=True).start()

    def run_addresses(self):
        district = self.selected_district.get()
        if district == "Выберите район":
            self.log("⚠️ Пожалуйста, выберите район перед парсингом адресов.")
            return
        self.log(f"🔄 GINFO: Запуск парсинга адресов района: {district} (URL: {self.url_selected_district})...")
        try:
            if self.parse_addresses_func:
                self.parse_addresses_func(self.url_selected_district)
                self.log("✅ Адреса GINFO успешно спарсены.")
            else:
                self.log("⚠️ Функция парсинга адресов не задана.")
        except Exception as e:
            self.log(f"❌ Ошибка при парсинге адресов: {e}")
