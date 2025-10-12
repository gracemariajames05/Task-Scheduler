# tasks.py
from datetime import datetime
from data_handler import save_data, parse_date, next_id
from rewards import reward_user

DATE_TIME_FMT = "%Y-%m-%d %H:%M"

def add_task(data):
    tasks = data["tasks"]
    name = input("Task name: ").strip()
    if not name:
        print("Name can't be empty.")
        return

    while True:
        dl = input(f"Deadline ({DATE_TIME_FMT}): ").strip()
        try:
            dt = datetime.strptime(dl, DATE_TIME_FMT)
            break
        except ValueError:
            print(f"Invalid format. Use {DATE_TIME_FMT}")

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
        "deadline": dt.strftime(DATE_TIME_FMT),
        "duration_hours": duration,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "completed": False,
        "completed_at": None
    }

    tasks.append(task)
    save_data(data)
    print(f"Task added (id={task['id']}).")


def view_tasks(data):
    tasks = data["tasks"]
    if not tasks:
        print("No tasks yet. Add one!")
        return
    tasks_sorted = sorted(tasks, key=lambda t: (t["completed"], t["deadline"], t["id"]))
    print("\nID  | Name (deadline, dur hrs) | Status")
    print("-"*50)
    for t in tasks_sorted:
        status = "DONE" if t["completed"] else "PENDING"
        print(f"{t['id']: <3} | {t['name'][:30]:30} | {t['deadline']} , {t['duration_hours']}h , priority {t['priority']} [{status}]")
    print()


def delete_task(data):
    tasks = data["tasks"]
    if not tasks:
        print("No tasks to delete.")
        return

    print("Tasks:")
    for t in tasks:
        status = "DONE" if t.get("completed", False) else "PENDING"
        print(f"{t['id']}: {t['name']} (deadline {t['deadline']}) [{status}]")

    try:
        tid = int(input("Enter the ID of the task to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    task_to_delete = next((t for t in tasks if t["id"] == tid), None)
    if not task_to_delete:
        print("No task with that ID.")
        return

    confirm = input(f"Are you sure you want to delete '{task_to_delete['name']}'? (y/n): ").strip().lower()
    if confirm == "y":
        tasks.remove(task_to_delete)
        save_data(data)
        print(f"Task '{task_to_delete['name']}' deleted.")
    else:
        print("Deletion cancelled.")


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
    points = data.get("points", 0)
    deadline_dt = parse_date(found["deadline"])
    now_dt = datetime.now()
    gained = 10 if deadline_dt and now_dt.date() <= deadline_dt.date() else 5
    data["points"] = points + gained
    save_data(data)
    print(f"[DONE] {found['name']} — +{gained} points. Total: {data['points']} points")
    reward_user(data["points"])


def suggest_edf(data):
    tasks = [t for t in data["tasks"] if not t["completed"]]
    if not tasks:
        print("No pending tasks to schedule.")
        return

    order = sorted(tasks, key=lambda t: (
        datetime.strptime(t["deadline"], DATE_TIME_FMT),
        t["priority"],
        t["duration_hours"],
        t["id"]
    ))
    print("\nSuggested order (Earliest Deadline First, priority as tie-breaker):")
    total_hours = 0.0
    for i, t in enumerate(order, 1):
        print(f"{i}. {t['name']} — deadline {t['deadline']} — {t['duration_hours']} h — priority {t['priority']}")
        total_hours += t["duration_hours"]
    print(f"Estimated total time to finish pending tasks: {total_hours} hours\n")
