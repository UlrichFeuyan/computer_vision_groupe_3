import tkinter as tk
from tkinter import colorchooser, messagebox, filedialog
import cv2
import numpy as np

from wcam import Webcam
from paint import FaceDetector


class DrawingApp:
    def __init__(self, root, width, height):
        self.root = root
        self.root.title("Dessin et Effacement")

        self.width = width
        self.height = height
        self.page_blanche = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()

        self.photo = self.convert_to_photo(self.page_blanche)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.photo = self.convert_to_photo(self.page_blanche)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Création de l'échelle pour le crayon
        self.pen_size_scale = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, label="Taille du crayon",
                                        command=self.update_pen_size)
        self.pen_size_scale.pack(side=tk.LEFT, padx=10, pady=10)
        self.pen_size = 5  # Taille par défaut du crayon

        # Création de l'échelle pour la gomme
        self.eraser_size_scale = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, label="Taille de la gomme",
                                          command=self.update_eraser_size)
        self.eraser_size_scale.pack(side=tk.LEFT, padx=10, pady=10)
        self.eraser_size = 10  # Taille par défaut de la gomme

        self.photo = self.convert_to_photo(self.page_blanche)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Ajout de la palette de couleurs
        self.color_palette_frame = tk.Frame(root)
        self.color_palette_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.colors = [
            (255, 0, 0),  # Rouge
            (0, 255, 0),  # Vert
            (0, 0, 255),  # Bleu
            (255, 255, 0),  # Jaune
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Violet
            (0, 255, 255),  # Cyan
            (255, 192, 203),  # Rose
            (128, 128, 128),  # Gris
            (0, 0, 0),  # Noir
        ]

        for color in self.colors:
            hex_color = self.rgb_to_hex(color)
            color_button = tk.Button(
                self.color_palette_frame,
                bg=hex_color,
                width=1,
                command=lambda c=color: self.set_active_color(c)
            )
            color_button.pack(side=tk.LEFT, padx=5)

        self.drawing_icon = tk.PhotoImage(file="images/icons8-stylo-48.png").subsample(3, 3)
        self.drawing_button = tk.Button(root, image=self.drawing_icon, command=self.enable_drawing, cursor="pencil")
        self.drawing_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.erasing_icon = tk.PhotoImage(file="images/icons8-gomme-50.png").subsample(3, 3)
        self.erasing_button = tk.Button(root, image=self.erasing_icon, command=self.enable_erasing)
        self.erasing_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.erasing_button.bind("<Button-1>", self.change_cursor_to_erase)

        self.color_icon = tk.PhotoImage(file="images/icons8-couleur-48.png").subsample(3, 3)
        self.color_button = tk.Button(root, image=self.color_icon, command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.tint_button = tk.Button(root, text="Teinter", command=self.apply_tint)
        self.tint_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.menu_bar = tk.Menu(root)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Nouveau", command=self.clear_canvas)
        self.file_menu.add_separator()

        self.file_submenu = tk.Menu(self.file_menu, tearoff=0)
        self.file_submenu.add_command(label="Insérer une image", command=self.insert_image)
        self.file_menu.add_cascade(label="Modifier l'image", menu=self.file_submenu)
        self.file_menu.add_separator()

        self.save_submenu = tk.Menu(self.file_menu, tearoff=0)
        self.save_submenu.add_command(label="Enregistrer", command=self.save_work)
        self.file_menu.add_cascade(label="Enregistrer le travail", menu=self.save_submenu)
        self.file_menu.add_separator()

        self.file_menu.add_command(label="Quitter", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Effacer tout", command=self.clear_canvas)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.about_menu.add_command(label="À propos", command=self.show_about_info)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)

        root.config(menu=self.menu_bar)

        self.active_button = None
        self.active_tool = None
        self.active_color = (0, 0, 0)  # Couleur par défaut

        self.drawing = False
        self.erasing = False
        self.ix, self.iy = -1, -1

        self.zoom_scale = 1.0

        self.canvas.bind("<B1-Motion>", self.draw_erase_line)
        self.canvas.bind("<ButtonRelease-1>", self.disable_drawing_erasing)
        self.canvas.bind("<B3-Motion>", self.draw_erase_line)
        self.canvas.bind("<ButtonRelease-3>", self.disable_drawing_erasing)

        self.blur_button = tk.Button(root, text="Flou", command=self.apply_blur_filter)
        self.blur_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.webcam_button = tk.Button(root, text="Ouvrir Webcam", command=self.open_webcam)
        self.webcam_button.pack(side=tk.LEFT, padx=10, pady=10)
        # ouvrir_webcam = tk.Button(root, text="Ouvrir Webcam", command=open_webcam(root))
        # ouvrir_webcam.pack()

        self.rotate_left_button = tk.Button(root, text="Rotation Gauche",
                                            command=lambda: self.rotate_image(cv2.ROTATE_90_COUNTERCLOCKWISE))
        self.rotate_left_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.rotate_right_button = tk.Button(root, text="Rotation Droite",
                                             command=lambda: self.rotate_image(cv2.ROTATE_90_CLOCKWISE))
        self.rotate_right_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.active_shape = None
        self.start_x = None
        self.start_y = None

        # Bouton pour dessiner des cercles
        self.cercle_button = tk.Button(root, text="Cercle", command=lambda: self.enable_cercle())
        self.cercle_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Bouton pour dessiner des rectangles
        self.rectangle_button = tk.Button(root, text="Rectangle", command=lambda: self.set_active_shape("Rectangle"))
        self.rectangle_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Canvas bindings pour dessiner les formes
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_shape)
        self.canvas.bind("<ButtonRelease-1>", self.end_drawing)


        self.tmp_x = 0
        self.tmp_y = 0

        self.fave_detector = FaceDetector

    def convert_to_photo(self, img):

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, img_encoded = cv2.imencode('.PPM', img_rgb)
        photo = tk.PhotoImage(data=img_encoded.tobytes())
        return photo

    def update_canvas(self):
        self.photo = self.convert_to_photo(self.page_blanche)
        self.canvas.itemconfig(self.image_item, image=self.photo)

    def enable_drawing(self):
        self.root.config(cursor="pencil")
        self.set_active_button(self.drawing_button, "Dessiner")

    def enable_erasing(self):
        self.set_active_button(self.erasing_button, "Effacer")

    def set_active_button(self, button, tool):
        if self.active_button:
            self.active_button.config(relief=tk.RAISED)
        button.config(relief=tk.SUNKEN)
        self.active_button = button
        self.active_tool = tool

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.active_color)
        if color[1]:
            self.active_color = tuple(int(val) for val in color[0])
            self.color_button.config(bg=self.rgb_to_hex(self.active_color))

    def rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

    def disable_drawing_erasing(self, event):
        self.root.config(cursor="")
        self.drawing = False
        self.erasing = False
        self.ix, self.iy = -1, -1

    def clear_canvas(self):
        self.page_blanche = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        self.update_canvas()

    def insert_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            img = cv2.imread(file_path)
            self.page_blanche = cv2.resize(img, (self.width, self.height))
            self.update_canvas()

    def save_work(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(self.page_blanche, cv2.COLOR_RGB2BGR))

    def show_about_info(self):
        about_text = "Cette application a été créée pour dessiner et effacer."
        messagebox.showinfo("À propos", about_text)

    def change_cursor_to_erase(self, event):
        self.root.config(cursor="X_cursor")

    def set_active_color(self, color):
        self.active_color = color

    def apply_blur_filter(self):
        blurred_img = cv2.GaussianBlur(self.page_blanche, (15, 15), 0)
        self.page_blanche = blurred_img
        self.update_canvas()




    # METHODE DE LA WEBCAM
    def open_webcam(self):
        # self.webcam = Webcam(tk.Toplevel(self.root),self)  # Crée une instance de la webcam dans une nouvelle fenêtre
        self.fave_detector = FaceDetector(tk.Toplevel(self.root),self)
    def load_webcam_image(self, frame):
        # Convertir l'image de la webcam (frame) en un format compatible avec votre zone de dessin
        # Par exemple, si self.page_blanche est la zone de dessin principale :
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(img_rgb, (self.width, self.height))

        # Charger l'image capturée depuis la webcam dans la zone de dessin
        self.page_blanche = resized_frame
        self.update_canvas()



    def rotate_image(self, angle):
        self.page_blanche = cv2.rotate(self.page_blanche, angle)  # Rotation de l'image
        self.update_canvas()

    def apply_tint(self):
        tint_color = colorchooser.askcolor(initialcolor=self.active_color)
        if tint_color[1]:
            self.active_color = tuple(int(val) for val in tint_color[0])

            # Création d'une matrice de la taille de l'image remplie de la couleur sélectionnée
            tinted_matrix = np.full((self.height, self.width, 3), self.active_color, dtype=np.uint8)

            # Appliquer le mélange pondéré (alpha blend) à l'image
            alpha = 0.5  # Modifier cette valeur pour ajuster l'intensité du tint
            self.page_blanche = cv2.addWeighted(self.page_blanche, 1 - alpha, tinted_matrix, alpha, 0)

            self.update_canvas()

    # FIN DES METHODE WEBCAM





    def update_canvas(self):
        self.photo = self.convert_to_photo(self.page_blanche)
        self.canvas.itemconfig(self.image_item, image=self.photo)

    def update_pen_size(self, size):
        self.pen_size = int(size)

    def update_eraser_size(self, size):
        self.eraser_size = int(size)

    def draw_erase_line(self, event):
        if self.active_tool:
            x, y = event.x, event.y
            if self.ix == -1 and self.iy == -1:
                self.ix, self.iy = x, y
            if self.active_tool == "Effacer":
                color = (255, 255, 255)
                size = self.eraser_size
            else:
                color = self.active_color
                size = self.pen_size
            cv2.line(self.page_blanche, (self.ix, self.iy), (x, y), color, size)
            self.ix, self.iy = x, y
            self.update_canvas()


    def set_active_shape(self, shape):
        self.active_shape = shape

    def start_drawing(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def end_drawing(self, event):
        self.start_x = None
        self.start_y = None

    def draw_shape(self, event):
        if self.active_shape and self.start_x is not None and self.start_y is not None:
            x, y = event.x, event.y
            if self.active_shape == "Circle":
                self.draw_circle(self.start_x, self.start_y, x, y)
            elif self.active_shape == "Rectangle":
                self.draw_rectangle(self.start_x, self.start_y, x, y)

    # def draw_circle(self, start_x, start_y, end_x, end_y):
    #     # Calculer le rayon
    #     radius = int(((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5)
    #     color = self.active_color
    #     self.page_blanche = self.page_blanche.copy()  # Créez une copie de la page pour dessiner sans modifier l'original
    #     cv2.circle(self.page_blanche, (start_x, start_y), radius, color, -1)
    #     self.update_canvas()

    def draw_temp_circle(self, event):
        if self.active_tool == "Cercle" and self.drawing:
            x, y = event.x, event.y
            radius = max(abs(self.ix - x), abs(self.iy - y))
            self.canvas.delete("temp_circle")  # Supprime le cercle temporaire précédent
            self.canvas.create_oval(self.ix - radius, self.iy - radius, self.ix + radius, self.iy + radius,
                                    outline=self.rgb_to_hex(self.active_color), tags="temp_circle")

    def draw_circle_on_release(self, event):
        if self.active_tool == "Cercle":
            x, y = event.x, event.y
            radius = max(abs(self.ix - x), abs(self.iy - y))
            self.canvas.create_oval(self.ix - radius, self.iy - radius, self.ix + radius, self.iy + radius,
                                    outline=self.rgb_to_hex(self.active_color))
            self.drawing = False
            self.canvas.delete("temp_circle")  # Supprime le cercle temporaire à la fin du dessin

    # ... (votre code existant)

    def enable_cercle(self):
        self.set_active_button(self.cercle_button, "Cercle")
        self.canvas.bind("<ButtonPress-1>", self.set_start_point)
        self.canvas.bind("<B1-Motion>", self.draw_temp_circle)
        self.canvas.bind("<ButtonRelease-1>", self.draw_circle_on_release)
    def draw_rectangle(self, start_x, start_y, end_x, end_y):
        color = self.active_color
        self.page_blanche = self.page_blanche.copy()  # Créez une copie de la page pour dessiner sans modifier l'original
        cv2.rectangle(self.page_blanche, (start_x, start_y), (end_x, end_y), color, -1)
        self.update_canvas()

    def set_start_point(self, event):
        self.ix, self.iy = event.x, event.y
if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root, width=800, height=600)
    root.mainloop()
