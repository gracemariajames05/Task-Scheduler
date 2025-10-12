# reminder_system.py
from datetime import datetime, timedelta
from data_handler import load_data, DATE_TIME_FMT
from plyer import notification

REMINDER_WINDOW_MIN = 10  # minutes

def check_reminders():
    """
    Run frequently (thread in GUI). Sends a desktop notification for any pending tasks
    whose deadline is within the next REMINDER_WINDOW_MIN minutes.
    """
    data = load_data()
    now = datetime.now()
    upcoming = now + timedelta(minutes=REMINDER_WINDOW_MIN)
    for task in data.get("tasks", []):
        if task.get("completed", False):
            continue
        try:
            d = datetime.strptime(task["deadline"], DATE_TIME_FMT)
        except Exception:
            continue
        # if within [now, upcoming] and we haven't notified recently
        # (simple approach: mark a transient 'notified' key in task — saved)
        if now <= d <= upcoming and not task.get("_reminder_sent", False):
            notification.notify(
                title="Task reminder",
                message=f"{task['name']} at {d.strftime(DATE_TIME_FMT)}",
                timeout=8
            )
            # mark as notified so we don't spam; persist lightly
            task["_reminder_sent"] = True
    # save updated tasks (persist notified flags)
    try:
        # keep save without raising if other process uses file
        from data_handler import save_data, load_data as ld
        data2 = ld()
        # sync _reminder_sent flags from data to saved file (simple overwrite)
        save_data(data)
    except Exception:
        pass
