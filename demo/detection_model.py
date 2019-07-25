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
    def __init__(self):
        pass

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)
keras.backend.tensorflow_backend.set_session(get_session())

model_path = "../keras-retinanet/inference_graphs/resnet50_600p_51+/resnet50_csv_36.h5"
model = models.load_model(model_path, backbone_name='resnet50')

labels_to_names = {0: "vehicle"}

ot = object_tracker()

video = cv2.VideoCapture("../videos/crash_all.mp4")
# Every 2 frames, I want to skip a frame.
frame_skip_amt = 0 # This makes inferencing appear realtime
frame_skip_start = 0

is_init_frame = True
font = cv2.FONT_HERSHEY_SIMPLEX
prev_frame_objects = []
cur_frame_objects = []

total_framerate = 0
total_frames = 0

while True:
    start_time = time.time()
    # Performing frame-skip for increased performance
    #if (frame_skip_start < 2):
    #    frame_skip_start += 1
    #else:
    #    ret, frame = video.read()
    #    frame_skip_start = 0

    ret, frame = video.read()
    if ret == False:
        break
    
    # Making input image square by padding it
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
    image, scale = resize_image(image, min_side=600)
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

        if (is_init_frame == True):
            prev_frame_objects.append([(midpoint_x, midpoint_y), ot.get_init_index(), 0, deque(), -1, 0])
        else:
            # All objects detected in current frame are initialised with index -1, after running through
            # the object sorter, objects are assigned appropriate indexes.
            cur_frame_objects.append([(midpoint_x, midpoint_y), 0, 0, deque(), -1, 0])

        #b = box.astype(int)
        #draw_box(draw, b, color=(0, 255, 255))
        #caption = "{} {:.2f}".format(labels_to_names[label], score)
        #draw_caption(draw, b, caption)
    
    # Sorting cur_frame midpoints
    if (is_init_frame == False):
        if (len(prev_frame_objects) != 0):
            cur_frame_objects = ot.sort_cur_objects(prev_frame_objects, cur_frame_objects)
    
    end_time = time.time() - start_time
    #print("Framerate: " + str(int(1/end_time)))
    total_framerate += (1/end_time)
    total_frames += 1

    is_crash_detected = False
    for point in cur_frame_objects:
        # Only drawing index for object that has been detected for 3 frames
        if (point[2] >= 5):            
            # Finding vector of car and converting to unit vector
            vector = [point[3][-1][0] - point[3][0][0], point[3][-1][1] - point[3][0][1]] # [x, y]
            vector_mag = (vector[0]**2 + vector[1]**2)**(1/2)
            
            dist = abs(vector_mag - point[5])

            has_object_crashed = False
            colour = (0, 255, 255)
            if (dist >= 11) and point[5] != 0.0:
                colour = (0, 0, 255)
                is_crash_detected = True
                has_object_crashed = True
            
            # Showing both magnitude and direction of vector
            end_point = (2 * vector[0] + point[3][-1][0], 2 * vector[1] + point[3][-1][1]) # (x, y)
            # Showing index of object on object
            #cv2.putText(draw, f"{int(point[1])}", point[0], font, 1, (0, 255, 255), 2, cv2.LINE_AA)
            #cv2.putText(draw, f"{dist:.1f},{vector_mag:.1f},{point[5]:.1f}", point[0], font, 0.5, colour, 2, cv2.LINE_AA)
            cv2.circle(draw, point[0], 5, (0, 255, 255), 2)
            if (has_object_crashed == True):
                cv2.circle(draw, point[0], 40, (0, 0, 255), 4)

            cv2.line(draw, point[3][-1], end_point, (255, 255, 0), 2)
    
    if (is_crash_detected == True):
        cv2.putText(draw, f"CRASH DETECTED", (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Crash", draw)

    if (is_init_frame == False):
        prev_frame_objects = cur_frame_objects.copy()
        cur_frame_objects = []

    cv2.imshow("CCTV", draw)

    is_init_frame = False
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('p'):
        cv2.waitKey()

print(f"Average FPS: {(total_framerate / total_frames):.2f}")
video.release()
cv2.destroyAllWindows()