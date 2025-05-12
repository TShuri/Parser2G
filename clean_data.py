from parsers.dadata.suggestion import DadataSuggestion


def processing_data(address_info, build, orgs, build_info):
    pass

def processing_address_info(address_info):
    data = {}
    data['address'] = address_info['value']
    data['full_address'] = address_info['unrestricted_value']
    data['city'] = address_info['data']['city']

    street = address_info['data']['street']
    settlement = address_info['data']['settlement']
    stead = address_info['data']['stead']
    if street is not None:
        data['street'] = street
    elif settlement is not None:
        data['street'] = settlement
    else:
        data['street'] = stead

    data['house'] = address_info['data']['house']

    return data

def processing_build(building_info):
    data = {}
    data['id'] = building_info.get("address", {}).get("building_id"),
    data['name'] = building_info.get("address", {}).get("building_name"),
    data['postcode'] = building_info.get("address", {}).get("postcode"),
    data['district'] = next((adm["name"] for adm in building_info.get("adm_div", []) if adm["type"] == "district"), None),
    data['lat'] = building_info.get("point", {}).get("lat"),
    data['lon'] = building_info.get("point", {}).get("lon"),


if __name__ == "__main__":
    dadata_parser = DadataSuggestion()
    address = "Иркутск, Ленина, 15"
    address_info = dadata_parser.process_address(address)
    print(address_info)

    processing_address_info(address_info)