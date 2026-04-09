import tkinter as tk
from tkinter import ttk
import pickle
from datetime import datetime
import csv
import os

from tab_live import LiveTab
from tab_records import RecordsTab
from tab_footage import FootageTab
from tab_students import StudentsTab

BG = "#eef3fb"
SIDEBAR_BG = "#ffffff"
BORDER = "#dbe3f0"
ACCENT = "#4f8cff"
TEXT = "#1f2937"
SUBTEXT = "#64748b"

# LOAD DATA
with open("encodings.pkl", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
students = data["students"]

root = tk.Tk()
root.title("Smart Attendance System")
root.geometry("1400x820")   
root.configure(bg=BG)

root.rowconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# SIDEBAR
sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=260, highlightthickness=1, highlightbackground=BORDER)
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)

content = tk.Frame(root, bg=BG)
content.grid(row=0, column=1, sticky="nsew")
content.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)

# HEADER
tk.Label(sidebar, text="Smart Attendance", font=("Segoe UI", 18, "bold"),
         bg=SIDEBAR_BG, fg=TEXT).pack(anchor="w", padx=18, pady=(18, 4))

tk.Label(sidebar, text="CCTV + Face Recognition", font=("Segoe UI", 10),
         bg=SIDEBAR_BG, fg=SUBTEXT).pack(anchor="w", padx=18, pady=(0, 16))

tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(0, 14))

# FRAMES
live_frame = tk.Frame(content, bg=BG)
records_frame = tk.Frame(content, bg=BG)
footage_frame = tk.Frame(content, bg=BG)
students_frame = tk.Frame(content, bg=BG)

for f in (live_frame, records_frame, footage_frame, students_frame):
    f.grid(row=0, column=0, sticky="nsew")

# INIT TABS
live_tab = LiveTab(live_frame, known_encodings, students)
records_tab = RecordsTab(records_frame)
footage_tab = FootageTab(footage_frame)
students_tab = StudentsTab(students_frame, lambda: show_view("live"))

# 🔥 CRITICAL FIX (camera control)
root.live_tab = live_tab

# =========================
# LIVE DATA REFRESH
# =========================
def refresh_live_data():
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)

    live_tab.known_encodings = data["encodings"]
    live_tab.students = data["students"]

    live_tab.attendance_status = {
        s["reg_no"]: {"name": s["name"], "count": 0, "status": ""}
        for s in data["students"]
    }

root.refresh_live_data = refresh_live_data

# FOOTAGE REFRESH
def refresh_footage():
    footage_tab.load_videos()

root.refresh_footage = refresh_footage

# SAVE ATTENDANCE
def save_attendance():
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    file_exists = os.path.isfile("attendance_records.csv")

    with open("attendance_records.csv", "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Date","Time","Name","Reg_No","Status"])

        for reg, data in live_tab.attendance_status.items():
            writer.writerow([date, time, data["name"], reg, data["status"]])

# MONITOR
session_state = {"was_active": False, "saved": True}

def monitor_class_end():
    if live_tab.class_active:
        session_state["was_active"] = True
        session_state["saved"] = False

    elif session_state["was_active"] and not session_state["saved"]:
        save_attendance()
        records_tab.load_sessions()
        session_state["saved"] = True
        session_state["was_active"] = False

    root.after(500, monitor_class_end)

# NAVIGATION
nav_buttons = {}

def show_view(name):
    mapping = {
        "live": live_frame,
        "records": records_frame,
        "footage": footage_frame,
        "students": students_frame
    }

    mapping[name].tkraise()

    for key, btn in nav_buttons.items():
        btn.config(bg=ACCENT if key == name else SIDEBAR_BG,
                   fg="white" if key == name else TEXT)
        
    if name == "live":
        try:
            live_tab.pause_camera()
            live_tab.resume_camera()
        except:
            pass
    if name == "records":
        records_tab.load_sessions()
    elif name == "footage":
        footage_tab.load_videos()
    elif name == "students":
        students_tab.load_students()

def make_nav(text, key):
    btn = tk.Button(
        sidebar,
        text=text,
        command=lambda: show_view(key),
        bg=SIDEBAR_BG,
        fg=TEXT,
        relief="flat",
        font=("Segoe UI", 11, "bold"),
        anchor="w",
        padx=18,
        pady=12
    )
    btn.pack(fill="x", padx=12, pady=6)
    nav_buttons[key] = btn

# NAV ITEMS
make_nav("Live Monitoring", "live")
make_nav("Attendance Records", "records")
make_nav("Class Footage", "footage")
make_nav("Students Details", "students")

# DEFAULT
show_view("live")

# CLOSE
def on_close():
    live_tab.release()
    footage_tab.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

live_tab.update()
monitor_class_end()

root.mainloop()