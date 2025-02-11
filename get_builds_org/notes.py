for address in addresses:
    if i == counter: break

    print(f"Ищем: {address}")

    # Находим поле поиска
    search_box = driver.find_element(By.NAME, "search")
    search_box.clear()
    search_box.send_keys(address)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)  # Ждём загрузки

    # Парсим информацию о здании
    try:
        square = driver.find_element(By.XPATH, "//span[contains(text(), 'Площадь')]/following-sibling::span").text
    except:
        square = "Не найдено"

    print(f"Адрес: {address}, Площадь: {square}")

    # Парсим организации в здании
    organizations = driver.find_elements(By.CLASS_NAME, "searchResults__resultTitle")
    
    org_list = []
    for org in organizations:
        name = org.text
        print(f"Организация: {name}")
        org_list.append(name)

    # Сохраняем в БД
    #save_to_db(address, square, org_list)
    i += 1