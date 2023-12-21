import os
import tkinter as tk
from tkinter import *
from tkinter import colorchooser, filedialog, messagebox
from tkinter.ttk import *
from collections import deque
import cv2
import numpy as np
from wcam import Webcam



class PaintApp:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        self.root.minsize(self.width,self.height)
        self.root.title('Untitled - Painter')

        self.menu_frame = Frame(root)
        self.menu_frame.place(x=0, y=0, relwidth=1, relheight=0.2)
        self.main_frame = Frame(root)
        self.main_frame.place(x=0, rely=0.2, relwidth=1, relheight=0.8)

        self.page_blanche = np.ones((600, 800, 3), dtype=np.uint8) * 255
        self.menu_frame.columnconfigure((0, 1, 2), weight=1)
        self.menu_frame.rowconfigure(0, weight=1)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.main_frame, width=800, height=600)
        self.canvas.grid(row=1, column=0)

        self.setup_navbar()
        self.main_frames()
        self.active_button = None
        self.active_tool = None
        self.active_color = (0, 0, 0)  # Couleur par défaut

        self.drawing = True
        self.erasing = False
        self.ix, self.iy = -1, -1

        self.canvas.bind("<B1-Motion>", self.draw_erase_line)
        self.canvas.bind("<ButtonRelease-1>", self.disable_drawing_erasing)



    def select_size(self, size):
        self.selected_size = size

    def open_webcam(self):
        self.webcam = Webcam(tk.Toplevel(self.root),self)  # Crée une instance de la webcam dans une nouvelle fenêtre

    def load_webcam_image(self, frame):
        # Convertir l'image de la webcam (frame) en un format compatible avec votre zone de dessin
        # Par exemple, si self.page_blanche est la zone de dessin principale :
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized_frame = cv2.resize(img_rgb, (self.width, self.height))

        # Charger l'image capturée depuis la webcam dans la zone de dessin
        self.page_blanche = resized_frame
        self.update_canvas()

    def main_frames(self):
        self.tool_frame = LabelFrame(self.menu_frame, text="Tools")
        self.tool_frame.grid(row=0, column=0)
        self.other_frame = LabelFrame(self.menu_frame, text="Interactive")
        self.other_frame.grid(row=0, column=1)

        self.image_frame = LabelFrame(self.menu_frame, text="Image")
        self.image_frame.grid(row=0, column=2)

        self.canvas = tk.Canvas(self.main_frame, width=800, height=600)
        self.canvas.grid(row = 1, column = 0)

        self.photo = self.convert_to_photo(self.page_blanche)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.drawing_icon = tk.PhotoImage(file='images/pencil.png')
        self.drawing_button = Button(self.tool_frame, image=self.drawing_icon, command=self.enable_drawing)
        self.drawing_button.grid(row = 0, column = 0)

        self.brush_sizes = [1, 3, 9, 13, 17, 21, 30]
        self.selected_size = self.brush_sizes[0]
        self.brush_size_label = Label(self.tool_frame, text="Epaisseur")
        self.brush_size_label.grid(row = 1, column = 0)
        self.brush_size_label = Label(self.tool_frame, text="Gomme")
        self.brush_size_label.grid(row=1, column=1)
        self.brush_size_label = Label(self.tool_frame, text="Couleur")
        self.brush_size_label.grid(row=1, column=2)

        self.brush_size_combobox = Combobox(self.tool_frame, values=self.brush_sizes, state="readonly")
        self.brush_size_combobox.current(0)
        self.brush_size_combobox.grid(row = 2, column = 0,sticky= NS)
        self.brush_size_combobox.bind("<<ComboboxSelected>>",
                                      lambda event: self.select_size(int(self.brush_size_combobox.get())))

        self.erasing_icon = tk.PhotoImage(file='images/eraser.png')
        self.erasing_button = Button(self.tool_frame, image=self.erasing_icon, command=self.enable_erasing)
        self.erasing_button.grid(row = 0, column = 1)

        self.color_icon = tk.PhotoImage(file='images/color.png')#.subsample(13, 13)
        self.color_button = Button(self.tool_frame, image=self.color_icon, command=self.choose_color)
        self.color_button.grid(row = 0, column = 2)

        self.cam = tk.PhotoImage(file='images/camera.png')
        self.live = tk.PhotoImage(file='images/live_draw.png')
        self.blur = tk.PhotoImage(file='images/blur.png')
        self.fill = tk.PhotoImage(file='images/fill.png')
        self.lf = tk.PhotoImage(file='images/rotate_left.png')
        self.rg = tk.PhotoImage(file='images/rotate_right.png')
        self.tri = tk.PhotoImage(file='images/triangle.png')
        self.cir = tk.PhotoImage(file='images/circle.png')

        Button(self.image_frame, image= self.fill, command=self.apply_tint).grid(row = 0, column = 0)
        Button(self.image_frame, image= self.lf, command= lambda: self.rotate_image(cv2.ROTATE_90_COUNTERCLOCKWISE)).grid(row = 0, column = 1)
        Button(self.image_frame, image= self.rg, command= lambda: self.rotate_image(cv2.ROTATE_90_CLOCKWISE)).grid(row=0, column=2)
        Button(self.image_frame, text="Flouter", image=self.blur, command=self.apply_blur_filter).grid(row=0, column=3)
        #self.circle = Button(self.image_frame, image=self.cir, command=lambda: self.enable_cercle()).grid(row=0, column=4)
        #triangle = Button(self.image_frame, image=self.tri, command=lambda: self.set_active_shape("Rectangle")).grid(row=0, column=5)

        Button(self.other_frame, image= self.cam, command= self.open_webcam).grid(row = 0, column = 0)
        Button(self.other_frame, image = self.live, command= open('live_draw.py')).grid(row = 0, column = 1)




        self.brush_size_label = Label(self.image_frame, text="Teindre")
        self.brush_size_label.grid(row=1, column=0)
        self.brush_size_label = Label(self.image_frame, text="Droite")
        self.brush_size_label.grid(row=1, column=1)
        self.brush_size_label = Label(self.image_frame, text="Gauche")
        self.brush_size_label.grid(row=1, column=2)
        self.brush_size_label = Label(self.image_frame, text="Flouter")
        self.brush_size_label.grid(row=1, column=3)
        #self.brush_size_label = Label(self.image_frame, text="Cercle")
        #self.brush_size_label.grid(row=1, column=4)
        #self.brush_size_label = Label(self.image_frame, text="Triangle")
        #self.brush_size_label.grid(row=1, column=5)

        self.brush_size_label = Label(self.other_frame, text='Photo')
        self.brush_size_label.grid(row=1, column=0)
        self.brush_size_label = Label(self.other_frame, text="Dessin live")
        self.brush_size_label.grid(row=1, column=1)

    def set_active_shape(self, shape):
        self.active_shape = shape
    def set_start_point(self, event):
        self.ix, self.iy = event.x, event.y

    def draw_temp_circle(self, event):
        if self.active_tool == "Cercle" and self.drawing:
            x, y = event.x, event.y
            radius = max(abs(self.ix - x), abs(self.iy - y))
            self.canvas.delete("temp_circle")  # Supprime le cercle temporaire précédent
            self.canvas.create_oval(self.ix - radius, self.iy - radius, self.ix + radius, self.iy + radius,
                                    outline=self.rgb_to_hex(self.active_color), tags="temp_circle")


    def enable_cercle(self):
        self.set_active_button(self.circle, "Cercle")
        self.canvas.bind("<ButtonPress-1>", self.set_start_point)
        self.canvas.bind("<B1-Motion>", self.draw_temp_circle)
        self.canvas.bind("<ButtonRelease-1>", self.draw_circle_on_release)

    def draw_circle_on_release(self, event):
        if self.active_tool == "Cercle":
            x, y = event.x, event.y
            radius = max(abs(self.ix - x), abs(self.iy - y))
            self.canvas.create_oval(self.ix - radius, self.iy - radius, self.ix + radius, self.iy + radius,
                                    outline=self.rgb_to_hex(self.active_color))
            self.drawing = False
            self.canvas.delete("temp_circle")  # Supprime le cercle temporaire à la fin du dessin

    # ... (votre code existant)

    def draw_rectangle(self, start_x, start_y, end_x, end_y):
        color = self.active_color
        self.page_blanche = self.page_blanche.copy()  # Créez une copie de la page pour dessiner sans modifier l'original
        cv2.rectangle(self.page_blanche, (start_x, start_y), (end_x, end_y), color, -1)
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
    def apply_blur_filter(self):
        blurred_img = cv2.GaussianBlur(self.page_blanche, (15, 15), 0)
        self.page_blanche = blurred_img
        self.update_canvas()

    def setup_navbar(self):
        self.menu_bar = tk.Menu(root)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Page vide", command=self.clear_canvas)
        self.file_menu.add_separator()

        self.file_submenu = tk.Menu(self.file_menu, tearoff=0)
        self.file_submenu.add_command(label="Insérer une image", command=self.insert_image)
        self.file_menu.add_cascade(label="Nouveau", menu=self.file_submenu)
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

    def convert_to_photo(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, img_encoded = cv2.imencode('.PPM', img_rgb)
        photo = tk.PhotoImage(data=img_encoded.tobytes())
        return photo

    def update_canvas(self):
        self.photo = self.convert_to_photo(self.page_blanche)
        self.canvas.itemconfig(self.image_item, image=self.photo)

    def enable_drawing(self):
        self.set_active_button(self.drawing_button, "Dessiner")

    def enable_erasing(self):
        self.set_active_button(self.erasing_button, "Effacer")

    def set_active_button(self, button, tool):
        #if self.active_button:
        #    self.active_button.config(relief=tk.RAISED)
        #button.config(relief=tk.SUNKEN)
        self.active_button = button
        self.active_tool = tool

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.active_color)
        if color[1]:  # S'assurer qu'une couleur a été sélectionnée
            self.active_color = tuple(int(val) for val in color[0])
            self.color_button.config(bg=self.rgb_to_hex(self.active_color))

    def rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

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

    def draw_erase_line(self, event):
        if self.active_tool:
            x, y = event.x, event.y
            if self.ix == -1 and self.iy == -1:
                self.ix, self.iy = x, y
            if self.active_tool == "Effacer":
                color = (255, 255, 255)
            else:
                color = self.active_color
            cv2.line(self.page_blanche, (self.ix, self.iy), (x, y), color, self.selected_size)
            self.ix, self.iy = x, y
            self.update_canvas()

    def disable_drawing_erasing(self, event):
        self.drawing = False
        self.erasing = False
        self.ix, self.iy = -1, -1


if __name__ == "__main__":
    root = tk.Tk()
    PaintApp(root, 800, 600)
    root.mainloop()