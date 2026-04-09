import tkinter as tk
from tkinter import ttk
import os
import cv2
from PIL import Image, ImageTk

BG = "#eef3fb"
CARD_BG = "#ffffff"
BORDER = "#dbe3f0"
TEXT = "#1f2937"
SUBTEXT = "#64748b"


class FootageTab:
    def __init__(self, parent):
        self.parent = parent
        self.parent.configure(bg=BG)

        self.video_var = tk.StringVar()
        self.cap = None

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
            text="Recorded Footage",
            font=("Segoe UI", 18, "bold"),
            bg=CARD_BG,
            fg=TEXT
        )
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))

        subtitle = tk.Label(
            header_card,
            text="Choose a saved class recording to review",
            font=("Segoe UI", 10),
            bg=CARD_BG,
            fg=SUBTEXT
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        select_card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        select_card.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        select_card.columnconfigure(1, weight=1)

        select_label = tk.Label(
            select_card,
            text="Recording",
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=TEXT
        )
        select_label.grid(row=0, column=0, sticky="w", padx=(16, 10), pady=14)

        self.dropdown = ttk.Combobox(
            select_card,
            textvariable=self.video_var,
            width=40,
            font=("Segoe UI", 12),
            style="Modern.TCombobox",
            state="readonly"
        )
        self.dropdown.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=14)

        preview_card = tk.Frame(
            parent,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER
        )
        preview_card.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 12))
        preview_card.rowconfigure(0, weight=1)
        preview_card.columnconfigure(0, weight=1)

        self.video_label = tk.Label(
            preview_card,
            bg="#dfe8f6",
            fg=SUBTEXT,
            text="Select a recording to play",
            font=("Segoe UI", 13)
        )
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        self.status_label = tk.Label(
            parent,
            text="Ready",
            font=("Segoe UI", 11),
            bg=BG,
            fg=SUBTEXT
        )
        self.status_label.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 20))

        self.dropdown.bind("<<ComboboxSelected>>", self.play_video)

        self.load_videos()

    def load_videos(self):
        folder = "footage"

        if os.path.exists(folder):
            files = sorted(os.listdir(folder), reverse=True)
            self.dropdown["values"] = files

            if self.video_var.get() not in files:
                self.video_var.set("")

            if files:
                self.status_label.config(text="Select a recording to play")
            else:
                self.status_label.config(text="No recordings found")
                self.video_label.config(text="No recordings found", image="")
        else:
            self.dropdown["values"] = []
            self.video_var.set("")
            self.status_label.config(text="Footage folder not found")
            self.video_label.config(text="Footage folder not found", image="")

    def play_video(self, event=None):
        file = self.video_var.get()

        if not file:
            return

        if self.cap:
            self.cap.release()

        path = f"footage/{file}"

        if not os.path.exists(path):
            self.status_label.config(text="File not found")
            return

        self.cap = cv2.VideoCapture(path)
        self.status_label.config(text=f"Playing: {file}")
        self.video_label.config(text="")
        self.update_video()

    def update_video(self):
        if self.cap:
            ret, frame = self.cap.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                target_w = self.video_label.winfo_width()
                target_h = self.video_label.winfo_height()

                if target_w > 100 and target_h > 100:
                    fh, fw, _ = frame.shape
                    scale = min(target_w / fw, target_h / fh)
                    new_w = max(1, int(fw * scale))
                    new_h = max(1, int(fh * scale))

                    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    canvas = Image.new("RGB", (target_w, target_h), (223, 232, 246))
                    x = (target_w - new_w) // 2
                    y = (target_h - new_h) // 2
                    canvas.paste(Image.fromarray(resized), (x, y))
                    img = ImageTk.PhotoImage(canvas)
                else:
                    img = ImageTk.PhotoImage(Image.fromarray(frame))

                self.video_label.imgtk = img
                self.video_label.config(image=img, text="")
                self.parent.after(16, self.update_video)

            else:
                self.cap.release()
                self.cap = None
                self.status_label.config(text="Playback finished")

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None