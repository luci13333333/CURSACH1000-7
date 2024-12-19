import os

API_TOKEN = "7149635723:AAFuvN9cNgQCqMHjuhHW1kDTIxnR9h5GQXE"
LECTURES_DIR = "lectures"
LECTURES_LIST_FILE = "lectures_list.txt"

# Создание необходимых директорий и файлов
if not os.path.exists(LECTURES_DIR):
    os.makedirs(LECTURES_DIR)

if not os.path.exists(LECTURES_LIST_FILE):
    with open(LECTURES_LIST_FILE, "w") as f:
        pass