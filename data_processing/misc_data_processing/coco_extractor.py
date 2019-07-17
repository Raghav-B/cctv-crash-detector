import json
import pandas as pd
import pathlib
import os

json_temp = open("instances_val2017.json")
json_file = json.load(json_temp)
src_path = "../val2017/"

cur_index = 0
total_items = len(json_file["annotations"])
category_labels = ["", "person", "", "car", "motorcycle", "", "bus", "", "truck"]

image_list = {}
for annotation in json_file["annotations"]:
    if (annotation["category_id"] == 3 or annotation["category_id"] == 4 or \
        annotation["category_id"] == 6 or annotation["category_id"] == 8 or annotation["category_id"] == 1):

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

for image in image_list:
    print(image_list[image])

print("Data extraction completed")

path_arr = []
x1_arr = []
y1_arr = []
x2_arr = []
y2_arr = []
label_arr = []

for item in image_list:
    for bbox in image_list[item][1]:
        path_arr.append(image_list[item][0])
        x1_arr.append(round(bbox[1][0]))
        y1_arr.append(round(bbox[1][1]))
        x2_arr.append(round(bbox[1][0]) + round(bbox[1][2]))
        y2_arr.append(round(bbox[1][1]) + round(bbox[1][3]))
        label_arr.append(bbox[0])

dataframe_structure = {"path": path_arr, "x1": x1_arr, "y1": y1_arr, "x2": x2_arr, \
    "y2": y2_arr, "label": label_arr}
df = pd.DataFrame(dataframe_structure, columns = ["path", "x1", "y1", "x2", "y2", "label"])
df.to_csv("validation.csv", index = False)