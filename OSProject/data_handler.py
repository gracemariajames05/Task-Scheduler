# data_handler.py
import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"
DATE_TIME_FMT = "%Y-%m-%d %H:%M"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "points": 0}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1

def parse_date(s):
    try:
        return datetime.strptime(s, DATE_TIME_FMT)
    except ValueError:
        return None
