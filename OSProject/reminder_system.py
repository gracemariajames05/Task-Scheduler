import json
from datetime import datetime, timedelta

DATA_FILE = "tasks.json"
DATE_TIME_FMT = "%Y-%m-%d %H:%M"

def load_data():
    """Load tasks and points from tasks.json"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tasks": [], "points": 0}

def check_reminders():
    """Check for tasks due in the next 10 minutes and print reminders"""
    data = load_data()
    now = datetime.now()
    upcoming_window = now + timedelta(minutes=10)  # 10-min reminder window

    for task in data["tasks"]:
        if task.get("completed", False):
            continue  # skip completed tasks
        try:
            task_deadline = datetime.strptime(task["deadline"], DATE_TIME_FMT)
        except ValueError:
            continue  # skip if deadline format is wrong

        if now <= task_deadline <= upcoming_window:
            print(f"⏰ Reminder: '{task['name']}' is coming up at {task_deadline.strftime(DATE_TIME_FMT)}")
