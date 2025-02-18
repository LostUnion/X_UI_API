import json
from datetime import datetime

json_filename = f'json/get_list_{datetime.now().strftime("%Y-%m-%d")}.json'

def loads_json_to_file(data):
    if data is not None:
        # Преобразуем строку в формат JSON
        data_json = json.loads(data)
        
        # Открываем файл для записи данных (если файла нет, он будет создан)
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data_json, f, ensure_ascii=False, indent=4)
            return True, json_filename
    else:
        return False