import tkinter as tk
from tkinter import scrolledtext
from gui.ginfo_frame import GinfoFrame
from gui.fias_frame import FiasFrame
from gui.gis_frame import GisFrame

# Заглушки
from parsers.ginfo.get_districts import get_districts
# from parsers.ginfo import parse_streets, parse_addresses
# from parsers.fias import parse_fias_addresses
# from parsers.dgist import parse_buildings

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

        # Рамки
        GinfoFrame(root, self.log).pack(padx=10, pady=5, fill="x")
        FiasFrame(root, self.log, run_in_thread(self.parse_fias)).pack(padx=10, pady=5, fill="x")
        GisFrame(root, self.log, run_in_thread(self.parse_2gis)).pack(padx=10, pady=5, fill="x")

        # Лог
        self.log_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=20)
        self.log_box.pack(padx=10, pady=10)

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def parse_districts(self):
        pass

    def parse_streets(self):
        print("GINFO streets parsing...")

    def parse_addresses(self):
        print("GINFO address parsing...")

    def parse_fias(self):
        print("FIAS parsing...")

    def parse_2gis(self):
        print("2GIS parsing...")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
