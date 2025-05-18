from dadata import Dadata
from dotenv import load_dotenv
import os

class DadataSuggestion:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("DADATA_TOKEN")
        self.secret = os.getenv("DADATA_SECRET")
        self.dadata = Dadata(self.token, self.secret)
        self.address = None
        self.data = None

    def process_address(self, address):
        try:
            self.address = address
            result = self.dadata.suggest("address", self.address)
            self.data = result[0]
            return self.data
        except Exception as e:
            print(f"Ошибка при обработке адреса: {e}")
            self.data = None
            return None

    def get_value(self):
        return self.data.get("value") if self.data else None

    def get_unrestricted_value(self):
        return self.data.get("unrestricted_value") if self.data else None

    def get_city(self):
        return self.data.get("data").get("city") if self.data else None

    def get_settlement(self):
        return self.data.get("data").get("settlement") if self.data else None

    def get_street(self):
        return self.data.get("data").get("street") if self.data else None

    def get_stead(self):
        return self.data.get("data").get("stead") if self.data else None

    def get_name_street(self):
        seettlement = self.get_settlement()
        street = self.get_street()
        stead = self.get_stead()

        if seettlement:
            return seettlement
        if street:
            return street
        if stead:
            return stead

    def get_house(self):
        return self.data.get("data").get("house") if self.data else None

    def get_coords(self):
        if not self.data:
            return None
        return {
            "lat": self.data.get("data").get("geo_lat"),
            "lon": self.data.get("data").get("geo_lon")
        }

if __name__ == "__main__":
    dadata_parser = DadataSuggestion()
    address = "Иркутск, Ленина, 15"
    file = dadata_parser.process_address(address)
    print(file.get("value"))

    print("Значение адреса:", dadata_parser.get_value())
    print("Полное значение адреса:", dadata_parser.get_unrestricted_value())
    print("Город:", dadata_parser.get_city())
    print("Микрорайон:", dadata_parser.get_settlement())
    print("Участок:", dadata_parser.get_stead())
    print("Улица:", dadata_parser.get_street())
    print("Дом:", dadata_parser.get_house())
    print("Координаты:", dadata_parser.get_coords())
    print("Наименование улицы:", dadata_parser.get_name_street())
