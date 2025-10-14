# scheduler.py
from data_handler import load_data
from tasks import add_task, view_tasks, delete_task, mark_complete, suggest_edf
from reminder_system import check_reminders
from rewards import reward_user
from pomodoro import start_pomodoro
import threading
import time

DATA_FILE = "tasks.json"

def start_reminder_thread():
    def run():
        while True:
            check_reminders()
            time.sleep(60)
    thread = threading.Thread(target=run, daemon=True)
    thread.start()


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
    start_reminder_thread()

    while True:
        print("\nMenu:")
        print("1) Add Task")
        print("2) View Tasks")
        print("3) Mark Task Complete")
        print("4) Suggest Schedule (EDF)")
        print("5) Summary")
        print("6) Delete Task")
        print("7) Start Pomodoro")
        print("8) Exit")

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
            delete_task(data)
        elif choice == "7":  # Pomodoro
            pending_tasks = [t for t in data["tasks"] if not t["completed"]]
            if not pending_tasks:
                print("No pending tasks!")
                continue

            print("Pending tasks:")
            for t in pending_tasks:
                print(f"{t['id']}: {t['name']} ({t['deadline']})")

            try:
                tid = int(input("Enter task ID to start Pomodoro: ").strip())
            except ValueError:
                print("Invalid ID.")
                continue

            task = next((t for t in pending_tasks if t["id"] == tid), None)
            if not task:
                print("No task with that ID.")
                continue

            # Ask for blocked sites
            blocked_input = input("Enter websites to block during Pomodoro (comma separated, or leave empty): ").strip()
            blocked_sites = [s.strip() for s in blocked_input.split(",") if s.strip()] if blocked_input else None

            # Ask if user wants real blocking
            real_block = False
            if blocked_sites:
                ans = input("Attempt real blocking via hosts file? (requires admin) [y/N]: ").strip().lower()
                real_block = ans == "y"

            # Ask for Pomodoro duration (optional)
            dur_input = input("Duration in minutes (default 25): ").strip()
            try:
                duration_minutes = int(dur_input) if dur_input else 25
            except ValueError:
                duration_minutes = 25

            # Start Pomodoro (with extend option)
            start_pomodoro(task["name"], duration_minutes=duration_minutes,
                        blocked_sites=blocked_sites, real_block=real_block)
        elif choice == "8":
            print("Bye! Data saved to", DATA_FILE)
            break
        else:
            print("Unknown choice. Try 1-8.")


if __name__ == "__main__":
    main_loop()
