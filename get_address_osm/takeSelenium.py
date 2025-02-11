from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Настройка Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    # Открываем 2ГИС
    driver.get("https://2gis.ru")

    # Ждём загрузки страницы
    time.sleep(5)

    # Находим строку поиска
    search_box = driver.find_element(By.CLASS_NAME, "searchBar__input")

    # Вводим запрос (например, "кафе")
    search_query = "Иркутск"
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.ENTER)

    # Ждём результаты поиска
    time.sleep(5)

    # Ищем первый элемент в результатах
    result = driver.find_element(By.CLASS_NAME, "miniCard__content")

    # Кликаем по нему
    result.click()

    # Ждём загрузки страницы объекта
    time.sleep(5)

    # Извлекаем координаты из URL
    url = driver.current_url
    if "place" in url:
        # Координаты в URL находятся после 'place/' и разделены запятой
        coordinates = url.split("place/")[1].split("/")[0]
        print(f"Координаты объекта: {coordinates}")
    else:
        print("Не удалось найти координаты в URL.")

finally:
    # Закрываем браузер
    driver.quit()
