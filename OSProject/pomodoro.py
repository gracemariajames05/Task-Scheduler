# pomodoro.py
import tkinter as tk
from tkinter import messagebox
import platform, time
from threading import Thread
from plyer import notification

def start_pomodoro_ui(parent, task_name, duration_minutes=25, blocked_sites=None, real_block=False):
    """
    parent: root Tk instance (so Toplevel has the proper master)
    Shows a Toplevel with controls and runs countdown via after().
    This function returns immediately; UI runs on mainloop.
    """
    blocked_sites = blocked_sites or []
    popup = tk.Toplevel(parent)
    popup.title(f"Pomodoro — {task_name}")
    popup.geometry("320x180")
    label = tk.Label(popup, text=f"{task_name}", font=("Helvetica", 12, "bold"))
    label.pack(pady=(8,0))
    timer_label = tk.Label(popup, text="", font=("Helvetica", 20))
    timer_label.pack(pady=8)

    status_label = tk.Label(popup, text="", font=("Helvetica", 9))
    status_label.pack()

    # optional: simulate blocking message (no terminal output)
    if blocked_sites:
        status_label.config(text=f"Blocking (simulated): {', '.join(blocked_sites)}")
    else:
        status_label.config(text="No blocking")

    remaining = [duration_minutes * 60]  # mutable container so nested functions can change it
    running = [True]  # boolean flag stored in list for mutability

    def update_label():
        mins, secs = divmod(max(0, remaining[0]), 60)
        timer_label.config(text=f"{mins:02d}:{secs:02d}")

    def countdown():
        if running[0] and remaining[0] > 0:
            remaining[0] -= 1
            update_label()
            popup.after(1000, countdown)
        elif remaining[0] <= 0:
            update_label()
            notification.notify(title="Pomodoro finished", message=f"'{task_name}' Pomodoro finished", timeout=5)
            messagebox.showinfo("Done", f"Pomodoro for '{task_name}' completed!")
            popup.destroy()

    def pause_resume():
        running[0] = not running[0]
        btn_pause.config(text="Resume" if not running[0] else "Pause")
        if running[0]:
            countdown()

    def add_five():
        remaining[0] += 5 * 60
        update_label()

    def stop():
        running[0] = False
        popup.destroy()

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=8)
    btn_pause = tk.Button(btn_frame, text="Pause", width=8, command=pause_resume)
    btn_pause.grid(row=0, column=0, padx=4)
    btn_plus = tk.Button(btn_frame, text="+5 min", width=8, command=add_five)
    btn_plus.grid(row=0, column=1, padx=4)
    btn_stop = tk.Button(btn_frame, text="Stop", width=8, command=stop)
    btn_stop.grid(row=0, column=2, padx=4)

    update_label()
    popup.after(1000, countdown)
    return popup

# convenience wrapper for non-GUI calls (keeps old interface)
def start_pomodoro(task_name, duration_minutes=25, blocked_sites=None, real_block=False):
    # fallback command-line friendly (minimal): just notify and sleep
    try:
        from tkinter import Tk
        root = Tk()
        root.withdraw()
        start_pomodoro_ui(root, task_name, duration_minutes, blocked_sites, real_block)
        root.mainloop()
    except Exception:
        # non-GUI fallback
        import time
        for i in range(duration_minutes*60,0,-1):
            mins, secs = divmod(i,60)
            print(f"\rTime remaining: {mins:02d}:{secs:02d}", end="")
            time.sleep(1)
        notification.notify(title="Pomodoro finished", message=f"'{task_name}' Pomodoro finished", timeout=5)
