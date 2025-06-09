import tkinter as tk
from tkinter import scrolledtext
from gui.parser.ginfo_frame import GinfoFrame
from gui.parser.fias_frame import FiasFrame


def run_in_thread(func):
    import threading
    def wrapper():
        threading.Thread(target=func).start()
    return wrapper

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсинг данных")
        self.root.geometry("800x600")

        # Выбор источника адресов
        self.source_var = tk.StringVar(value="GINFO")  # По умолчанию выбрано GINFO

        self.radio_frame = tk.Frame(root)
        self.radio_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Размещение в первой строке

        self.ginfo_checkbox = tk.Radiobutton(self.radio_frame, text="GINFO", variable=self.source_var, value="GINFO", command=self.update_source)
        self.ginfo_checkbox.pack(side="left", padx=5)

        self.fias_checkbox = tk.Radiobutton(self.radio_frame, text="ФИАС", variable=self.source_var, value="FIAS", command=self.update_source)
        self.fias_checkbox.pack(side="left", padx=5)

        # Контейнер для рамок (GinfoFrame и FiasFrame)
        self.frames_container = tk.Frame(root)
        self.frames_container.grid(row=1, column=0, padx=10, pady=5, sticky="ew")  # Размещение во второй строке

        # Рамки
        self.ginfo_frame = GinfoFrame(self.frames_container, self.log)
        self.fias_frame = FiasFrame(self.frames_container, self.log)

        # Изначально показываем только GINFO
        self.ginfo_frame.pack(fill="x")
        self.fias_frame.pack_forget()  # Скрываем ФИАС

        # Окно логов
        self.log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=20)
        self.log_box.grid(row=2, column=0, padx=10, pady=10)  # Размещение в третьей строке

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def update_source(self):
        """Обновление выбранного источника и переключение видимости рамок."""
        source = self.source_var.get()
        self.log(f"📍 Выбран источник данных: {source}")

        # Скрываем и показываем нужные рамки
        if source == "GINFO":
            self.ginfo_frame.pack(fill="x")
            self.fias_frame.pack_forget()  # Скрываем ФИАС
        elif source == "FIAS":
            self.fias_frame.pack(fill="x")
            self.ginfo_frame.pack_forget()  # Скрываем GINFO


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
