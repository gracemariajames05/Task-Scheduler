# pomodoro.py (updated)
import time
import platform
import threading

def start_pomodoro(task_name, duration_minutes=25, blocked_sites=None, real_block=False):
    """
    Run a Pomodoro timer for a task.
    blocked_sites: list of websites to block (optional)
    real_block: if True, attempt actual blocking via hosts file (Windows)
    """
    print(f"\n💫 Starting Pomodoro for '{task_name}' — {duration_minutes} min")

    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    redirect_ip = "127.0.0.1"

    # Block websites if requested
    if blocked_sites:
        if real_block and platform.system() == "Windows":
            try:
                with open(hosts_path, "r+") as file:
                    content = file.read()
                    for site in blocked_sites:
                        if site not in content:
                            file.write(f"{redirect_ip} {site}\n")
                print("🚫 Websites blocked (hosts file).")
            except PermissionError:
                print("⚠️ Admin permission required to block websites.")
        else:
            print(f"🚫 Pretending to block sites: {', '.join(blocked_sites)} (real_block=False)")

    remaining_seconds = duration_minutes * 60
    stop_timer = threading.Event()

    def timer():
        nonlocal remaining_seconds
        while remaining_seconds > 0 and not stop_timer.is_set():
            mins, secs = divmod(remaining_seconds, 60)
            print(f"\rTime remaining: {mins:02d}:{secs:02d}", end="")
            time.sleep(1)
            remaining_seconds -= 1
        if remaining_seconds <= 0:
            print("\n⏰ Pomodoro complete! Take a short break.")

    t = threading.Thread(target=timer)
    t.start()

    # Allow user to extend timer
    while t.is_alive():
        extend_input = input("\nType '+N' to add N minutes to Pomodoro, or press Enter to continue: ").strip()
        if extend_input.startswith("+"):
            try:
                extra = int(extend_input[1:])
                remaining_seconds += extra * 60
                print(f"⏱ Added {extra} minutes. New remaining time: {remaining_seconds//60} min")
            except ValueError:
                print("Invalid input. Use format +5 to add 5 minutes.")
        else:
            time.sleep(1)  # small pause to avoid tight loop

    # Unblock websites if real_block
    if blocked_sites and real_block and platform.system() == "Windows":
        try:
            with open(hosts_path, "r") as file:
                lines = file.readlines()
            with open(hosts_path, "w") as file:
                for line in lines:
                    if not any(site in line for site in blocked_sites):
                        file.write(line)
            print("✅ Websites unblocked.")
        except PermissionError:
            print("⚠️ Could not unblock websites (permission error).")