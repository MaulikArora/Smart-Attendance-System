import tkinter as tk
from tkinter import ttk
import csv
import os

BG = "#eef3fb"
CARD_BG = "#ffffff"
BORDER = "#dbe3f0"
TEXT = "#1f2937"
SUBTEXT = "#64748b"


class RecordsTab:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg=BG)

        self.session_var = tk.StringVar()

        self.parent.rowconfigure(2, weight=1)
        self.parent.columnconfigure(0, weight=1)

        header_card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        header_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        header_card.columnconfigure(0, weight=1)

        title = tk.Label(
            header_card,
            text="Attendance Records",
            font=("Segoe UI", 18, "bold"),
            bg=CARD_BG,
            fg=TEXT
        )
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))

        subtitle = tk.Label(
            header_card,
            text="Choose a class session by date and time",
            font=("Segoe UI", 10),
            bg=CARD_BG,
            fg=SUBTEXT
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        filter_card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        filter_card.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        filter_card.columnconfigure(1, weight=1)

        filter_label = tk.Label(
            filter_card,
            text="Session",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT
        )
        filter_label.grid(row=0, column=0, sticky="w", padx=(16, 10), pady=14)

        self.dropdown = ttk.Combobox(
            filter_card,
            textvariable=self.session_var,
            width=40,
            style="Modern.TCombobox",
            state="readonly"
        )
        self.dropdown.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=14)
        self.dropdown.bind("<<ComboboxSelected>>", self.load_records)

        table_card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        table_card.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 12))
        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            table_card,
            columns=("Name", "Reg", "Status"),
            show="headings",
            style="Modern.Treeview"
        )
        self.tree.heading("Name", text="Name")
        self.tree.heading("Reg", text="Reg No")
        self.tree.heading("Status", text="Status")

        self.tree.column("Name", anchor="center", width=240)
        self.tree.column("Reg", anchor="center", width=180)
        self.tree.column("Status", anchor="center", width=140)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.status_label = tk.Label(
            parent,
            text="Select a session to view records",
            font=("Segoe UI", 11),
            bg=BG,
            fg=SUBTEXT
        )
        self.status_label.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 20))

        self.sessions = {}
        self.load_sessions()

    def load_sessions(self):
        self.sessions = {}

        if not os.path.exists("attendance_records.csv"):
            self.dropdown["values"] = []
            self.session_var.set("")
            self.status_label.config(text="No attendance data found")
            return

        sessions = set()

        with open("attendance_records.csv") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row.get("Date", "")
                time = row.get("Time", "00:00:00")
                key = f"{date} {time}"
                sessions.add(key)
                self.sessions[key] = (date, time)

        sorted_sessions = sorted(list(sessions), reverse=True)
        self.dropdown["values"] = sorted_sessions

        if sorted_sessions:
            self.status_label.config(text="Select a session to view records")
        else:
            self.status_label.config(text="No sessions available")

        if self.session_var.get() not in self.sessions:
            self.session_var.set("")

    def load_records(self, event=None):
        selected = self.session_var.get()
        if selected not in self.sessions:
            return

        date, time = self.sessions[selected]

        for row in self.tree.get_children():
            self.tree.delete(row)

        with open("attendance_records.csv") as f:
            reader = csv.DictReader(f)
            rows = [
                (row["Name"], row["Reg_No"], row["Status"])
                for row in reader
                if row.get("Date") == date and row.get("Time", "00:00:00") == time
            ]

        if not rows:
            self.status_label.config(text="No records for this session")
            return

        self.status_label.config(text="Loading records...")
        self.insert_rows_smooth(rows, 0)

    def insert_rows_smooth(self, rows, index):
        if index >= len(rows):
            self.status_label.config(text="Loaded")
            return

        self.tree.insert("", "end", values=rows[index])
        self.parent.after(10, lambda: self.insert_rows_smooth(rows, index + 1))