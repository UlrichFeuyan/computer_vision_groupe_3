import cv2
import tkinter as tk
from PIL import Image, ImageTk


class FaceDetector:
    def __init__(self, root,drawing_app):
        self.root = root
        self.root.title("Face Detection")
        self.drawing_app = drawing_app
        # Create canvas
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create buttons
        self.create_button("Start Detection", self.start_detection, row=1, column=0)
        self.create_button("Stop Detection", self.stop_detection, row=1, column=1)
        self.create_button("Prendre une photo", self.take_snapshot, row=1, column=3)

        # Webcam and face detector
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_detecting = False

        # After every 10 milliseconds, update the webcam frame
        self.root.after(10, self.update)

        self.update_frame()
    def take_snapshot(self):
        ret, frame = self.cap.read()  # Capture une image
        if ret:
            cv2.imwrite("captured_image.png", frame)  # Enregistre l'image capturée
            # self.page_blanche = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Charge l'image dans la page blanche
            # self.update_canvas()
            # cap.release()

            self.drawing_app.load_webcam_image(frame)
    def update_frame(self):
        ret, frame = self.cap.read()  # Capture une image
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.frame.config(image=self.photo)
        self.root.after(10, self.update_frame)


    def create_button(self, text, command, row, column):
        button = tk.Button(self.root, text=text, command=command)
        button.grid(row=row, column=column)

    def start_detection(self):
        self.is_detecting = True

    def stop_detection(self):
        self.is_detecting = False

    def update(self):
        if self.is_detecting:
            # Read frame from webcam
            ret, frame = self.cap.read()

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Blur and draw rectangles around the faces
            for (x, y, w, h) in faces:
                face_region = frame[y:y + h, x:x + w]
                face_region = cv2.GaussianBlur(face_region, (99, 99), 30)
                frame[y:y + face_region.shape[0], x:x + face_region.shape[1]] = face_region

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                label = "Person" if self.is_person(frame, x, y, w, h) else "Not person"
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the frame
            self.display_frame(frame)

        # After 10 milliseconds, call the update function again
        self.root.after(10, self.update)

    def is_person(self, frame, x, y, w, h):
        # Additional checks to determine if it's a person (you can customize these checks)
        # For example, you can use facial recognition libraries for better accuracy
        return True  # Placeholder, replace with actual person detection logic

    def display_frame(self, frame):
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.canvas_width, self.canvas_height))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.photo = photo

    def __del__(self):
        # Release the webcam when the object is deleted
        if self.cap.isOpened():
            self.cap.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDetector(root)
    root.mainloop()
