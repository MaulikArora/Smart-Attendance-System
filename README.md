# Smart-Attendance-System
An AI-powered smart attendance system that uses real-time face recognition to automatically mark student attendance.

The system integrates computer vision (OpenCV), a Python-based UI, and a backend to create a scalable and automated attendance solution.

## Features

- Real-time face detection and recognition via webcam/CCTV
- Automated attendance marking
- Python-based UI for managing system operations
- Scalable architecture (Laptop detection + API backend)
- Reduced manual effort and improved accuracy

## Tech Stack

- Python
- OpenCV
- Tkinter (for UI)
- SQLite (or your DB)

## System Architecture

1. Camera captures live video feed
2. Face recognition matches with stored encodings
3. Attendance is marked automatically
4. Data is sent to backend
5. Backend stores attendance records

## Future Improvements

- Mobile app integration for attendance tracking
- Real-time notifications
- Liveness detection (anti-spoofing)
- Cloud deployment
- Multi-camera support

<img width="1600" height="954" alt="image" src="https://github.com/user-attachments/assets/26d20705-8ee0-40be-9833-a7ae112baf2f" />

## Installation and Setup

1. Clone the repository
2. Install dependencies: pip install -r requirements.txt
3. Run the register_students script to add the first student manually: python register_students.py
     - When the camera opens press c to capture, fill student details in the terminal and switch back to the camera tab and press q to exit.
4. Run the root script: python main.py
     - Press start class to run detection, wait for the 6 checks then once the button turns red press end class to save attendance and the camera recording.
     - In the records tab select the date and time from dropdown menu to access the attendacne records
     - In footage tab select the date and time from dropdown menu to access saved footage of the class
     - In students tab, you can see details of all registered students and add more students using the Add Student button.
