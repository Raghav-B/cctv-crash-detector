import keras
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color
import tensorflow as tf

import cv2
import numpy as np
import glob
import time
from collections import deque
from object_tracker import object_tracker

class detection_model:
    def __init__(self, model_path, src_video=0, frame_skip=0):
        keras.backend.tensorflow_backend.set_session(self.get_session())
        self.ot = object_tracker()
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        
        self.model = models.load_model(model_path, backbone_name='resnet50')
        self.label_names = {0: "vehicle"}
        
        self.video = cv2.VideoCapture(src_video)
        self.frame_width = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.frame_skip = frame_skip
        self.total_framerate = 0
        self.total_frames = 0

        self.is_init_frame = True
        self.prev_frame_objects = []
        self.cur_frame_objects = []

    def get_session(self):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.Session(config=config)
    
    def get_frame(self):
        start_time = time.time()

        for i in range(0, self.frame_skip):
            ret, frame = self.video.read()
        ret, frame = self.video.read()
        if (ret == False):
            return ret, None, -1, False 

        # Making input image square by padding it
        rows = frame.shape[0]
        cols = frame.shape[1]
        if rows < cols:
            padding = int((cols - rows) / 2)
            frame = cv2.copyMakeBorder(frame, padding, padding, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
        elif rows > cols:
            padding = int((rows - cols) / 2)
            frame = cv2.copyMakeBorder(frame, 0, 0, padding, padding, cv2.BORDER_CONSTANT, (0, 0, 0))
        
        # Making copy of raw frame for drawing detections and other info
        draw_frame = frame.copy()

        frame = preprocess_image(frame)
        frame, scale = resize_image(frame, min_side=600)
        boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(frame, axis=0))
        boxes /= scale

        # Filter detections and prepare for object tracking
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            if score < 0.95:
                break

            midpoint_x = int((box[2] + box[0]) / 2)
            midpoint_y = int((box[3] + box[1]) / 2)

            if (self.is_init_frame == True):
                self.prev_frame_objects.append([(midpoint_x, midpoint_y), self.ot.get_init_index(), 0, deque(), -1, 0])
            else:
                self.cur_frame_objects.append([(midpoint_x, midpoint_y), 0, 0, deque(), -1, 0])

        # Running object tracking algorithm to track detections across frames
        if (self.is_init_frame == False):
            if (len(self.prev_frame_objects) != 0):
                self.cur_frame_objects = self.ot.sort_cur_objects(self.prev_frame_objects, self.cur_frame_objects)

        frame_time = time.time() - start_time
        #print("Framerate: " + str(int(1/frame_time)))
        self.total_framerate += (1/frame_time)
        self.total_frames += 1

        is_crash_detected = False
        for point in self.cur_frame_objects:
            # Only drawing index for object that has been detected for 3 frames
            if (point[2] >= 5):            
                # Finding vector of car and converting to unit vector
                vector = [point[3][-1][0] - point[3][0][0], point[3][-1][1] - point[3][0][1]] # [x, y]
                end_point = (2 * vector[0] + point[3][-1][0], 2 * vector[1] + point[3][-1][1]) # (x, y)
                vector_mag = (vector[0]**2 + vector[1]**2)**(1/2)
                delta = abs(vector_mag - point[5])

                has_object_crashed = False
                if (delta >= 11) and point[5] != 0.0:
                    is_crash_detected = True
                    has_object_crashed = True
                
                cv2.circle(draw_frame, point[0], 5, (0, 255, 255), 2)
                if (has_object_crashed == True):
                    cv2.circle(draw_frame, point[0], 40, (0, 0, 255), 4)

                # Drawing vector of each object
                cv2.line(draw_frame, point[3][-1], end_point, (255, 255, 0), 2)

        if (is_crash_detected == True):
            cv2.putText(draw_frame, f"CRASH DETECTED", (10, 30), self.font, 1, (0, 0, 255), 2, cv2.LINE_AA)
            #cv2.imshow("Crash", draw_frame)

        if (self.is_init_frame == False):
            self.prev_frame_objects = self.cur_frame_objects.copy()
            self.cur_frame_objects = []
        
        self.is_init_frame = False
        return ret, draw_frame, frame_time, is_crash_detected
        
    def __del__(self):
        self.video.release()