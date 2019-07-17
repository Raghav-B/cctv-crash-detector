import cv2
import numpy as np
import glob
import os
import pandas as pd

import keras
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

import tensorflow as tf

#csv_file = pd.read_csv("../annotations/validation_no_p.csv", names = ["path", "x1", "y1", "x2", "y2", "label"])
#image_paths = csv_file["path"]
#image_list = set()

#for i in image_paths:
#    image_list.add(i)

def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)
keras.backend.tensorflow_backend.set_session(get_session())

# Can change this to change the model used for inferencing
model_path = "inference_graphs/resnet50_coco_best_v2.1.0.h5"
model = models.load_model(model_path, backbone_name='resnet50')

# Strings associated with each label index
#labels_to_names = {0: "car", 1: "motorcycle", 2: "bus", 3: "truck"}
labels_to_names = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

# Get paths of all input images
input_images = glob.glob("test_inputs/*.jpg")
input_images_png = glob.glob("test_inputs/*.png")
input_images.extend(input_images_png)

input_images_len = len(input_images)
cur_image = 0

# Iterate through all input images
for i in input_images:
    just_image_name = os.path.split(i)
    image = cv2.imread(i)

    
    rows = image.shape[0]
    cols = image.shape[1]

    if rows < cols:
        padding = int((cols - rows) / 2)
        image = cv2.copyMakeBorder(image, padding, padding, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
    elif rows > cols:
        padding = int((rows - cols) / 2)
        image = cv2.copyMakeBorder(image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, (0, 0, 0))
    

    draw = image.copy()

    # Preprocessing, before inputting into the model
    image = preprocess_image(image)
    image, scale = resize_image(image)
    print(image.shape)

    # Running the inferencing
    boxes, scores, labels = model.predict_on_batch(np.expand_dims(image, axis=0))
    # Correcting the box scale
    boxes /= scale

    # Visualizing detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        if score < 0.5: # Change score threshold to display lower probability detections
            break # We can break because scores are sorted
        
        if not(label == 2 or label == 3 or label == 5 or label == 7):
            continue # We skip drawing all other labels

        # Visualising bounding boxes and labels
        color = label_color(label)
        b = box.astype(int)
        draw_box(draw, b, color=color)
        caption = "{} {:.3f}".format(labels_to_names[label], score)
        draw_caption(draw, b, caption)
    
    # Saving image with detections
    cur_image += 1
    cv2.imwrite("test_outputs/" + "output_" + just_image_name[1], draw)
    print("Finished " + str(cur_image) + " out of " + str(input_images_len) + " test images.")

print("Testing completed.")