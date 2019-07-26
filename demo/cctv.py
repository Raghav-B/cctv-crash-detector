import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from detection_model import detection_model
import datetime
import glob

class cctv:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.dm = detection_model("../keras-retinanet/inference_graphs/resnet50_600p_51+/resnet50_csv_36.h5", \
            src_video = "../videos/crash_all.mp4")

        self.imageFrame = tk.Frame(self.window, width=600, height=600)
        self.imageFrame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.crash_images = ttk.Treeview(self.window, height=29)
        self.crash_images.heading("#0", text="Detected Crashes")
        self.crash_images.grid(row=0, column=2, padx=5, pady=5)
        self.vsb = ttk.Scrollbar(self.window, orient="vertical", command=self.crash_images.yview)
        self.vsb.place(x=812, y=8, height=605)
        self.crash_images.configure(yscrollcommand=self.vsb.set)
        self.crash_images.bind("<Double-1>", self.open_crash_image)
        self.crash_dupl_checklist = set()

        self.cctv_list = glob.glob("../videos/*.mp4") # 10 different videos
        self.cur_cctv_index = 0

        self.cctv_label_text = tk.StringVar()
        self.cctv_label_text.set(f"CCTV ID: {self.cur_cctv_index} / {len(self.cctv_list) - 1}")
        self.cctv_label = tk.Label(self.window, textvariable=self.cctv_label_text, \
            font=("Helvetica", 15))
        self.cctv_label.grid(row=1, column=0, columnspan=2, pady=5)

        self.prev_cctv = tk.Button(self.window, text="Prev CCTV", command=self.load_prev_cctv, \
            height=1, width=26, font=("Helvetica", 15))
        self.prev_cctv.grid(row=2, column=0, pady=5, padx=5)
        self.next_cctv = tk.Button(self.window, text="Next CCTV", command=self.load_next_cctv, \
            height=1, width=26, font=("Helvetica", 15))
        self.next_cctv.grid(row=2, column=1, pady=5, padx=5)

        self.developer = tk.Label(self.window, text="Developed by Rcube", width=22, height=4, \
            font=("Helvetica", 12), borderwidth=2, relief="groove")
        self.developer.grid(row=1, column=2, rowspan=2, pady=5, padx=5)

        #Capture video frames
        self.lmain = tk.Label(self.imageFrame)
        self.lmain.grid(row=0, column=0)

        self.update()
        self.window.mainloop()

    def update(self):
        ret, cv_image, frame_time, is_crash_detected = self.dm.get_frame()

        #if (ret == True):
        frame = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGBA)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(image=frame)
        self.lmain.imgtk = frame
        self.lmain.configure(image=frame)

        if (is_crash_detected == True):
            current_time = datetime.datetime.now()
            crash_name = current_time.strftime("CCTV_" + str(self.cur_cctv_index) + "_%d-%m-%y_%H-%M-%S")
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

    def load_prev_cctv(self):
        self.cur_cctv_index -= 1
        if (self.cur_cctv_index < 0):
            self.cur_cctv_index = len(self.cctv_list) - 1
        self.dm.src_video = self.cctv_list[self.cur_cctv_index]
        self.dm.video = cv2.VideoCapture(self.dm.src_video)
        self.cctv_label_text.set(f"CCTV ID: {self.cur_cctv_index} / {len(self.cctv_list) - 1}")
    
    def load_next_cctv(self):
        self.cur_cctv_index += 1
        if (self.cur_cctv_index >= len(self.cctv_list)):
            self.cur_cctv_index = 0
        self.dm.src_video = self.cctv_list[self.cur_cctv_index]
        self.dm.video = cv2.VideoCapture(self.dm.src_video)
        self.cctv_label_text.set(f"CCTV ID: {self.cur_cctv_index} / {len(self.cctv_list) - 1}")

cctv(tk.Tk(), "CCTV Crash Detector")