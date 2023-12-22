import numpy as np
import cv2
from collections import deque
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab


class LiveDraw:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.camera = cv2.VideoCapture(0)
        self.kernel = np.ones((5, 5), np.uint8)
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
        self.color_index = 0

        self.bpoints = [deque(maxlen=512)]
        self.gpoints = [deque(maxlen=512)]
        self.rpoints = [deque(maxlen=512)]
        self.ypoints = [deque(maxlen=512)]

        self.bindex = 0
        self.gindex = 0
        self.rindex = 0
        self.yindex = 0

        self.paint_interface = np.zeros((471, 636, 3)) + 255
        self.create_paint_interface()

        self.canvas = tk.Canvas(window)
        self.canvas.pack(side=tk.LEFT)

        self.video_canvas = tk.Canvas(window)
        self.video_canvas.pack(side=tk.RIGHT)

        self.update()

        self.save_button = tk.Button(self.window, text="Save Drawing", command=self.save_drawing)
        self.save_button.pack(side=tk.BOTTOM,)

    def save_drawing(self):
        try:
            # Get the content of the canvas and convert it to an image
            x = self.window.winfo_rootx() + self.canvas.winfo_x()
            y = self.window.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()

            drawing_image = ImageGrab.grab(bbox=(x, y, x1, y1))

            # Save the image
            drawing_image.save("drawing_output.png")
            print("Drawing saved as drawing_output.png")
        except Exception as e:
            print("Error in save_drawing:", str(e))

    def create_paint_interface(self):
        self.paint_interface = cv2.rectangle(self.paint_interface, (40, 41), (140, 105), (0, 0, 0), 2)
        for i, color in enumerate(self.colors):
            start_x, end_x = 160 + i * 115, 255 + i * 115
            self.paint_interface = cv2.rectangle(self.paint_interface, (start_x, 41), (end_x, 105), color, -1)
            cv2.putText(self.paint_interface, self.color_name(i), (start_x + 10, 73), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(self.paint_interface, "CLEAR ALL", (49, 73), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
        self.update_tkinter_image()

    def color_name(self, index):
        color_names = ["BLUE", "GREEN", "RED", "YELLOW"]
        return color_names[index]

    def update_tkinter_image(self):
        img = np.uint8(self.paint_interface)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.photo = ImageTk.PhotoImage(image=img)
        if hasattr(self, 'canvas'):
            self.canvas.config(width=self.photo.width(), height=self.photo.height())
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.canvas.image = self.photo

        #print("Tkinter image updated successfully")

    def update_video_feed(self):
        _, frame = self.camera.read()
        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame = cv2.rectangle(frame, (40, 41), (140, 105), (122, 122, 122), -1)
        for i, color in enumerate(self.colors):
            start_x, end_x = 160 + i * 115, 255 + i * 115
            frame = cv2.rectangle(frame, (start_x, 41), (end_x, 105), color, -1)
            cv2.putText(frame, self.color_name(i), (start_x + 10, 73), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255),
                        2, cv2.LINE_AA)
        cv2.putText(frame, "CLEAR ALL", (49, 73), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        blue_mask = self.color_mask(hsv, lower=(105, 50, 50), upper=(125, 255, 255))
        blue_mask = cv2.erode(blue_mask, self.kernel, iterations=2)
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, self.kernel)
        blue_mask = cv2.dilate(blue_mask, self.kernel, iterations=1)

        cnts, _ = cv2.findContours(blue_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None

        if cnts:
            cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            if center[1] <= 105:
                if 40 <= center[0] <= 140:  # Clear All
                    self.clear_all()
                elif 160 <= center[0] <= 255:
                    self.color_index = 0  # Blue
                elif 275 <= center[0] <= 370:
                    self.color_index = 1  # Green
                elif 390 <= center[0] <= 485:
                    self.color_index = 2  # Red
                elif 505 <= center[0] <= 600:
                    self.color_index = 3  # Yellow
            else:
                self.draw_points(center)

        self.update_tkinter_image()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.stop()
        self.window.update()

        #if self.processing:
        self.window.after(10, self.update)

        points = [self.bpoints, self.gpoints, self.rpoints, self.ypoints]
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], self.colors[i], 2)
                    cv2.line(self.paint_interface, points[i][j][k - 1], points[i][j][k], self.colors[i], 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        self.video_photo = ImageTk.PhotoImage(image=img)

        if hasattr(self, 'video_canvas'):
            self.video_canvas.config(width=self.video_photo.width(), height=self.video_photo.height())
            self.video_canvas.create_image(0, 0, image=self.video_photo, anchor=tk.NW)
            self.video_canvas.image = self.video_photo

        self.update_tkinter_image()

    def update(self):
        self.update_video_feed()
        self.update_tkinter_image()

        self.window.after(10, self.update)

    def color_mask(self, hsv, lower, upper):
        return cv2.inRange(hsv, np.array(lower), np.array(upper))

    def draw_points(self, center):
        points = [self.bpoints, self.gpoints, self.rpoints, self.ypoints]
        selected_points = points[self.color_index]
        selected_index = [self.bindex, self.gindex, self.rindex, self.yindex][self.color_index]

        if self.color_index == 3:
            selected_points[selected_index].appendleft(center)
        else:
            selected_points[selected_index].appendleft(center)
    def clear_all(self):
        self.bpoints = [deque(maxlen=512)]
        self.gpoints = [deque(maxlen=512)]
        self.rpoints = [deque(maxlen=512)]
        self.ypoints = [deque(maxlen=512)]

        self.bindex = 0
        self.gindex = 0
        self.rindex = 0
        self.yindex = 0

        self.paint_interface[107:, :, :] = 255
        self.update_tkinter_image()

    def start(self):
        #self.processing = True
        #self.camera = cv2.VideoCapture(0)
        #self.kernel = np.ones((5, 5), np.uint8)
        self.update()

    def stop(self):
        if self.camera is None:
            #self.processing = False
            self.camera.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveDraw(root, "Paint App")
    app.start()
    root.mainloop()
