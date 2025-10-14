# tasks.py
from datetime import datetime
from data_handler import load_data, save_data, next_id, DATE_TIME_FMT
from rewards import reward_user

def add_task_data(data, name, deadline, duration_hours, priority):
    """Add a task using parameters (for GUI). deadline must be 'YYYY-MM-DD HH:MM'"""
    tasks = data.get("tasks", [])
    # validate deadline
    try:
        dt = datetime.strptime(deadline, DATE_TIME_FMT)
    except ValueError:
        raise ValueError("Invalid deadline format. Use YYYY-MM-DD HH:MM")

    task = {
        "id": next_id(tasks),
        "name": str(name),
        "deadline": dt.strftime(DATE_TIME_FMT),
        "duration_hours": float(duration_hours),
        "priority": int(priority),
        "created_at": datetime.now().isoformat(),
        "completed": False,
        "completed_at": None
    }
    tasks.append(task)
    data["tasks"] = tasks
    save_data(data)
    return task

def delete_task_data(data, task_id):
    tasks = data.get("tasks", [])
    found = next((t for t in tasks if t["id"] == task_id), None)
    if not found:
        raise KeyError(f"No task with id {task_id}")
    tasks.remove(found)
    save_data(data)
    return found

def mark_complete_data(data, task_id):
    tasks = data.get("tasks", [])
    found = next((t for t in tasks if t["id"] == task_id), None)
    if not found:
        raise KeyError(f"No task with id {task_id}")
    if found["completed"]:
        return found, 0
    found["completed"] = True
    found["completed_at"] = datetime.now().isoformat()
    # points policy
    from data_handler import parse_date
    deadline_dt = parse_date(found["deadline"])
    now_dt = datetime.now()
    gained = 10 if deadline_dt and now_dt.date() <= deadline_dt.date() else 5
    data["points"] = data.get("points", 0) + gained
    save_data(data)
    # notify reward system
    reward_user(data["points"], message=f"Completed '{found['name']}' — +{gained} points")
    return found, gained

def suggest_edf(data):
    tasks = [t for t in data.get("tasks", []) if not t.get("completed", False)]
    if not tasks:
        return []
    tasks_sorted = sorted(tasks, key=lambda t: (
        datetime.strptime(t["deadline"], DATE_TIME_FMT),
        t["priority"],
        t["duration_hours"],
        t["id"]
    ))
    return tasks_sorted
