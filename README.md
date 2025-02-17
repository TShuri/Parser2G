# 📌 PyCharm Парсер Адресов и Зданий

## 📖 Описание
Этот проект содержит набор парсеров для работы с адресами и зданиями, используя данные из OpenStreetMap (OSM) и 2ГИС.

### 📂 Структура проекта
#### `get_address_osm/` (Работает с OpenStreetMap)
- `get_address_osm.py` — получает весь список адресов города.
- `get_district_osm.py` — получает список районов города.
- `get_addresses_for_district_osm.py` — получает список адресов соответствующего района.

#### `get_builds_org/` (Работает с 2ГИС)
- `script_on_mock.py` — работает с тестовыми данными, получает информацию о зданиях и организациях внутри здания в формате JSON.
- `script_on_file.py` — работает с файлом (список адресов, полученный из OSM), получает информацию о зданиях и организациях внутри здания в формате JSON.

## ⚙️ Установка
### 1. Клонирование репозитория
```sh
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 2. Установка зависимостей
Создайте виртуальное окружение (рекомендуется):
```sh
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate  # для Windows
```

Установите зависимости:
```sh
pip install -r requirements.txt
```

## 🚀 Использование

### Получение адресов из OpenStreetMap
```sh
python get_address_osm/get_address_osm.py
```

### Получение районов
```sh
python get_address_osm/get_district_osm.py
```

### Получение адресов по району
```sh
python get_address_osm/get_addresses_for_district_osm.py
```

### Работа с 2ГИС (тестовые данные)
```sh
python get_builds_org/script_on_mock.py
```

### Работа с 2ГИС (файл с адресами)
```sh
python get_builds_org/script_on_file.py
```

## 🛠 Требования
- Python 3.8+
- Установленные зависимости из `requirements.txt`

## 📜 Лицензия
Нет лицензии...
