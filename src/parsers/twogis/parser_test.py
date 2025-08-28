import subprocess
import json
import os
from typing import Union
from urllib.parse import quote

def run_parser(city: str,
               category: str,
               output: str = "test.json",
               output_format: str = 'json') -> Union[list, dict, str]:
    """
    Вызывает CLI-парсер parser-2gis и возвращает результат.
    - Если output_format == 'json' возвращается распарсенный объект (list/dict).
    - Иначе возвращается строка (stdout или содержимое output-файла).
    Параметры:
      city         - название города (Обязательно на транслитом и с маленькой буквы например: Иркутск = irkutsk )
      category     - категория поиска
      output       - путь к файлу для записи
      output_format- формат вывода (обычно 'json')
    """
    # Формируем URL
    url = f"https://2gis.ru/{quote(city)}/search/{quote(category)}"
    print(f"Запуск парсера по URL: {url}")

    cmd = [
        'parser-2gis',
        '-i', url,
        '-o', output,
        '-f', output_format
    ]
    # Запуск процесса
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # Выводим полезную информацию для отладки
        print("Ошибка при выполнении парсера.")
        if e.stdout:
            print("STDOUT:\n", e.stdout)
        if e.stderr:
            print("STDERR:\n", e.stderr)
        raise

    if output_format.lower() == 'json':
        stdout_text = (completed.stdout or "").strip()
        if stdout_text:
            try:
                return json.loads(stdout_text)
            except json.JSONDecodeError:
                print("Не удалось распарсить JSON из stdout, попробую прочитать файл:", output)

        if os.path.exists(output):
            try:
                with open(output, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка при чтении/парсинге файла {output}: {e}")
                raise
        else:
            print("Файл с результатом не найден и stdout пуст.")
            return []
    else:
        stdout_text = (completed.stdout or "")
        if stdout_text.strip():
            return stdout_text
        if os.path.exists(output):
            with open(output, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

if __name__ == '__main__':
    results = run_parser(city="irkutsk", category="ВУЗ", output="test.json", output_format="json")

    if isinstance(results, (list, dict)):
        print("Получено организаций (элемент/ключей):", len(results) if isinstance(results, list) else len(results.keys()))
    else:
        print("Результат в виде строки, длина:", len(results))

    try:
        with open('2gis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("Результат сохранён в 2gis_results.json")
    except TypeError:
        with open('2gis_results.json', 'w', encoding='utf-8') as f:
            f.write(str(results))
        print("Текстовый результат сохранён в 2gis_results.json")
