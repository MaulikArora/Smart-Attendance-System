import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition  # type: ignore
import pickle
import os
from PIL import Image, ImageTk

BG = "#eef3fb"
CARD_BG = "#ffffff"
BORDER = "#dbe3f0"
TEXT = "#1f2937"
ACCENT = "#4f8cff"


class StudentsTab:
    def __init__(self, parent, go_back_callback):
        self.parent = parent
        self.go_back = go_back_callback
        self.parent.configure(bg=BG)

        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(fill="both", expand=True)

        title = tk.Label(
            self.frame,
            text="Registered Students",
            font=("Segoe UI", 18, "bold"),
            bg=BG,
            fg=TEXT
        )
        title.pack(anchor="w", padx=20, pady=10)

        self.tree = ttk.Treeview(
            self.frame,
            columns=("Name", "Reg"),
            show="headings"
        )
        self.tree.heading("Name", text="Name")
        self.tree.heading("Reg", text="Reg No")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        btn = tk.Button(
            self.frame,
            text="+ Add Student",
            bg=ACCENT,
            fg="white",
            command=self.open_add_student
        )
        btn.pack(anchor="e", padx=20, pady=10)

        self.load_students()

    def load_students(self):
        self.tree.delete(*self.tree.get_children())

        if not os.path.exists("encodings.pkl"):
            return

        with open("encodings.pkl", "rb") as f:
            data = pickle.load(f)

        for s in data["students"]:
            self.tree.insert("", "end", values=(s["name"], s["reg_no"]))

    def open_add_student(self):
        if hasattr(self.parent.master.master, "live_tab"):
            self.parent.master.master.live_tab.pause_camera()

        AddStudentWindow(self)


class AddStudentWindow:
    def __init__(self, parent_tab):
        self.parent_tab = parent_tab
        self.root = parent_tab.parent.master.master

        self.win = tk.Toplevel()
        self.win.title("Add Student")
        self.win.geometry("900x500")
        self.win.configure(bg=BG)

        self.cap = cv2.VideoCapture(0)
        self.captured_frame = None

        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

        self.win.columnconfigure(0, weight=3)
        self.win.columnconfigure(1, weight=1)

        self.video_label = tk.Label(self.win, bg="black")
        self.video_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        right = tk.Frame(self.win, bg=CARD_BG)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        tk.Label(right, text="Name", bg=CARD_BG).pack(pady=5)
        self.name_entry = tk.Entry(right)
        self.name_entry.pack(pady=5)

        tk.Label(right, text="Reg No", bg=CARD_BG).pack(pady=5)
        self.reg_entry = tk.Entry(right)
        self.reg_entry.pack(pady=5)

        self.capture_btn = tk.Button(right, text="Capture", command=self.capture)
        self.capture_btn.pack(pady=10)

        self.save_btn = tk.Button(right, text="Save Student", command=self.save)
        self.save_btn.pack(pady=10)

        self.update()

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.video_label.imgtk = img
            self.video_label.config(image=img)

        self.win.after(10, self.update)

    def capture(self):
        ret, frame = self.cap.read()
        if ret:
            self.captured_frame = frame
            messagebox.showinfo("Captured", "Image captured successfully")

    def save(self):
        name = self.name_entry.get()
        reg = self.reg_entry.get()

        if self.captured_frame is None:
            messagebox.showerror("Error", "Capture image first")
            return

        rgb = cv2.cvtColor(self.captured_frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)

        if not encodings:
            messagebox.showerror("Error", "No face detected")
            return

        encoding = encodings[0]

        if os.path.exists("encodings.pkl"):
            with open("encodings.pkl", "rb") as f:
                data = pickle.load(f)
        else:
            data = {"encodings": [], "students": []}

        # override logic
        for i, s in enumerate(data["students"]):
            if s["reg_no"] == reg:
                data["students"][i] = {"name": name, "reg_no": reg}
                data["encodings"][i] = encoding
                break
        else:
            data["students"].append({"name": name, "reg_no": reg})
            data["encodings"].append(encoding)

        with open("encodings.pkl", "wb") as f:
            pickle.dump(data, f)

        messagebox.showinfo("Success", "Student saved")

        if hasattr(self.root, "refresh_live_data"):
            self.root.refresh_live_data()

        if hasattr(self.root, "live_tab"):
            self.root.live_tab.resume_camera()

        self.cap.release()
        self.win.destroy()

        self.parent_tab.load_students()

    def on_close(self):
        if self.cap:
            self.cap.release()

        if hasattr(self.root, "live_tab"):
            self.root.live_tab.resume_camera()

        self.win.destroy()