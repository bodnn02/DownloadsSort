import os
import json
import shutil
import hashlib
from platformdirs import user_downloads_dir, user_documents_dir, user_music_dir, user_pictures_dir, user_videos_dir

CONFIG_PATH = 'config.json'

# Получаем системные пути
DEFAULT_CONFIG = {
    "downloads": os.path.normpath(user_downloads_dir()),
    "images": {
        "path": os.path.normpath(user_pictures_dir()),
        "extensions": [".jpg", ".png", ".gif"]
    },
    "music": {
        "path": os.path.normpath(user_music_dir()),
        "extensions": [".mp3", ".wav", ".flac", ".weba"]
    },
    "videos": {
        "path": os.path.normpath(user_videos_dir()),
        "extensions": [".mp4", ".avi", ".mkv", ".mov"]
    },
    "executables": {
        "path": os.path.normpath(os.path.join(user_downloads_dir(), "Executables")),
        "extensions": [".exe", ".msi"]
    },
    "documents": {
        "path": os.path.normpath(user_documents_dir()),
        "extensions": [".docx", ".pdf", ".txt"]
    },
    "compressed": {
        "path": os.path.normpath(os.path.join(user_downloads_dir(), "Compressed")),
        "extensions": [".zip", ".7z", ".rar"]
    },
    "databases": {
        "path": os.path.normpath(os.path.join(user_downloads_dir(), "Databases")),
        "extensions": [".db", ".sqlite", ".sql"]
    },
    "torrents": {
        "path": os.path.normpath(os.path.join(user_downloads_dir(), "Torrents")),
        "extensions": [".torrent"]
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as config_file:
            json.dump(DEFAULT_CONFIG, config_file, ensure_ascii=False, indent=4)
        print("Создан файл config.json с настройками по умолчанию.")
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
            return config
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
                    if get_file_hash(file_path) == get_file_hash(destination_path):
                        trash_folder = os.path.join(source_folder, "trash")
                        if not os.path.exists(trash_folder):
                            os.makedirs(trash_folder)
                        shutil.move(file_path, os.path.join(trash_folder, file_name))
                        print(f"Файл {file_name} уже существует в {destination_folder}. Перемещен в корзину.")
                        continue
                    else:
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
        
        if downloads_folder and os.path.exists(downloads_folder):
            for type_name, type_info in config.items():
                if type_name != "downloads" and isinstance(type_info, dict):
                    file_extensions = type_info.get("extensions", [])
                    move_files(downloads_folder, type_info.get("path", ""), file_extensions)
        else:
            print("Папка для загрузок не найдена. Проверьте путь в config.json.")


if __name__ == "__main__":
    organize_downloads()
    print("Файлы успешно отсортированы.")
    input("Нажмите Enter, чтобы закрыть...")