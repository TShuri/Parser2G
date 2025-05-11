from dadata import Dadata

class DadataSuggestion:
    def __init__(self, token, secret, address=None):
        self.token = token
        self.secret = secret
        self.dadata = Dadata(token, secret)
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
    token = "80219668a6c5cf96def06462f6e05fd147e0223b"
    secret = "3091ba0b3524603295189105effb34c0ba675af3"

    dadata_parser = DadataSuggestion(token, secret)
    dadata_parser.set_address("Иркутск, Ленина, 15")
    dadata_parser.process_address()

    print("Значение адреса:", dadata_parser.get_value())
    print("Полное значение адреса:", dadata_parser.get_unrestricted_value())
    print("Улица:", dadata_parser.get_street())
    print("Дом:", dadata_parser.get_house())
    print("Город:", dadata_parser.get_city())
    print("Координаты:", dadata_parser.get_coords())
