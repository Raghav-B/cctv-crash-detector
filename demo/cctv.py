import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from detection_model import detection_model
import datetime
import glob
import os
import threading

import requests
import base64

class cctv:
    # Setting up window elements
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.URL = "http://34.66.101.75:5002/add_face"

        # Getting list of .mp4 files (CCTV footage)
        self.cctv_list = glob.glob("../videos/final/*.mp4")
        self.cur_cctv_index = 0

        # Setting up our model for detection
        self.dm = detection_model("../keras-retinanet/inference_graphs/crash_detection_model.h5", \
        #self.dm = detection_model("../keras-retinanet/inference_graphs/vehicle_tracking_model.h5", \
            src_video = self.cctv_list[self.cur_cctv_index])

        # Frame to show our frame outputs from the detection model
        self.imageFrame = tk.Frame(self.window, width=600, height=600)
        self.imageFrame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Listbox that will contain all the information on detected crashes
        self.crash_images = ttk.Treeview(self.window, height=29)
        self.crash_images.heading("#0", text="Detected Crashes")
        self.crash_images.grid(row=0, column=2, padx=5, pady=5)
        self.vsb = ttk.Scrollbar(self.window, orient="vertical", command=self.crash_images.yview)
        self.vsb.place(x=812, y=8, height=605)
        self.crash_images.configure(yscrollcommand=self.vsb.set)
        self.crash_images.bind("<Double-1>", self.open_crash_image)
        self.crash_dupl_checklist = set()

        # Label that shows current CCTV (.mp4) being viewed
        self.cctv_label_text = tk.StringVar()
        self.cctv_label_text.set(f"CCTV ID: {self.cur_cctv_index + 1} / {len(self.cctv_list)} - {os.path.basename(self.cctv_list[self.cur_cctv_index])[:-4]}")
        self.cctv_label = tk.Label(self.window, textvariable=self.cctv_label_text, \
            font=("Helvetica", 15))
        self.cctv_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Buttons to switch back and forth between different CCTVs
        self.prev_cctv = tk.Button(self.window, text="Prev CCTV", command=self.load_prev_cctv, \
            height=1, width=26, font=("Helvetica", 15))
        self.prev_cctv.grid(row=2, column=0, pady=5, padx=5)
        self.next_cctv = tk.Button(self.window, text="Next CCTV", command=self.load_next_cctv, \
            height=1, width=26, font=("Helvetica", 15))
        self.next_cctv.grid(row=2, column=1, pady=5, padx=5)

        # Reset history of suspected crash detections and delete saved crash images
        self.reset_history()
        self.reset = tk.Button(self.window, text="Reset History", font=("Helvetica", 11), \
            command=self.reset_history, width=21, height=4)
        self.reset.grid(row=1, column=2, rowspan=2)

        # Required to show frame output from detection model
        self.lmain = tk.Label(self.imageFrame)
        self.lmain.grid(row=0, column=0)

        # Callback function to get new frames from detection model
        self.update()
        self.window.mainloop()

    # Callback function that gets a frame from the detection model. Based on whether a crash has been 
    # detected, it also saves the image of the crash and updates the crash listbox.
    def update(self):
        ret, cv_image, frame_time, is_crash_detected = self.dm.get_frame()

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
            
            # Post online
            post_thread = threading.Thread(target=self.poster, args=(cv_image, self.cur_cctv_index,))
            post_thread.start()
            #self.poster(cv_image, self.cur_cctv_index)
            
            cv2.imwrite("crashes/" + crash_name + ".jpg", cv_image)

        self.lmain.after(1, self.update)
    
    # Double-click any of the items in the listbox to view the image of the crash
    def open_crash_image(self, event):
        query_image = self.crash_images.selection()[0]
        print(self.crash_images.index(query_image))
        open_image = cv2.imread("crashes/" + self.crash_images.item(query_image, "text") + \
            ".jpg")
        cv2.imshow("Detected Crash", open_image)

    # Loads previous CCTV, emulates circular array
    def load_prev_cctv(self):
        self.cur_cctv_index -= 1
        if (self.cur_cctv_index < 0):
            self.cur_cctv_index = len(self.cctv_list) - 1
        self.dm.src_video = self.cctv_list[self.cur_cctv_index]
        self.dm.video = cv2.VideoCapture(self.dm.src_video)
        self.cctv_label_text.set(f"CCTV ID: {self.cur_cctv_index + 1} / {len(self.cctv_list)} - {os.path.basename(self.cctv_list[self.cur_cctv_index])[:-4]}")
    
    # Loads next CCTV, emulates circular array
    def load_next_cctv(self):
        self.cur_cctv_index += 1
        if (self.cur_cctv_index >= len(self.cctv_list)):
            self.cur_cctv_index = 0
        self.dm.src_video = self.cctv_list[self.cur_cctv_index]
        self.dm.video = cv2.VideoCapture(self.dm.src_video)
        self.dm.total_frames = 0
        self.dm.crash_frames = 0
        self.cctv_label_text.set(f"CCTV ID: {self.cur_cctv_index + 1} / {len(self.cctv_list)} - {os.path.basename(self.cctv_list[self.cur_cctv_index])[:-4]}")

    # Deletes all saved crash images and empties crash listbox
    def reset_history(self):
        files_to_delete = glob.glob("crashes/*")
        for i in files_to_delete:
            os.remove(i)
        self.crash_dupl_checklist = set()
        for row in self.crash_images.get_children():
            self.crash_images.delete(row)

    def poster(self, frame, cctv_id):
        ret, buffer = cv2.imencode(".jpg", frame)
        jpg_as_text = base64.b64encode(buffer)
        response = requests.post(self.URL, data={"num":cctv_id + 1, "img":jpg_as_text})
        #print(response.content)

# Start the UI
if __name__ == "__main__":
    cctv(tk.Tk(), "CCTV Crash Detector")