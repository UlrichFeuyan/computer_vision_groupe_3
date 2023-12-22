import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageFaceDetectionApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.image_path = ""

        self.canvas = tk.Canvas(window)
        self.canvas.pack()

        self.btn_open = tk.Button(window, text="Open Image", command=self.open_image)
        self.btn_open.pack(pady=10)

        self.btn_detect_faces = tk.Button(window, text="Detect Faces", command=self.detect_faces)
        self.btn_detect_faces.pack(pady=10)

        self.window.mainloop()

    def open_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        self.show_image()

    def show_image(self):
        if self.image_path:
            image = Image.open(self.image_path)
            photo = ImageTk.PhotoImage(image=image)
            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.image = photo

    def detect_faces(self):
        if self.image_path:
            image = cv2.imread(self.image_path)
            faces = self.detect_faces_in_image(image)

            # Draw rectangles around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Display the image with face rectangles
            image_with_faces = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_with_faces = Image.fromarray(image_with_faces)
            photo = ImageTk.PhotoImage(image=image_with_faces)

            self.canvas.config(width=photo.width(), height=photo.height())
            self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.canvas.image = photo

    def detect_faces_in_image(self, image):
        # Convert the image to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Load the Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        return faces

# Create a window and pass it to ImageFaceDetectionApp
root = tk.Tk()
app = ImageFaceDetectionApp(root, "Image Face Detection App")
root.mainloop()
