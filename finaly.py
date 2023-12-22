import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class WebcamFaceBlurApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.face_detector_path = "haarcascade_frontalface_default.xml"
        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + self.face_detector_path)

        self.cap = cv2.VideoCapture(0)

        self.canvas = tk.Canvas(window)
        self.canvas.pack()

        self.btn_start = ttk.Button(window, text="Start", command=self.start)
        self.btn_start.pack(pady=10)

        self.btn_stop = ttk.Button(window, text="Stop", command=self.stop, state="disabled")
        self.btn_stop.pack(pady=10)

        self.processing = False
        self.update_frame()

    def start(self):
        self.btn_start["state"] = "disabled"
        self.btn_stop["state"] = "normal"
        self.processing = True

    def stop(self):
        self.btn_start["state"] = "normal"
        self.btn_stop["state"] = "disabled"
        self.processing = False

    def update_frame(self):
        if self.processing:
            ret, frame = self.cap.read()

            if ret:
                blurred_frame = self.blur_faces(frame)
                self.display_frame(blurred_frame)

        self.window.after(10, self.update_frame)

    def blur_faces(self, img):
        # Apply blur to the frame
        blurred_img = self.blur_img(img, factor=20)

        # Detect faces in the original frame
        faces = self.face_detector.detectMultiScale(img, 1.3, 5)

        # Replace corresponding regions in the blurred frame with original detected faces
        for x, y, w, h in faces:
            detected_face = img[int(y):int(y + h), int(x):int(x + w)]
            blurred_img[y:y + h, x:x + w] = detected_face

        return blurred_img

    def blur_img(self, img, factor):
        kW = int(img.shape[1] / factor)
        kH = int(img.shape[0] / factor)

        # Ensure the shape of the kernel is odd
        if kW % 2 == 0: kW = kW - 1
        if kH % 2 == 0: kH = kH - 1

        blurred_img = cv2.GaussianBlur(img, (kW, kH), 0)
        return blurred_img

    def display_frame(self, frame):
        # Display the result in the Tkinter window
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=img)

        self.canvas.config(width=photo.width(), height=photo.height())
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamFaceBlurApp(root, "Webcam Face Blur App")
    root.mainloop()
