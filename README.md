# 📌 Парсер Адресов и Зданий с организациями

## 📖 Описание
Этот проект содержит набор парсеров для работы с адресами и зданиями, используя данные из OpenStreetMap (OSM) и 2ГИС.

### 📂 Структура проекта

📂 data_clean/ – обработанные и экспортированные данные
- 📂 export_data/ – экспортированные данные
- 📂 processed_data/ – Очищенные данные
- 🐍 cleanup_script.py - Очищает полученные данные с 2ГИС
- 🐍 convert_to_csv.py - Экспортирует очищенные данные в .csv

📂 data_raw/ – сырые (неочищенные) данные
- 📂 2gis/ – данные с 2ГИС о зданиях и организациях внутри здания
- 📂 osm/ – списки адресов с OpenStreetMap

📂 db_integration/ – здесь будет интеграция с базой данных

📂 parsers/ – парсеры 
- 📂 2gis/ – парсер 2ГИС (также содержит логирование)
- - 🐍 script.py - получает данные с 2ГИС о зданиях и организациях внутри здания
- 📂 osm/ – парсеры OpenStreetMap
- - 🐍 get_addresses_for_district.py - получает список адресов соответствующего района
- - 🐍 get_all_addresses.py - получает весь список адресов города
- - 🐍 get_districts.py - получает список районов города

📂 tests/ – папка с папками для тестов проекта (**Рекомендуется для ознакомления с проектом!**)

## ⚙️ Установка
### 1. Клонирование репозитория
```sh
git clone https://github.com/TShuri/Parser2G.git
cd your-repository
```

### 2. Установка зависимостей
Создайте виртуальное окружение (рекомендуется):
```sh
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate  # для Windows
```

Установите зависимости для windows:
```sh
pip install -r requirements.txt
```

Установите зависимости для mac:
```sh
brew install chromedriver

pip install webdriver-manager

pip install selenium-wire

pip uninstall pywin32 pypiwin32 # если установлены, необходимо удалить

````

## 🔍 Ознакомление (использовать папку tests/)
📂 tests/ – тесты скриптов
- 📂 tests_2gis_parser/ – работа с 2ГИС
  - 📂 test_district/ - будет содержать выходные файлы после работы скрипта
  - 📄 test_addresses - тестовые адреса, с ними работает тестовый скрипт
  - 🐍 test_script - скрипт для работы с тестовыми данными
- 📂 test_clean_export_data - работа с чисткой и экспортом данных
  - 📂 export_data/ – экспортированные тестовые данные
  - 📂 processed_data/ – Очищенные тестовые данные
  - 🐍 test_clean.py - Очищает полученные тестовые данные с 2ГИС
  - 🐍 test_convert_to_csv.py - Экспортирует очищенные тестовые данные в .csv

## 🚀 Использование

### Получение адресов из OpenStreetMap
```sh
python parsers/osm/get_all_addresses.py
```

### Получение районов
```sh
python parsers/osm/get_districts.py
```

### Получение адресов по району
```sh
python parsers/osm/get_addresses_for_district.py
```

### Работа с 2ГИС (файл с адресами)
```sh
python parsers/twogis/twogis_parser.py
```

## 🛠 Требования
- Python 3.8+
- Установленные зависимости из `requirements.txt`

## 📜 Лицензия
Нет лицензии...
