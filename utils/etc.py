# utils/etc.py
# Garfield Bot Management – ETC helper

import os
import json
from datetime import datetime
from .tools import wib_now

# ----------------------------------------------------------
# File management (save & load data JSON lokal)
# ----------------------------------------------------------
def load_json(filename, default={}):
    if not os.path.exists(filename):
        return default
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ----------------------------------------------------------
# Path utility
# ----------------------------------------------------------
def ensure_dir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

# ----------------------------------------------------------
# Error logging ke file logs/error.log
# ----------------------------------------------------------
def log_error(text):
    ensure_dir("logs")
    with open("logs/error.log", "a", encoding="utf-8") as f:
        f.write(f"[{wib_now()}] {text}\n")

# ----------------------------------------------------------
# Fungsi validasi ID
# ----------------------------------------------------------
def is_valid_id(x):
    try
