from tkinter import filedialog

import cv2
import tkinter as tk
from PIL import Image, ImageTk
# #
# # class WebcamApp:
# #     def __init__(self, root):
# #         self.root = root
# #         self.root.title("Webcam")
# #
# #         self.cap = cv2.VideoCapture(0)  # Ouvre la webcam
# #
# #         self.frame = tk.Label(root)
# #         self.frame.pack()
# #
# #         self.capture_button = tk.Button(root, text="Prendre une photo", command=self.take_snapshot)
# #         self.capture_button.pack()
# #
# #         self.photo = None
# #         self.update_frame()
# #
# #     def take_snapshot(self):
# #         ret, frame = self.cap.read()  # Capture une image
# #         if ret:
# #             cv2.imwrite("captured_image.png", frame)  # Enregistre l'image capturée
# #
# #     def update_frame(self):
# #         ret, frame = self.cap.read()  # Capture une image
# #         if ret:
# #             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #             self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
# #             self.frame.config(image=self.photo)
# #         self.root.after(10, self.update_frame)  # Met à jour la frame toutes les 10 ms
# #
# # if __name__ == "__main__":
# #     root = tk.Tk()
# #     app = WebcamApp(root)
# #     root.mainloop()
#
#
#
# class Webcam:
#     def __init__(self, root):
#
#
#         self.root = root
#         self.root.title("Webcam")
#
#         self.cap = cv2.VideoCapture(0)  # Ouvre la webcam
#
#         self.frame = tk.Label(root)
#         self.frame.pack()
#
#         self.capture_button = tk.Button(root, text="Prendre une photo", command=self.take_snapshot)
#         self.capture_button.pack()
#
#         self.photo = None
#         self.update_frame()
#
#     def take_snapshot(self):
#         ret, frame = self.cap.read()  # Capture une image
#         if ret:
#             cv2.imwrite("captured_image.png", frame)  # Enregistre l'image capturée
#
#     def update_frame(self):
#         ret, frame = self.cap.read()  # Capture une image
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
#             self.frame.config(image=self.photo)
#         self.root.after(10, self.update_frame)  # Met à jour la frame toutes les 10 ms
#
# def open_webcam():
#     webcam = Webcam(root)
#     webcam.take_photo()
#
# root = tk.Tk()
#
# ouvrir_webcam = tk.Button(root, text="Ouvrir Webcam", command=open_webcam)
# ouvrir_webcam.pack()
#
# root.mainloop()

class Webcam:
    def __init__(self, root,drawing_app):
        self.root = root
        self.root.title("Webcam")
        self.drawing_app = drawing_app


        self.cap = cv2.VideoCapture(0)  # Ouvre la webcam

        self.frame = tk.Label(root)
        self.frame.pack()

        self.capture_button = tk.Button(root, text="Prendre une photo", command=self.take_snapshot)
        self.capture_button.pack()

        self.photo = None
        self.update_frame()

    def take_snapshot(self):
        ret, frame = self.cap.read()  # Capture une image
        if ret:
            cv2.imwrite("captured_image.png", frame)  # Enregistre l'image capturée
            # self.page_blanche = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Charge l'image dans la page blanche
            # self.update_canvas()
        # cap.release()


            self.drawing_app.load_webcam_image(frame)

    def take_webcam_snapshot(self):
        if hasattr(self, 'webcam'):
            # Capture d'une image depuis la webcam
            frame = self.webcam.capture_frame()

            # Enregistrement de l'image dans un fichier
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Sauvegarde au format PNG

                # Charger l'image dans la page_blanche
                img = cv2.imread(file_path)
                self.page_blanche = cv2.resize(img, (self.width, self.height))
                self.update_canvas()  # Mettre à jour la page blanche avec la nouvelle image

    def update_frame(self):
        ret, frame = self.cap.read()  # Capture une image
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.frame.config(image=self.photo)
        self.root.after(10, self.update_frame)  # Met à jour la frame toutes les 10 ms



