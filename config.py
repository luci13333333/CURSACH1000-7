from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

LECTURES_DIR = "lectures"
LECTURES_LIST_FILE = "lectures_list.txt"


# Создание необходимых директорий и файлов
if not os.path.exists(LECTURES_DIR):
    os.makedirs(LECTURES_DIR)

if not os.path.exists(LECTURES_LIST_FILE):
    with open(LECTURES_LIST_FILE, "w") as f:
        pass