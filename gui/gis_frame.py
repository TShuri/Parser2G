import tkinter as tk

class GisFrame(tk.LabelFrame):
    def __init__(self, parent, log_func, parse_2gis_func):
        super().__init__(parent, text="2ГИС", padx=10, pady=10)
        self.log = log_func
        self.parse_2gis_func = parse_2gis_func

        tk.Button(self, text="🏬 Парсить здания (2ГИС)", command=self.run_2gis).pack(side="left", padx=5)

    def run_2gis(self):
        self.log("🔄 2ГИС: Запуск парсинга зданий...")
        try:
            self.parse_2gis_func()
            self.log("✅ Здания 2ГИС успешно спарсены.")
        except Exception as e:
            self.log(f"❌ Ошибка при парсинге 2ГИС: {e}")
