from dadata import Dadata

class DadataAddress:
    def __init__(self, token, secret, address=None):
        self.token = token
        self.secret = secret
        self.dadata = Dadata(token, secret)
        self.address = address
        self.data = None

    def process_address(self, raw_address: str):
        try:
            result = self.dadata.clean("address", raw_address)
            self.data = result
            return result
        except Exception as e:
            print(f"Ошибка при обработке адреса: {e}")
            self.data = None
            return None

    def set_address(self, address):
        self.address = address

    def get_full_address(self):
        return self.data.get("result") if self.data else None

    def get_street(self):
        return self.data.get("street") if self.data else None

    def get_house(self):
        return self.data.get("house") if self.data else None

    def get_city(self):
        return self.data.get("city") if self.data else None

    def get_city_district(self):
        return self.data.get("city_district") if self.data else None

    def get_coords(self):
        if not self.data:
            return None
        return {
            "lat": self.data.get("geo_lat"),
            "lon": self.data.get("geo_lon")
        }

if __name__ == "__main__":
    token = "80219668a6c5cf96def06462f6e05fd147e0223b"
    secret = "3091ba0b3524603295189105effb34c0ba675af3"

    dadata_parser = DadataAddress(token, secret)
    dadata_parser.process_address("Иркутск, Ленина, 15")

    print("Полный адрес:", dadata_parser.get_full_address())
    print("Улица:", dadata_parser.get_street())
    print("Дом:", dadata_parser.get_house())
    print("Город:", dadata_parser.get_city())
    print("Район:", dadata_parser.get_city_district())
    print("Координаты:", dadata_parser.get_coords())
