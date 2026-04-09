import cv2
import face_recognition # type: ignore
import pickle

known_encodings = []
known_data = []   # will store name + reg no

# try loading existing data (so you can add more students later)
try:
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
        known_encodings = data["encodings"]
        known_data = data["students"]
except:
    print("No existing data found. Creating new database...")

cap = cv2.VideoCapture(0)

while True:
    print("\nPress 'c' to capture face, 'q' to quit")

    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Register Student", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, faces)

        if len(encodings) == 0:
            print("No face detected. Try again.")
            continue

        if len(encodings) > 1:
            print("Multiple faces detected. Only one person at a time.")
            continue

        # get student details
        name = input("Enter Student Name: ")
        reg_no = input("Enter Registration Number: ")

        # store encoding
        known_encodings.append(encodings[0])
        known_data.append({
            "name": name,
            "reg_no": reg_no
        })

        print(f"Registered: {name} ({reg_no})")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# save data
data = {
    "encodings": known_encodings,
    "students": known_data
}

with open("encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print("\nAll data saved successfully!")