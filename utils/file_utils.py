import os

def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def ensure_file_exists(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            pass
