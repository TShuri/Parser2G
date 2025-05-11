from dadata import Dadata
from dotenv import load_dotenv
import os

class DadataStandardization:
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
            result = self.dadata.clean("address", self.address)
            self.data = result
            return result
        except Exception as e:
            print(f"Ошибка при обработке адреса: {e}")
            self.data = None
            return None

    def get_full_address(self):
        return self.data.get("result") if self.data else None

    def get_city(self):
        return self.data.get("city") if self.data else None

    def get_city_district(self):
        return self.data.get("city_district") if self.data else None

    def get_settlement(self):
        return self.data.get("settlement") if self.data else None

    def get_street(self):
        return self.data.get("street") if self.data else None

    def get_stead(self):
        return self.data.get("stead") if self.data else None

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
        return self.data.get("house") if self.data else None

    def get_coords(self):
        if not self.data:
            return None
        return {
            "lat": self.data.get("geo_lat"),
            "lon": self.data.get("geo_lon")
        }

if __name__ == "__main__":
    dadata_parser = DadataStandardization()
    dadata_parser.process_address("Иркутск, крылатый, 4")

    print("Полный адрес:", dadata_parser.get_full_address())
    print("Улица:", dadata_parser.get_street())
    print("Дом:", dadata_parser.get_house())
    print("Город:", dadata_parser.get_city())
    print("Район:", dadata_parser.get_city_district())
    print("Координаты:", dadata_parser.get_coords())
