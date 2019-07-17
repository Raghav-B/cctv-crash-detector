import keras
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

import cv2
import numpy as np

import matplotlib.pyplot as plt
import os
import glob
import time

import tensorflow as tf

from sort_midpoints import object_sorter

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)
keras.backend.tensorflow_backend.set_session(get_session())

model_path = os.path.join('inference_graphs', 'resnet101_csv_24.h5') # huh lucky number
model = models.load_model(model_path, backbone_name='resnet101')

labels_to_names = {0: "vehicle"}

cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detection", 1280, 1280)

ot = object_sorter()

while(True):
    video = cv2.VideoCapture("../videos/singapore_traffic.mp4")
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_skip_amt = 3 # This makes inferencing appear realtime

    cur_frame = 0
    #fourcc = cv2.VideoWriter_fourcc(*"XVID")
    #output_video = cv2.VideoWriter("../videos/output.avi", fourcc, 30.0, (720, 720))
    
    is_init_frame = True
    prev_frame_objects = []
    cur_frame_objects = []

    while(True):
        start_time = time.time()
        # Performing frame-skip for increased performance
        for i in range(0, frame_skip_amt):
            ret, frame = video.read()
        ret, frame = video.read()
        if ret == False:
            break
        
        rows = frame.shape[0]
        cols = frame.shape[1]

        if rows < cols:
            padding = int((cols - rows) / 2)
            frame = cv2.copyMakeBorder(frame, padding, padding, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
        elif rows > cols:
            padding = int((rows - cols) / 2)
            frame = cv2.copyMakeBorder(frame, 0, 0, padding, padding, cv2.BORDER_CONSTANT, (0, 0, 0))
        
        draw = frame.copy()

        # preprocess image for network
        image = preprocess_image(frame)
        image, scale = resize_image(image)#, min_side = 500)

        # process image
        boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))

        # correct for image scale
        boxes /= scale

        # visualize detections
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            if score < 0.95:
                break

            midpoint_x = int((box[2] + box[0]) / 2)
            midpoint_y = int((box[3] + box[1]) / 2)

            x1 = box[0]
            y1 = box[1]
            x2 = box[2]
            y2 = box[3]

            if (is_init_frame == True):
                prev_frame_objects.append([(midpoint_x, midpoint_y), (x2, y2), ot.get_init_index(), 0])
            else:
                cur_frame_objects.append([(midpoint_x, midpoint_y), (x2, y2), -1, 0])

            color = label_color(label)
            b = box.astype(int)
            draw_box(draw, b, color=color)
            caption = "{} {:.2f}".format(labels_to_names[label], score)
            draw_caption(draw, b, caption)
        
        # Sorting cur_frame midpoints
        if (is_init_frame == False):
            cur_frame_objects = ot.sort_cur_objects(prev_frame_objects, cur_frame_objects)
        
        #print(cur_frame_objects)
        end_time = time.time() - start_time
        print("Framerate: " + str(end_time))

        font = cv2.FONT_HERSHEY_SIMPLEX
        for point in cur_frame_objects:
            cv2.putText(draw, f"{int(point[3] / end_time)}", point[0], font, 0.5, (255, 255, 0), 2, cv2.LINE_AA)
        if (is_init_frame == False):
            prev_frame_objects = cur_frame_objects
            cur_frame_objects = []

        #output_img = cv2.cvtColor(draw, cv2.COLOR_RGB2BGR)
        cv2.imshow("Detection", draw)
        #framerate = (1 / (time.time() - start_time)) * (frame_skip_amt + 1)

        #output_video.write(output_img)
        cur_frame += 1
        #print("Finished " + str(cur_frame) + " out of " + str(total_frames) + " total frames...")
        #print(framerate)

        is_init_frame = False

        if cv2.waitKey(1) == ord('q'):
            break

#output_video.release()
video.release()
cv2.destroyAllWindows()