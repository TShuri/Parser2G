import tkinter as tk

class FiasFrame(tk.LabelFrame):
    def __init__(self, parent, log_func):
        super().__init__(parent, text="ФИАС", padx=10, pady=10)
        self.log = log_func
        self.parse_fias_func = None

        tk.Button(self, text="🏢 Парсить адреса ФИАС", command=self.run_fias).pack(side="left", padx=5)

    def run_fias(self):
        self.log("🔄 ФИАС: Запуск парсинга...")
        try:
            self.parse_fias_func()
            self.log("✅ Адреса ФИАС успешно спарсены.")
        except Exception as e:
            self.log(f"❌ Ошибка при парсинге ФИАС: {e}")
