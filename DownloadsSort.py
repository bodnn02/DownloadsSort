import os
import json
import shutil
import hashlib

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        print("Файл config.json не найден.")
        return None
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON в файле config.json.")
        return None

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buf = file.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(65536)
    return hasher.hexdigest()

def move_files(source_folder, destination_folder, file_extensions):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)

        if os.path.isfile(file_path):
            _, file_extension = os.path.splitext(file_name)
            file_extension = file_extension.lower()

            if isinstance(file_extensions, list) and any(file_extension in ext for ext in file_extensions):
                destination_path = os.path.join(destination_folder, file_name)

                if os.path.exists(destination_path):
                    # Сравниваем хэши файлов
                    if get_file_hash(file_path) == get_file_hash(destination_path):
                        # Если хэши одинаковы, переместим файл в корзину (можно использовать другую папку)
                        trash_folder = os.path.join(source_folder, "trash")
                        if not os.path.exists(trash_folder):
                            os.makedirs(trash_folder)
                        shutil.move(file_path, os.path.join(trash_folder, file_name))
                        print(f"Файл {file_name} уже существует в {destination_folder}. Перемещен в корзину.")
                        continue
                    else:
                        # Если хэши разные, добавим число к имени файла
                        count = 1
                        new_file_name = os.path.splitext(file_name)[0] + f"_{count}" + os.path.splitext(file_name)[1]
                        while os.path.exists(os.path.join(destination_folder, new_file_name)):
                            count += 1
                            new_file_name = os.path.splitext(file_name)[0] + f"_{count}" + os.path.splitext(file_name)[1]
                        destination_path = os.path.join(destination_folder, new_file_name)

                shutil.move(file_path, destination_path)
                print(f"Перемещен файл: {file_name} -> {destination_folder}")

def organize_downloads():
    config = load_config()

    if config is not None:
        downloads_folder = config.get("downloads", "")
        if downloads_folder:
            for type_name, type_info in config.items():
                if type_name != "downloads" and isinstance(type_info, dict):
                    file_extensions = type_info.get("extensions", [])
                    move_files(downloads_folder, type_info.get("path", ""), file_extensions)

if __name__ == "__main__":
    organize_downloads()
