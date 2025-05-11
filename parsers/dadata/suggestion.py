from dadata import Dadata
from dotenv import load_dotenv
import os

class DadataSuggestion:
    def __init__(self, address=None):
        load_dotenv()
        self.token = os.getenv("DADATA_TOKEN")
        self.secret = os.getenv("DADATA_SECRET")
        self.dadata = Dadata(self.token, self.secret)
        self.address = address
        self.data = None

    def process_address(self):
        try:
            result = self.dadata.suggest("address", self.address)
            self.data = result[0]
            return result
        except Exception as e:
            print(f"Ошибка при обработке адреса: {e}")
            self.data = None
            return None

    def set_address(self, address):
        self.address = address

    def get_value(self):
        return self.data.get("value") if self.data else None

    def get_unrestricted_value(self):
        return self.data.get("unrestricted_value") if self.data else None

    def get_street(self):
        return self.data.get("data").get("street") if self.data else None

    def get_house(self):
        return self.data.get("data").get("house") if self.data else None

    def get_city(self):
        return self.data.get("data").get("city") if self.data else None

    def get_coords(self):
        if not self.data:
            return None
        return {
            "lat": self.data.get("data").get("geo_lat"),
            "lon": self.data.get("data").get("geo_lon")
        }

if __name__ == "__main__":
    dadata_parser = DadataSuggestion()
    dadata_parser.set_address("Иркутск, Ленина, 15")
    dadata_parser.process_address()

    print("Значение адреса:", dadata_parser.get_value())
    print("Полное значение адреса:", dadata_parser.get_unrestricted_value())
    print("Улица:", dadata_parser.get_street())
    print("Дом:", dadata_parser.get_house())
    print("Город:", dadata_parser.get_city())
    print("Координаты:", dadata_parser.get_coords())
