import pandas as pd
import time

csv_file = pd.read_csv("keras_train.csv", names = ["path", "x1", "y1", "x2", "y2", "label"])

num_objects = [0,0,0,0,0]
label_dict = {"vehicle": 0}

labels = csv_file["label"]

for i in labels:
    num_objects[label_dict[i]] += 1
    
for i in label_dict:
    print(f"{i}: {num_objects[label_dict[i]]}")

print("Total: " + str(sum(num_objects)))