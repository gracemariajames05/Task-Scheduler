#!/usr/bin/env python3
"""
Pomodoro Timer Module for Cozy Task Scheduler
---------------------------------------------
Seamlessly integrates with TaskApp GUI.
Features:
- Focus / Break timers
- Start / Pause / Reset / Close buttons
- GIF animation
- Optional app-blocking during focus
"""

import os
import time
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import psutil

# ---------- Theme constants (match GUI) ----------
COLOR_BG = "#EAD8BB"
COLOR_TEXT = "#452815"
COLOR_BTN = "#B6885D"
COLOR_HEADER = "#3E2723"
FONT_NORMAL = ("Georgia", 11)

# ---------- Resource path helper ----------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    import sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ---------- Pomodoro UI function ----------
def start_pomodoro_ui(root, task_name, focus_minutes=25, break_minutes=5, blocked_apps=None):
    """Pomodoro modal integrated with GUI. Optionally blocks apps during focus."""
    win = tk.Toplevel(root)
    win.title(f"Pomodoro — {task_name}")
    win.attributes("-fullscreen", True)
    win.configure(bg=COLOR_BG)
    win.transient(root)
    win.grab_set()

    # ---------- Load GIFs ----------
    gifs = {"focus": [], "break": []}
    for mode, file_name in [("focus", "pomodoro.gif"), ("break", "pomodoro_break.gif")]:
        path = resource_path(file_name)
        if os.path.exists(path):
            frames = []
            i = 0
            while True:
                try:
                    frame = tk.PhotoImage(file=path, format=f"gif - {i}")
                    frames.append(frame)
                    i += 1
                except Exception:
                    break
            gifs[mode] = frames

    gif_label = tk.Label(win, bg=COLOR_BG)
    gif_label.pack(pady=(18, 8))

    # ---------- Timer label ----------
    timer_var = tk.StringVar()
    timer_label = tk.Label(win, textvariable=timer_var,
                           font=("Segoe UI", 36, "bold"),
                           bg=COLOR_BG, fg=COLOR_TEXT)
    timer_label.pack(pady=(6, 12))

    # ---------- Controls ----------
    controls_frame = tk.Frame(win, bg=COLOR_BG)
    controls_frame.pack(pady=(8, 6))

    state = {
        "mode": "focus",
        "running": False,
        "paused": False,
        "after_id": None,
        "anim_after_id": None,
        "gif_index": 0,
        "gifs": gifs,
        "focus_minutes": focus_minutes,
        "break_minutes": break_minutes,
        "remaining": focus_minutes * 60,
        "blocked_apps": set(b.lower() for b in blocked_apps) if blocked_apps else set(),
        "blocking": False,
        "block_thread": None,
    }

    # ---------- GIF animation ----------
    def animate_gif():
        frames = state["gifs"][state["mode"]]
        if frames:
            gif_label.configure(image=frames[state["gif_index"]])
            state["gif_index"] = (state["gif_index"] + 1) % len(frames)
            state["anim_after_id"] = win.after(100, animate_gif)

    def start_gif():
        if state["anim_after_id"] is None:
            animate_gif()

    def stop_gif():
        if state["anim_after_id"]:
            try:
                win.after_cancel(state["anim_after_id"])
            except Exception:
                pass
            state["anim_after_id"] = None

    # ---------- Timer helper ----------
    def format_time(s):
        m, sec = divmod(s, 60)
        return f"{m:02d}:{sec:02d}"

    # ---------- Kill blocked apps ----------
    def kill_blocked():
        for p in psutil.process_iter(["name", "exe"]):
            try:
                name = (p.info["name"] or "").lower()
                exe  = (p.info["exe"] or "").lower()
                if name in state["blocked_apps"] or any(exe.endswith(b) for b in state["blocked_apps"]):
                    try:
                        p.terminate()
                        try:
                            p.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            p.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # ---------- App-blocking thread ----------
    def block_apps_loop():
        state["blocking"] = True
        while state["blocking"]:
            if state["blocked_apps"]:
                kill_blocked()
            time.sleep(0.75)

    def start_blocking():
        if state["blocked_apps"] and not state["block_thread"]:
            t = threading.Thread(target=block_apps_loop, daemon=True)
            t.start()
            state["block_thread"] = t

    def stop_blocking():
        state["blocking"] = False
        state["block_thread"] = None

    # ---------- Timer tick ----------
    def timer_tick():
        if not state["running"]:
            return
        if state["remaining"] <= 0:
            state["running"] = False
            stop_gif()
            stop_blocking()
            if state["mode"] == "focus":
                messagebox.showinfo("Focus Finished", f"Time for a {break_minutes}-minute break!")
                start_break()
            else:
                messagebox.showinfo("Break Finished", "Back to focus!")
                win.destroy()
            return
        state["remaining"] -= 1
        timer_var.set(format_time(state["remaining"]))
        state["after_id"] = win.after(1000, timer_tick)

    # ---------- Start / Pause / Reset ----------
    def start_timer():
        if state["running"]:
            return
        state["running"] = True
        state["paused"] = False
        start_gif()
        if state["mode"] == "focus":
            start_blocking()
        timer_tick()

    def pause_timer():
        if not state["running"]:
            return
        state["running"] = False
        state["paused"] = True
        if state["after_id"]:
            try:
                win.after_cancel(state["after_id"])
            except Exception:
                pass
            state["after_id"] = None
        stop_gif()
        stop_blocking()

    def reset_timer():
        state["running"] = False
        state["paused"] = False
        if state["after_id"]:
            try:
                win.after_cancel(state["after_id"])
            except Exception:
                pass
            state["after_id"] = None
        state["gif_index"] = 0
        state["remaining"] = state["focus_minutes"] * 60 if state["mode"] == "focus" else state["break_minutes"] * 60
        timer_var.set(format_time(state["remaining"]))
        stop_gif()
        frames = state["gifs"][state["mode"]]
        if frames:
            gif_label.configure(image=frames[0])

    def close_win():
        state["running"] = False
        stop_gif()
        stop_blocking()
        if state["after_id"]:
            try:
                win.after_cancel(state["after_id"])
            except Exception:
                pass
        try:
            win.grab_release()
        except Exception:
            pass
        win.destroy()

    # ---------- Break ----------
    def start_break():
        state["mode"] = "break"
        state["remaining"] = state["break_minutes"] * 60
        state["gif_index"] = 0
        start_timer()

    # ---------- Buttons ----------
    btn_start = tk.Button(controls_frame, text="Start", command=start_timer,
                          bg=COLOR_BTN, fg="white", font=FONT_NORMAL, relief="flat", padx=8, pady=6)
    btn_pause = tk.Button(controls_frame, text="Pause", command=pause_timer,
                          bg=COLOR_BTN, fg="white", font=FONT_NORMAL, relief="flat", padx=8, pady=6)
    btn_reset = tk.Button(controls_frame, text="Reset", command=reset_timer,
                          bg=COLOR_BTN, fg="white", font=FONT_NORMAL, relief="flat", padx=8, pady=6)
    btn_close = tk.Button(win, text="Close", command=close_win,
                          bg=COLOR_HEADER, fg=COLOR_BG, font=FONT_NORMAL, relief="flat", padx=8, pady=6)

    btn_start.grid(row=0, column=0, padx=6)
    btn_pause.grid(row=0, column=1, padx=6)
    btn_reset.grid(row=0, column=2, padx=6)
    btn_close.pack(pady=(10, 12))

    timer_var.set(format_time(state["remaining"]))
    win.protocol("WM_DELETE_WINDOW", close_win)

    return win