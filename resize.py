import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageResizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer")

        self.image_path = ""
        self.canvas = tk.Canvas(root)
        self.canvas.pack(pady=10)

        self.btn_browse = tk.Button(root, text="Browse Image", command=self.browse_image)
        self.btn_browse.pack(pady=5)

        self.label_width = tk.Label(root, text="New Width:")
        self.label_width.pack()
        self.entry_width = tk.Entry(root)
        self.entry_width.pack(pady=5)

        self.label_height = tk.Label(root, text="New Height:")
        self.label_height.pack()
        self.entry_height = tk.Entry(root)
        self.entry_height.pack(pady=10)

        self.btn_resize = tk.Button(root, text="Resize Image", command=self.resize_image)
        self.btn_resize.pack(pady=10)

        # Variables for selection tool
        self.start_x = None
        self.start_y = None
        self.selection_rect = None

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def browse_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path = file_path
            self.show_image()

    def show_image(self):
        img = Image.open(self.image_path)
        img = img.resize((800, 600), Image.ADAPTIVE)
        photo = ImageTk.PhotoImage(img)

        self.canvas.config(width=img.width, height=img.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.photo = photo

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        self.canvas.coords(self.selection_rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        new_width = abs(end_x - self.start_x)
        new_height = abs(end_y - self.start_y)

        self.entry_width.delete(0, tk.END)
        self.entry_height.delete(0, tk.END)
        self.entry_width.insert(0, str(new_width))
        self.entry_height.insert(0, str(new_height))

        self.canvas.delete(self.selection_rect)

    def resize_image(self):
        try:
            new_width = int(self.entry_width.get())
            new_height = int(self.entry_height.get())
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Width and height must be positive integers.")

            original_image = cv2.imread(self.image_path)
            resized_image = cv2.resize(original_image, (new_width, new_height))

            cv2.imshow("Resized Image", resized_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizer(root)
    root.mainloop()
