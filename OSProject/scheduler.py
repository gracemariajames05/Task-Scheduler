#!/usr/bin/env python3
"""
Simple Task Scheduler (terminal version)
- Add / View / Complete tasks
- EDF (Earliest Deadline First) suggestion
- Persists tasks + points to tasks.json
"""
import json
from datetime import datetime
import os

DATA_FILE = "tasks.json"
DATE_FMT = "%Y-%m-%d"  # use YYYY-MM-DD

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
        return datetime.strptime(s, DATE_FMT)
    except ValueError:
        return None

def add_task(data):
    tasks = data["tasks"]
    name = input("Task name: ").strip()
    if not name:
        print("Name can't be empty.")
        return
    while True:
        dl = input(f"Deadline ({DATE_FMT}): ").strip()
        dt = parse_date(dl)
        if dt:
            break
        print("Invalid date format. Try again.")
    while True:
        dur = input("Estimated duration (hours, e.g. 1.5): ").strip()
        try:
            duration = float(dur)
            if duration <= 0:
                raise ValueError
            break
        except ValueError:
            print("Enter a positive number like 1 or 0.5")
    while True:
        pr = input("Priority (1-5, 1 = highest): ").strip()
        try:
            priority = int(pr)
            if priority < 1 or priority > 5:
                raise ValueError
            break
        except ValueError:
            print("Enter an integer between 1 and 5")

    task = {
        "id": next_id(tasks),
        "name": name,
        "deadline": dt.strftime(DATE_FMT),
        "duration_hours": duration,
        "priority": priority,  # <-- new field
        "created_at": datetime.now().isoformat(),
        "completed": False,
        "completed_at": None
    }
    tasks.append(task)
    save_data(data)
    print(f"Task added (id={task['id']}).")

def view_tasks(data, show_all=True):
    tasks = data["tasks"]
    if not tasks:
        print("No tasks yet. Add one!")
        return
    # Sort by deadline then by id
    tasks_sorted = sorted(tasks, key=lambda t: (t["completed"], t["deadline"], t["id"]))
    print("\nID  | Name (deadline, dur hrs) | Status")
    print("-"*50)
    for t in tasks_sorted:
        status = "DONE" if t["completed"] else "PENDING"
        print(f"{t['id']: <3} | {t['name'][:30]:30} | {t['deadline']} , {t['duration_hours']}h , priority {t['priority']} [{status}]")
    print()

def mark_complete(data):
    tasks = data["tasks"]
    pending = [t for t in tasks if not t["completed"]]
    if not pending:
        print("No pending tasks to complete.")
        return
    print("Pending tasks:")
    for t in pending:
        print(f"{t['id']}: {t['name']} (deadline {t['deadline']})")
    try:
        tid = int(input("Enter id to mark complete: ").strip())
    except ValueError:
        print("Invalid id.")
        return
    found = next((t for t in tasks if t["id"] == tid), None)
    if not found:
        print("No task with that id.")
        return
    if found["completed"]:
        print("Task already completed.")
        return
    found["completed"] = True
    found["completed_at"] = datetime.now().isoformat()
    # Points: +10 if completed on or before deadline, else +5
    points = data.get("points", 0)
    deadline_dt = parse_date(found["deadline"])
    now_dt = datetime.now()
    if deadline_dt and now_dt.date() <= deadline_dt.date():
        gained = 10
    else:
        gained = 5
    data["points"] = points + gained
    save_data(data)
    print(f"[DONE] {found['name']} — +{gained} points. Total: {data['points']} points")

def suggest_edf(data):
    tasks = [t for t in data["tasks"] if not t["completed"]]
    if not tasks:
        print("No pending tasks to schedule.")
        return
    # Sort by deadline → priority → duration → id
    def key_fn(t):
        return (parse_date(t["deadline"]) or datetime.max, t["priority"], t["duration_hours"], t["id"])
    
    order = sorted(tasks, key=key_fn)
    print("\nSuggested order (Earliest Deadline First, priority as tie-breaker):")
    total_hours = 0.0
    for i, t in enumerate(order, 1):
        print(f"{i}. {t['name']} — deadline {t['deadline']} — {t['duration_hours']} h — priority {t['priority']}")
        total_hours += t["duration_hours"]
    print(f"Estimated total time to finish pending tasks: {total_hours} hours\n")

def summary(data):
    tasks = data["tasks"]
    total = len(tasks)
    done = sum(1 for t in tasks if t["completed"])
    pending = total - done
    print("Summary:")
    print(f"Total tasks: {total} | Done: {done} | Pending: {pending} | Points: {data.get('points',0)}")

def main_loop():
    print("=== Task Scheduler (terminal) ===")
    data = load_data()
    while True:
        print("\nMenu:")
        print("1) Add Task")
        print("2) View Tasks")
        print("3) Mark Task Complete")
        print("4) Suggest Schedule (EDF)")
        print("5) Summary")
        print("6) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_task(data)
        elif choice == "2":
            view_tasks(data)
        elif choice == "3":
            mark_complete(data)
        elif choice == "4":
            suggest_edf(data)
        elif choice == "5":
            summary(data)
        elif choice == "6":
            print("Bye! Data saved to", DATA_FILE)
            break
        else:
            print("Unknown choice. Try 1-6.")

if __name__ == "__main__":
    main_loop()