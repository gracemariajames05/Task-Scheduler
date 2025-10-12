#!/usr/bin/env python3
"""
Cozy Task Scheduler GUI (Pretty Edition)
---------------------------------------
- Cleaned layout, rounded buttons, hover effect, and alternating row colors.
- Recommended header image: header.jpeg (1920x120px or wider).
"""

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry

# External dependencies
from data_handler import load_data
from tasks import add_task_data, delete_task_data, mark_complete_data, suggest_edf
from pomodoro import start_pomodoro_ui
from reminder_system import check_reminders

# Pillow for header images
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---------- Theme ----------
COLOR_BG = "#EAD8BB"      # light raffia beige
COLOR_HEADER = "#3E2723"  # deep coffee
COLOR_BTN = "#B6885D"     # soft brown
COLOR_BTN_HOVER = "#a9774e"
COLOR_TEXT = "#452815"
COLOR_TABLE_ODD = "#EFDCC8"
COLOR_TABLE_EVEN = "#EAD8BB"

FONT_TITLE = ("Times New Roman", 18, "bold")
FONT_NORMAL = ("Georgia", 11)
FONT_SMALL = ("Georgia", 9)
HEADER_HEIGHT = 140


# ---------- Toast Message ----------
def toast_message(root, title, message, duration=3000):
    try:
        popup = tk.Toplevel(root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-alpha", 0.0)
        popup.configure(bg=COLOR_HEADER)

        frm = tk.Frame(popup, bg=COLOR_HEADER, padx=10, pady=6)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text=title, font=("Times New Roman", 10, "bold"),
                 bg=COLOR_HEADER, fg=COLOR_BG).pack(anchor="w")
        tk.Label(frm, text=message, font=FONT_SMALL, wraplength=300,
                 bg=COLOR_HEADER, fg=COLOR_BG, justify="left").pack(anchor="w")

        popup.update_idletasks()
        w, h = popup.winfo_width(), popup.winfo_height()
        sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
        start_x, target_x = sw, sw - w - 30
        y = sh - h - 80
        popup.geometry(f"+{start_x}+{y}")

        def slide_in(i=0):
            alpha = (i + 1) / 12
            cur_x = int(start_x + (target_x - start_x) * (i + 1) / 12)
            popup.geometry(f"+{cur_x}+{y}")
            popup.attributes("-alpha", alpha)
            if i < 11:
                popup.after(18, slide_in, i + 1)
            else:
                popup.after(duration, fade_out)

        def fade_out(i=12):
            if i < 0:
                popup.destroy(); return
            popup.attributes("-alpha", i / 12)
            popup.after(25, fade_out, i - 1)

        slide_in()
    except Exception:
        pass


# ---------- Background reminder thread ----------
def start_reminder_thread():
    def run():
        while True:
            try:
                check_reminders()
            except Exception:
                pass
            time.sleep(60)
    threading.Thread(target=run, daemon=True).start()


