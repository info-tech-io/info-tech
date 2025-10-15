import argparse
import xml.etree.ElementTree as ET
import csv
import os
from collections import OrderedDict

def parse_xml_to_csv(xml_file_path):
    """
    Parses a specific XML file format to a CSV file.

    The process involves two passes:
    1. First Pass: Iterate through all <ASBO> elements to collect a complete,
       ordered set of all possible child tags. These will become the CSV headers.
    2. Second Pass: Iterate through the <ASBO> elements again, extracting data
       for each header. If a tag is missing in an <ASBO> element, an empty
       string is used as its value.
    Finally, writes the data to a CSV file with the same base name.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Ошибка: Не удалось разобрать XML файл. Проверьте его формат. {e}")
        return
    except FileNotFoundError:
        print(f"��шибка: Файл не найден по пути: {xml_file_path}")
        return

    # XML-файлы часто используют пространства имен. Мы должны их учитывать при поиске элементов.
    # Получим пространство имен из корневого элемента
    namespace = ''
    if '}' in root.tag:
        namespace = root.tag.split('}')[0][1:]
    
    ns_map = {'ns': namespace}

    # --- Первый проход: Сбор всех уникальных заголовков ---
    # Используем OrderedDict для сохранения порядка, в котором теги были впервые встречены
    headers = OrderedDict()
    asbo_elements = root.findall('.//ns:ASBO', ns_map)

    if not asbo_elements:
        print("Предупреждение: В XML файле не найдены элементы <ASBO>. Выходной CSV файл будет пустым.")
        # Создаем пустой csv файл с таким же именем
        csv_file_path = os.path.splitext(xml_file_path)[0] + '.csv'
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            pass # create empty file
        print(f"Создан пустой файл: {csv_file_path}")
        return

    for asbo in asbo_elements:
        for child in asbo:
            # Извлекаем имя тега без пространства имен
            tag_name = child.tag.split('}')[-1]
            if tag_name not in headers:
                headers[tag_name] = None
    
    header_list = list(headers.keys())

    # --- Второй проход: Извлечение данных для каждой строки ---
    all_rows_data = []
    for asbo in asbo_elements:
        # Создаем словарь с данными текущего элемента <ASBO>
        current_row_dict = {child.tag.split('}')[-1]: child.text for child in asbo}
        
        # Формируем строку в соответствии с общим списком заголовков
        row_data = [current_row_dict.get(header, "") for header in header_list]
        all_rows_data.append(row_data)

    # --- Запись в CSV файл ---
    csv_file_path = os.path.splitext(xml_file_path)[0] + '.csv'

    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Используем csv.QUOTE_ALL, чтобы заключить все поля в двойные кавычки,
            # как того требует задача. Пустые строки будут представлены как "".
            writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
            
            # Записываем заголовки
            writer.writerow(header_list)
            
            # Записываем данные
            writer.writerows(all_rows_data)
            
        print(f"Файл успешно создан: {csv_file_path}")

    except IOError as e:
        print(f"Ошибка при записи в файл {csv_file_path}: {e}")


def main():
    """
    Основная функция для обработки аргументов командной строки.
    """
    parser = argparse.ArgumentParser(
        description="Конвертер из XML в CSV для специального формата сообщений.",
        epilog="Пример использования: python parse_to_csv.py my_data.xml"
    )
    parser.add_argument(
        "filename",
        help="Имя входного XML файла (должен находиться в той же папке)."
    )
    args = parser.parse_args()
    
    # We need to construct the absolute path to the file
    # The user is instructed to place the file in the same directory as the script
    # However, the script can be called from anywhere, so we need to be careful.
    # Let's assume the filename provided is in the current working directory.
    file_path = os.path.abspath(args.filename)

    parse_xml_to_csv(file_path)


if __name__ == "__main__":
    main()
