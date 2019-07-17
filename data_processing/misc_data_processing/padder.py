import json
import pandas as pd
import os
import cv2

json_temp = open("instances_train2017.json")
json_file = json.load(json_temp)
src_path = "../train2017/"

# Ids I want are: 1, 3, 4, 6, 8
# Basically, I need to create a list that looks like this:
# Images 
#   Bboxes, Label
# Iterate through all my images, check if for that particular image id, if any of the ids I want exist.
# Faster method is to iterate through all my annotations, and create a set that contains the image_ids of every image which contains a category_id that i'm looking for

cur_index = 0
total_items = len(json_file["annotations"])
category_labels = ["", "person", "", "car", "motorcycle", "", "bus", "", "truck"]

image_list = {}
for annotation in json_file["annotations"]:
    if (annotation["category_id"] == 1 or annotation["category_id"] == 3 or annotation["category_id"] == 4 or \
        annotation["category_id"] == 6 or annotation["category_id"] == 8):

        if annotation["image_id"] in image_list:
            image_list[annotation["image_id"]][1].append((category_labels[annotation["category_id"]], annotation["bbox"]))
        else:
            image_list[annotation["image_id"]] = ["", [(category_labels[annotation["category_id"]], annotation["bbox"])]]

    cur_index += 1
    print(f"Completed {cur_index} out of {total_items} items")

cur_index = 0
for image in json_file["images"]:
    if (image["id"] in image_list):
        path = os.path.abspath(os.path.join(src_path, image["file_name"]))
        path = path.replace("\\", "/")
        image_list[image["id"]][0] = path
    
    cur_index += 1
    print(f"Got {cur_index} out of {total_items} file names")

cur_index = 0
to_pad = len(image_list)
for item in image_list:
    input_img = cv2.imread(image_list[item][0])

    rows = input_img.shape[0]
    cols = input_img.shape[1]

    if rows < cols:
        padding = int((cols - rows) / 2)
        input_img = cv2.copyMakeBorder(input_img, padding, padding, 0, 0, cv2.BORDER_CONSTANT, (0, 0, 0))
    elif rows > cols:
        padding = int((rows - cols) / 2)
        input_img = cv2.copyMakeBorder(input_img, 0, 0, padding, padding, cv2.BORDER_CONSTANT, (0, 0, 0))
    else:
        cur_index += 1
        print("Finished padding " + str(cur_index) + " out of " + str(to_pad) + " images...")
        continue

    cv2.imwrite(image_list[item][0], input_img)

    cur_index += 1
    print("Finished padding " + str(cur_index) + " out of " + str(to_pad) + " images...")

print("Padding finished")