import cv2
import face_recognition  # type: ignore
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import os

BG = "#eef3fb"
CARD_BG = "#ffffff"
BORDER = "#dbe3f0"
TEXT = "#1f2937"
SUBTEXT = "#64748b"
ACCENT = "#4f8cff"
GREEN = "#22c55e"
RED = "#ef4444"


class LiveTab:
    def __init__(self, parent, known_encodings, students):
        self.parent = parent
        self.known_encodings = known_encodings
        self.students = students

        self.results_finalized = False

        self.attendance_status = {
            s["reg_no"]: {"name": s["name"], "count": 0, "status": ""}
            for s in students
        }

        self.frame_count = 0
        self.check_number = 0

        self.cap = cv2.VideoCapture(0)

        self.recording = False
        self.out = None
        self.video_path = None

        self.class_active = False
        self.camera_active = True

        self.parent.configure(bg=BG)
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=3, minsize=780)
        self.parent.columnconfigure(1, weight=1, minsize=360)

        self.camera_card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        self.camera_card.grid(row=0, column=0, sticky="nsew", padx=(20, 12), pady=20)
        self.camera_card.rowconfigure(1, weight=1)
        self.camera_card.columnconfigure(0, weight=1)

        camera_header = tk.Frame(self.camera_card, bg=CARD_BG)
        camera_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        camera_header.columnconfigure(0, weight=1)

        title = tk.Label(
            camera_header,
            text="Live Monitoring",
            font=("Segoe UI", 18, "bold"),
            bg=CARD_BG,
            fg=TEXT
        )
        title.grid(row=0, column=0, sticky="w")

        self.status_chip = tk.Label(
            camera_header,
            text="● READY",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=SUBTEXT
        )
        self.status_chip.grid(row=0, column=1, sticky="e")

        self.checks_label = tk.Label(
            camera_header,
            text="Checks 0 / 6",
            font=("Segoe UI", 10),
            bg=CARD_BG,
            fg=SUBTEXT
        )
        self.checks_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.progress = ttk.Progressbar(
            camera_header,
            maximum=6,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress.grid(row=1, column=1, sticky="ew", padx=(14, 0), pady=(6, 0))

        self.left_frame = tk.Label(self.camera_card, bg="#dfe8f6")
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        self.right_frame = tk.Frame(
            parent,
            bg=CARD_BG,
            width=360,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        self.right_frame.grid(row=0, column=1, sticky="ns", padx=(12, 20), pady=20)
        self.right_frame.grid_propagate(False)
        self.right_frame.rowconfigure(2, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        panel_title = tk.Label(
            self.right_frame,
            text="Class Panel",
            font=("Segoe UI", 16, "bold"),
            bg=CARD_BG,
            fg=TEXT
        )
        panel_title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        progress_card = tk.Frame(self.right_frame, bg="#f8fbff")
        progress_card.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        progress_card.columnconfigure(0, weight=1)

        progress_title = tk.Label(
            progress_card,
            text="Attendance Progress",
            font=("Segoe UI", 10, "bold"),
            bg="#f8fbff",
            fg=SUBTEXT
        )
        progress_title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        self.progress_value = tk.Label(
            progress_card,
            text="0 / 6",
            font=("Segoe UI", 14, "bold"),
            bg="#f8fbff",
            fg=TEXT
        )
        self.progress_value.grid(row=1, column=0, sticky="w", padx=12)

        self.progress_bar = ttk.Progressbar(
            progress_card,
            maximum=6,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=12, pady=(8, 12))

        list_card = tk.Frame(
            self.right_frame,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        list_card.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))
        list_card.rowconfigure(0, weight=1)
        list_card.columnconfigure(0, weight=1)

        self.list_canvas = tk.Canvas(list_card, bg=CARD_BG, highlightthickness=0, bd=0)
        self.list_scroll = ttk.Scrollbar(list_card, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=self.list_scroll.set)

        self.list_canvas.grid(row=0, column=0, sticky="nsew")
        self.list_scroll.grid(row=0, column=1, sticky="ns")

        self.list_frame = tk.Frame(self.list_canvas, bg=CARD_BG)
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )
        self.list_canvas.bind(
            "<Configure>",
            lambda e: self.list_canvas.itemconfigure(self.list_window, width=e.width)
        )

        self.labels = {}
        for s in students:
            reg = s["reg_no"]
            lbl = tk.Label(
                self.list_frame,
                text=f"{s['name']} : (0/6)",
                font=("Consolas", 12),
                bg=CARD_BG,
                fg=TEXT,
                anchor="w",
                width=40
            )
            lbl.pack(fill="x", pady=4)
            self.labels[reg] = lbl

        self.button = tk.Button(
            self.right_frame,
            text="Start Class",
            font=("Segoe UI", 12, "bold"),
            bg="#22c55e",
            fg="white",
            activebackground="#16a34a",
            activeforeground="white",
            relief="flat",
            bd=0,
            command=self.toggle_class
        )
        self.button.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))

        self.reload_btn = tk.Button(
            self.right_frame,
            text="Reload Camera",
            font=("Segoe UI", 11),
            bg="#4f8cff",
            fg="white",
            command=self.reload_camera
        )
        self.reload_btn.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 16))

    def toggle_class(self):
        if not self.class_active:
            self.start_class()
        elif self.check_number == 6:
            self.end_class()

    def start_class(self):
        self.class_active = True
        self.results_finalized = False
        self.button.config(text="End Class", bg="#64748b", activebackground="#64748b", state="disabled")

        self.frame_count = 0
        self.check_number = 0

        for reg in self.attendance_status:
            self.attendance_status[reg]["count"] = 0
            self.attendance_status[reg]["status"] = ""

    def end_class(self):
        self.class_active = False
        self.results_finalized = True
        self.button.config(text="Start Class", bg="#22c55e", activebackground="#16a34a", state="normal")

        if self.recording:
            self.recording = False
            if self.out is not None:
                self.out.release()
                self.out = None
            print("Recording saved")

        for reg, data in self.attendance_status.items():
            data["status"] = "Present" if data["count"] >= 4 else "Absent"

        if hasattr(self.parent.master.master, "refresh_footage"):
            self.parent.master.master.refresh_footage()

    def update(self):
        if not self.camera_active or self.cap is None:
            self.parent.after(100, self.update)
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        if self.class_active:
            self.frame_count += 1

            if self.frame_count % 30 == 0 and self.check_number < 6:
                if not self.recording:
                    if not os.path.exists("footage"):
                        os.makedirs("footage")

                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    self.video_path = f"footage/{timestamp}.avi"

                    fourcc = cv2.VideoWriter_fourcc(*"XVID")
                    h, w, _ = frame.shape
                    self.out = cv2.VideoWriter(self.video_path, fourcc, 20.0, (w, h))
                    self.recording = True
                    print(f"Recording started: {self.video_path}")

                self.check_number += 1

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                locations = face_recognition.face_locations(rgb)
                encodings = face_recognition.face_encodings(rgb, locations)

                detected = set()

                for encoding in encodings:
                    matches = face_recognition.compare_faces(self.known_encodings, encoding)
                    distances = face_recognition.face_distance(self.known_encodings, encoding)

                    if len(distances) > 0:
                        best = np.argmin(distances)
                        if matches[best]:
                            reg = self.students[best]["reg_no"]
                            if reg not in detected:
                                detected.add(reg)
                                self.attendance_status[reg]["count"] += 1

        if self.recording and self.out:
            self.out.write(frame)

        if self.check_number == 6 and self.class_active:
            if self.recording:
                self.out.release()
                self.out = None
                self.recording = False
                print("Recording saved (auto)")

            self.button.config(bg="#ef4444", activebackground="#dc2626", state="normal")

        self.progress["value"] = self.check_number
        self.progress_value.config(text=f"{self.check_number} / 6")
        self.checks_label.config(text=f"Checks {self.check_number} / 6")

        if not self.class_active:
            self.status_chip.config(text="● READY", fg=SUBTEXT)
        elif self.recording:
            self.status_chip.config(text="● RECORDING", fg=RED)
        else:
            self.status_chip.config(text="● LIVE", fg=GREEN)

        for reg, data in self.attendance_status.items():
            if not self.results_finalized:
                if self.check_number < 6:
                    text = f"{data['name']} : ({data['count']}/6)"
                else:
                    text = f"{data['name']} : ({data['count']}/6)"

                color = TEXT

            else:
                text = f"{data['name']} : {data['status']} ({data['count']}/6)"
                color = GREEN if data["status"] == "Present" else RED

            self.labels[reg].config(text=text, fg=color)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.recording:
            pass

        w = self.left_frame.winfo_width()
        h = self.left_frame.winfo_height()

        if w > 100 and h > 100:
            fh, fw, _ = frame_rgb.shape
            scale = min(w / fw, h / fh)
            new_w = max(1, int(fw * scale))
            new_h = max(1, int(fh * scale))
            resized = cv2.resize(frame_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)

            canvas = Image.new("RGB", (w, h), (223, 232, 246))
            x = (w - new_w) // 2
            y = (h - new_h) // 2
            canvas.paste(Image.fromarray(resized), (x, y))
            img = ImageTk.PhotoImage(canvas)
        else:
            img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

        self.left_frame.imgtk = img
        self.left_frame.config(image=img)

        self.parent.after(15, self.update)

    def pause_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def resume_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)

    def reload_camera(self):
        # stop camera usage
        self.camera_active = False

        try:
            if self.cap:
                self.cap.release()
                self.cap = None
        except:
            pass

        # restart after short delay
        self.parent.after(300, self._restart_camera)

    def _restart_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.camera_active = True

    def release(self):
        self.cap.release()
        if self.out:
            self.out.release()
            self.out = None