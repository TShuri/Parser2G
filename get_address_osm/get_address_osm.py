import requests
import xml.etree.ElementTree as ET
import re

# Define the Overpass API URL
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Query чтобы спарсить адреса
overpass_query = """
[out:xml][timeout:25];
area[name="Иркутск"]->.searchArea;
(
  node["addr:street"](area.searchArea);
  way["addr:street"](area.searchArea);
  relation["addr:street"](area.searchArea);
);
out body;
>;
out skel qt;
"""

# Запрос к серверу
response = requests.get(OVERPASS_URL, params={"data": overpass_query})
if response.status_code != 200:
    print(f"Error: Failed to fetch data (HTTP {response.status_code})")
    exit()

root = ET.fromstring(response.content)

# Достаем и обрабатываем адреса
addresses = []
for element in root.findall(".//node") + root.findall(".//way") + root.findall(".//relation"):
    addr_street = None
    addr_housenumber = None

    for tag in element.findall("tag"):
        key = tag.attrib.get("k")
        value = tag.attrib.get("v")
        if key == "addr:street":
            addr_street = value
        elif key == "addr:housenumber":
            addr_housenumber = value

    if addr_street and addr_housenumber:
        # Combine street and house number into a single address
        addresses.append((addr_street, addr_housenumber))

# Сортируем адреса
def extract_number(house):
    """Extract numeric part from a house number, default to 0 if no number."""
    match = re.search(r'\d+', house)
    return int(match.group()) if match else float('inf')

addresses = sorted(addresses, key=lambda x: (x[0], extract_number(x[1])))
formatted_addresses = [f"{street}, {housenumber}" for street, housenumber in addresses]

# Сохраняем в файл
txt_filename = "irkutsk_addresses_sorted.txt"
with open(txt_filename, mode="w", encoding="utf-8") as txtfile:
    txtfile.write("\n".join(formatted_addresses))

print(f"Addresses saved to {txt_filename}")
