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
from sort_midpoints import object_sorter

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)
keras.backend.tensorflow_backend.set_session(get_session())

model_path = "../keras-retinanet/inference_graphs/resnet101_csv_24.h5"
model = models.load_model(model_path, backbone_name='resnet101')

labels_to_names = {0: "vehicle"}

cv2.namedWindow("Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Detection", 800, 800)

ot = object_sorter()

video = cv2.VideoCapture("../videos/real_traffic1.mp4")
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
frame_skip_amt = 2 # This makes inferencing appear realtime

is_init_frame = True
font = cv2.FONT_HERSHEY_SIMPLEX
prev_frame_objects = []
cur_frame_objects = []

while True:
    start_time = time.time()
    # Performing frame-skip for increased performance
    for i in range(0, frame_skip_amt):
        ret, frame = video.read()
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
    image, scale = resize_image(image)

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

        #x1 = box[0]
        #y1 = box[1]
        #x2 = box[2]
        #y2 = box[3]

        if (is_init_frame == True):
            prev_frame_objects.append([(midpoint_x, midpoint_y), ot.get_init_index(), 0, deque()])
        else:
            # All objects detected in current frame are initialised with index -1, after running through
            # the object sorter, objects are assigned appropriate indexes.
            cur_frame_objects.append([(midpoint_x, midpoint_y), -1, 0, deque()])

        b = box.astype(int)
        draw_box(draw, b, color=(0, 255, 255))
        #caption = "{} {:.2f}".format(labels_to_names[label], score)
        #draw_caption(draw, b, caption)
    
    # Sorting cur_frame midpoints
    if (is_init_frame == False):
        cur_frame_objects = ot.sort_cur_objects(prev_frame_objects, cur_frame_objects)
    
    end_time = time.time() - start_time
    print("Frame time: " + str(end_time))

    for point in cur_frame_objects:
        # Only drawing index for object that has been detected for 3 frames
        if (point[2] >= 3):
            cv2.putText(draw, f"{int(point[1])}", point[0], font, 2, (0, 255, 255), 5, cv2.LINE_AA)
            vector = (point[3][-1][0] - point[3][0][0], point[3][-1][1] - point[3][0][1]) # (x, y)
            end_point = (5 * vector[0] + point[3][0][0], 5 * vector[1] + point[3][0][1]) # (x, y)
            #cv2.line(draw, point[3][0], point[3][-1], (255, 255, 0), 10)
            cv2.line(draw, point[3][0], end_point, (255, 255, 0), 10)
    
    if (is_init_frame == False):
        prev_frame_objects = cur_frame_objects.copy()
        cur_frame_objects = []

    cv2.imshow("Detection", draw)

    is_init_frame = False
    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()