# ---------- Main Application ----------
class TaskApp:
    def __init__(self, root):
        self.root = root
        root.title("Task Scheduler — Cozy")
        root.geometry("940x600")
        root.configure(bg=COLOR_BG)

        self._header_pil = None
        self._header_img_ref = None

        # --- Header ---
        header = tk.Frame(root, bg=COLOR_HEADER, height=HEADER_HEIGHT)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Header image
        self.header_img_label = tk.Label(header, bg=COLOR_HEADER)
        self.header_img_label.place(x=0, y=0, relwidth=1, relheight=1)
        self._load_header_image("header.png")

        # Title text overlay
        tk.Label(header, text="🌿 Task Scheduler — Cozy",
                 font=FONT_TITLE, bg=COLOR_HEADER, fg="#FBEEC1").place(relx=0.5, rely=0.5, anchor="center")

        # Clock (top-right)
        self.time_var = tk.StringVar()
        tk.Label(header, textvariable=self.time_var, bg="#000", fg="#FBEEC1",
                 font=FONT_SMALL).place(relx=0.98, rely=0.08, anchor="ne")
        self.update_clock()

        # Rescale header image on resize
        def _resize_header(event):
            if self._header_pil:
                w = max(1, event.width)
                h = int(w / (self._header_pil.width / self._header_pil.height))
                resized = self._header_pil.resize((w, h), Image.LANCZOS)
                self._header_img_ref = ImageTk.PhotoImage(resized)
                self.header_img_label.config(image=self._header_img_ref)
        header.bind("<Configure>", _resize_header)

        # --- Main area ---
        main = tk.Frame(root, bg=COLOR_BG)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Task list
        left = tk.Frame(main, bg=COLOR_BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("S.No", "name", "deadline", "duration", "priority", "status")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")

        # Styling Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=COLOR_TABLE_EVEN,
                        foreground=COLOR_TEXT,
                        rowheight=26,
                        fieldbackground=COLOR_TABLE_EVEN,
                        font=("Georgia", 10))
        style.configure("Treeview.Heading",
                        font=("Times New Roman", 11, "bold"),
                        foreground=COLOR_TEXT)
        style.map("Treeview", background=[("selected", COLOR_BTN)])

        for c, w in zip(cols, (50, 240, 160, 90, 80, 80)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")

        # Add alternating row colors
        self.tree.tag_configure("odd", background=COLOR_TABLE_ODD)
        self.tree.tag_configure("even", background=COLOR_TABLE_EVEN)

        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Right: Controls
        right = tk.Frame(main, bg=COLOR_BG, width=240)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # Rounded button look
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Rounded.TButton",
            background=COLOR_BTN,
            foreground="white",
            font=FONT_NORMAL,
            padding=6,
            relief="flat",
            borderwidth=0
        )
        style.map("Rounded.TButton",
                background=[("active", COLOR_BTN_HOVER)])

        def mkbtn(text, cmd):
            btn = ttk.Button(right, text=text, command=cmd, style="Rounded.TButton")
            btn.pack(fill="x", pady=5, padx=14)
            return btn


        mkbtn("Add Task", self.open_add_popup)
        mkbtn("Delete Task", self.delete_selected)
        mkbtn("Mark as Done", self.complete_selected)
        mkbtn("Start Pomodoro", self.start_pomodoro_selected)
        mkbtn("Suggested Schedule", self.show_edf)
        mkbtn("Summary", self.show_summary)
        mkbtn("Refresh", self.refresh)
        mkbtn("Exit", root.destroy)

        tk.Label(right, text="Tip: select a task row first.",
                 bg=COLOR_BG, fg=COLOR_TEXT, font=FONT_SMALL,
                 wraplength=200, justify="left").pack(side="bottom", pady=6)

        # Initialize
        self.refresh()
        start_reminder_thread()

    # ---------- Header ----------
    def _load_header_image(self, path):
        if not PIL_AVAILABLE or not os.path.exists(path):
            return
        try:
            self._header_pil = Image.open(path).convert("RGBA")
            w = max(1, self.root.winfo_width() or 1200)
            h = int(w / (self._header_pil.width / self._header_pil.height))
            resized = self._header_pil.resize((w, h), Image.LANCZOS)
            self._header_img_ref = ImageTk.PhotoImage(resized)
            self.header_img_label.config(image=self._header_img_ref)
        except Exception as e:
            print("Header image load failed:", e)

    # ---------- General ----------
    def update_clock(self):
        self.time_var.set(time.strftime("%A, %d %b %Y  %I:%M %p"))
        self.root.after(1000, self.update_clock)

    def refresh(self):
        data = load_data()
        for i in self.tree.get_children():
            self.tree.delete(i)

        tasks = data.get("tasks", [])
        for idx, t in enumerate(tasks, start=1):
            status = "DONE" if t.get("completed") else "PENDING"
            tag = "even" if idx % 2 == 0 else "odd"

            # Insert serial number (displayed) but store real id as a tag
            self.tree.insert(
                "",
                "end",
                values=(
                    idx,  # serial display only
                    t.get("name"),
                    t.get("deadline"),
                    t.get("duration_hours"),
                    t.get("priority"),
                    status,
                ),
                tags=(tag, str(t.get("id")))
            )

        pts = data.get("points", 0)
        self.root.title(f"Task Scheduler — Cozy — Points: {pts}")

    # ---------- Actions ----------
    def open_add_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Task")
        popup.geometry("460x300")
        popup.configure(bg=COLOR_BG)
        popup.lift()

        frm = tk.Frame(popup, bg=COLOR_BG, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        def lbl(txt, r, c):
            tk.Label(frm, text=txt, bg=COLOR_BG, fg=COLOR_TEXT, font=FONT_NORMAL).grid(row=r, column=c, sticky="w", pady=4)

        lbl("Task name:", 0, 0)
        name_entry = tk.Entry(frm, width=36, font=FONT_NORMAL)
        name_entry.grid(row=0, column=1, columnspan=3, pady=4, sticky="w")

        lbl("Date:", 1, 0)
        date_entry = DateEntry(frm, date_pattern="yyyy-mm-dd")
        date_entry.grid(row=1, column=1, sticky="w")

        lbl("Hour:", 2, 0)
        hour_spin = tk.Spinbox(frm, from_=0, to=23, width=6)
        hour_spin.grid(row=2, column=1, sticky="w")

        lbl("Minute:", 2, 2)
        min_spin = tk.Spinbox(frm, from_=0, to=59, width=6)
        min_spin.grid(row=2, column=3, sticky="w")

        lbl("Duration (hrs):", 3, 0)
        dur_entry = tk.Entry(frm, width=10)
        dur_entry.grid(row=3, column=1, sticky="w")

        lbl("Priority (1–5):", 4, 0)
        prio_spin = tk.Spinbox(frm, from_=1, to=5, width=6)
        prio_spin.grid(row=4, column=1, sticky="w")

        def submit():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Task name required"); return
            date_str = date_entry.get_date().strftime("%Y-%m-%d")
            try:
                hour, minute = int(hour_spin.get()), int(min_spin.get())
                duration = float(dur_entry.get())
                priority = int(prio_spin.get())
            except Exception:
                messagebox.showerror("Error", "Invalid input values"); return
            deadline = f"{date_str} {hour:02d}:{minute:02d}"
            add_task_data(load_data(), name, deadline, duration, priority)
            popup.destroy()
            self.refresh()
            toast_message(self.root, "Task added", f"'{name}' — due {deadline}")

        mkbtn = tk.Button(frm, text="Add Task", command=submit,
                          bg=COLOR_BTN, fg="white", font=FONT_NORMAL,
                          relief="flat", padx=6, pady=4)
        mkbtn.grid(row=6, column=1, pady=12)

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a task row first."); return
        item = sel[0]
        tags = self.tree.item(item)["tags"]
        task_id = int(tags[1]) if len(tags) > 1 else int(tags[0])  # real ID from tag
        name = self.tree.item(item)["values"][1]

        if not messagebox.askyesno("Confirm delete", f"Delete task {task_id}: {name}?"):
            return
        delete_task_data(load_data(), task_id)
        self.refresh()
        toast_message(self.root, "Deleted", f"Task '{name}' deleted")

    def complete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a task row first."); return
        item = sel[0]
        tags = self.tree.item(item)["tags"]
        task_id = int(tags[1]) if len(tags) > 1 else int(tags[0])

        _, gained = mark_complete_data(load_data(), task_id)
        self.refresh()
        toast_message(self.root, "Completed", f"Task completed — +{gained} pts")

    def start_pomodoro_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a task row first."); return
        vitem = sel[0]
        tags = self.tree.item(item)["tags"]
        task_id = int(tags[1]) if len(tags) > 1 else int(tags[0])

        data = load_data()
        task = next((t for t in data.get("tasks", []) if t.get("id") == task_id), None)
        if not task:
            messagebox.showerror("Error", "Task not found"); return
        minutes = simpledialog.askinteger("Pomodoro minutes", "Duration (default 25):", initialvalue=25, minvalue=1)
        if not minutes:
            return
        start_pomodoro_ui(self.root, task.get("name"), duration_minutes=minutes)

    def show_edf(self):
        tasks = suggest_edf(load_data())
        if not tasks:
            messagebox.showinfo("EDF", "No pending tasks"); return
        text = "\n".join(f"{i+1}. {t['name']} — {t['deadline']} — {t['duration_hours']}h — prio {t['priority']}" for i,t in enumerate(tasks))
        messagebox.showinfo("EDF Suggested Order", text)

    def show_summary(self):
        data = load_data()
        total = len(data.get("tasks", []))
        done = sum(1 for t in data.get("tasks", []) if t.get("completed"))
        pending = total - done
        pts = data.get("points", 0)
        messagebox.showinfo("Summary", f"Total: {total}\nDone: {done}\nPending: {pending}\nPoints: {pts}")


# ---------- Run ----------
def main():
    root = tk.Tk()
    TaskApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
