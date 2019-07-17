import numpy as np
import cv2
import glob
import os
import random

vid_col = glob.glob("videos/*.mp4")

print(vid_col)

frame_index = 0
for x in vid_col:
    print(x)
    
    input_vid = cv2.VideoCapture(x)
    ret, frame = input_vid.read()
    while (ret):
        #frames_to_skip = random.randint(50, 250)
        frames_to_skip = random.randint(250, 1000)
        ret = None

        for i in range(0, frames_to_skip):
            ret, frame = input_vid.read()
            if (ret == False):
                break
        ret, frame = input_vid.read()
        if (ret == False):
            break

        output_path = "validation_extracted_frames/" + str(frame_index) + ".jpg"
        frame_index += 1

        cv2.imwrite(output_path, frame)

    input_vid.release()