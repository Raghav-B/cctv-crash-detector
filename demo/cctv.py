import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from detection_model import detection_model
import datetime

class cctv:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.dm = detection_model("../keras-retinanet/inference_graphs/resnet50_600p_51+/resnet50_csv_36.h5", \
            src_video = "../videos/crash_all.mp4")

        self.imageFrame = tk.Frame(self.window, width=600, height=600)
        self.imageFrame.grid(row=0, column=0, padx=5, pady=5)

        self.crash_images = ttk.Treeview(self.window, height=29)#, column=("#0"))#, height=600) #width=600)
        self.crash_images.heading("#0", text="Detected Crashes")
        self.crash_images.grid(row=0, column=600, padx=5, pady=5)
        self.vsb = ttk.Scrollbar(self.window, orient="vertical", command=self.crash_images.yview)
        self.vsb.place(x=812, y=8, height=605)
        self.crash_images.configure(yscrollcommand=self.vsb.set)
        self.crash_images.bind("<Double-1>", self.open_crash_image)
        self.crash_dupl_checklist = set()

        #Capture video frames
        self.lmain = tk.Label(self.imageFrame)
        self.lmain.grid(row=0, column=0)

        self.update()
        self.window.mainloop()

    def update(self):
        ret, cv_image, frame_time, is_crash_detected = self.dm.get_frame()

        if (ret == True):
            frame = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGBA)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(image=frame)
            self.lmain.imgtk = frame
            self.lmain.configure(image=frame)

            if (is_crash_detected == True):
                current_time = datetime.datetime.now()
                crash_name = current_time.strftime("%d-%m-%y_%H-%M-%S")# + str(current_time.microsecond)
                if not (crash_name in self.crash_dupl_checklist):
                    self.crash_dupl_checklist.add(crash_name)
                    self.crash_images.insert("", 0, text=crash_name)
                cv2.imwrite("crashes/" + crash_name + ".jpg", cv_image)

        self.lmain.after(1, self.update)
    
    def open_crash_image(self, event):
        query_image = self.crash_images.selection()[0]
        open_image = cv2.imread("crashes/" + self.crash_images.item(query_image, "text") + \
            ".jpg")
        cv2.imshow("Detected Crash", open_image)


cctv(tk.Tk(), "CCTV")