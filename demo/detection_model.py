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

# This class is the main backend of the crash detector. It initially detects all objects (vehicles) in an
# input frame, and then based on the initial and subsequent vectors for every object, determines whether
# or not a crash has occured.
class detection_model:
   
    # model_path: Path to the pretrained model to be used
    # src_video: Source video to be ran. Default is local device's primary camera.
    # frame_skip: Used to emulate realtime performance if single-frame inference is too slow.
    #             Default is 0 since the provided pretrained model gives an FPS of about 26.
    def __init__(self, model_path, src_video=0, frame_skip=0):
        keras.backend.tensorflow_backend.set_session(self.get_session()) # Initialising keras
        self.ot = object_tracker() # This class handles tracking objects across subsequent frames
        self.font = cv2.FONT_HERSHEY_SIMPLEX # OpenCV font for drawing text on frame

        # Loading pretrained model with resnet50 backbone
        self.model = models.load_model(model_path, backbone_name='resnet50')
        # Unused in our case, but is basically the class our model was trained to detect
        self.label_names = {0: "bike", 1: "non-bike"}
        
        # Initialising input video source
        self.src_video = src_video
        self.video = cv2.VideoCapture(self.src_video)
        self.frame_skip = frame_skip
        # Used for average framerate calculation
        self.total_framerate = 0
        self.total_frames = 0

        # The following is used for object tracking across frames.
        self.is_init_frame = True # Flag is necessary to setup object tracking properly
        self.prev_frame_objects = []
        self.cur_frame_objects = []


    # Sets up Tensorflow/Keras backend 
    def get_session(self):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.Session(config=config)
    

    # Gets a new frame from the video source and runs inference on it
    # Return values:
    # ret: Flag for whether there are any available frames to read in the video source
    # draw_frame: Frame post-inferencing with detections and other information drawn on
    # frame_time: Time taken for inferencing of frame
    # is_crash_detected: Flag for whether frame contains a suspected crash 
    total_frames = 0
    crash_frames = 0
    def get_frame(self):
        # Used for framerate calculation
        start_time = time.time()

        # Frameskipping
        for i in range(0, self.frame_skip):
            ret, frame = self.video.read()
        # Frame to be inferenced on is read here
        ret, frame = self.video.read()
        if (ret == False):
            self.video = cv2.VideoCapture(self.src_video)
            ret, frame = self.video.read()
            print("end\n\n\n\n\n\n\n\n\n")

        # Making input image square by padding it. This is because our model was trained on square
        # images. Changing the aspect ratio of input images would greatly reduce accuracy.
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

        # Preprocessing frame before inferencing
        frame = preprocess_image(frame)
        frame, scale = resize_image(frame, min_side=600)
        # Running actual inference on input frame
        boxes, scores, labels = self.model.predict_on_batch(np.expand_dims(frame, axis=0))
        boxes /= scale # Adjusting scale of bounding boxes since our frame is resized to 600p

        # Filtering detections and preparing for object tracking
        for box, score, label in zip(boxes[0], scores[0], labels[0]):
            # We break if the score of any of our detections is below 0.95. This is because
            # all detections are sorted in descending order in terms of their scores.
            if score < 0.95:
                break

            # Getting midpoint of detected bounding box
            midpoint_x = int((box[2] + box[0]) / 2)
            midpoint_y = int((box[3] + box[1]) / 2)

            # Object tracking stuff, see object_tracker.py for more information
            if (self.is_init_frame == True):
                self.prev_frame_objects.append([(midpoint_x, midpoint_y), self.ot.get_init_index(), 0, deque(), -1, 0])
            else:
                self.cur_frame_objects.append([(midpoint_x, midpoint_y), 0, 0, deque(), -1, 0])

        # Running object tracking algorithm to track detections across frames
        if (self.is_init_frame == False):
            # We only run when we have had at least 1 object detected in the previous (initial) frame
            if (len(self.prev_frame_objects) != 0):
                self.cur_frame_objects = self.ot.sort_cur_objects(self.prev_frame_objects, self.cur_frame_objects)

        # Framerate calculation
        frame_time = time.time() - start_time
        #print("Framerate: " + str(int(1/frame_time)))
        self.total_framerate += (1/frame_time)
        self.total_frames += 1

        #cv2.imwrite(str(self.total_frames) + ".png", draw_frame)

        is_crash_detected = False # Has a crash been detected anywhere in our current frame?
        for point in self.cur_frame_objects: # Iterating through all our objects in the current frame.
            # Only objects that have been present for 5 consecutive frames are considered. This is done to
            # filter out any inaccurate momentary detections.
            if (point[2] >= 5):            
                # Finding vector of object across 5 frames
                vector = [point[3][-1][0] - point[3][0][0], point[3][-1][1] - point[3][0][1]]
                # Getting a simple estimate coordinate of where we expect our object to end up
                # with its current vector. This is used to draw the predicted vector for each object.
                end_point = (2 * vector[0] + point[3][-1][0], 2 * vector[1] + point[3][-1][1])
                
                # Getting magnitude of vector for crash detection. We could use the direction in this detection
                # as well, but we achieved much better results when just using the magnitude.
                vector_mag = (vector[0]**2 + vector[1]**2)**(1/2)
                # Change in magnitude (essentially the object's acceleration/deceleration)
                delta = abs(vector_mag - point[5])

                # Flag for current object being a crash or not.
                has_object_crashed = False
                if (delta >= 11) and point[5] != 0.0: # Criteria for crash.
                    is_crash_detected = True
                    has_object_crashed = True
                
                # Drawing circle to label detected objects
                cv2.circle(draw_frame, point[0], 5, (0, 255, 255), 2)
                if (has_object_crashed == True):
                    # Red circle is drawn around an object that has been suspected of crashing
                    cv2.circle(draw_frame, point[0], 40, (0, 0, 255), 4)

                # Drawing predicted future vector of each object. (Blue line)
                cv2.line(draw_frame, point[3][-1], end_point, (255, 255, 0), 2)

        #cv2.imwrite(str(self.total_frames) + "_detect.png", draw_frame)
        # If crash has occured in current frame, add text that notifies that a crash has occurred.
        if (is_crash_detected == True):
            cv2.putText(draw_frame, f"CRASH DETECTED", (10, 30), self.font, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # More object tracking stuff, please see object_tracker.py
        if (self.is_init_frame == False):
            self.prev_frame_objects = self.cur_frame_objects.copy()
            self.cur_frame_objects = []
        self.is_init_frame = False

        self.total_frames += 1
        if is_crash_detected:
            self.crash_frames += 1
        print((self.crash_frames / self.total_frames) * 100)
        return ret, draw_frame, frame_time, is_crash_detected
        
    # Cleaning up
    def __del__(self):
        self.video.release()