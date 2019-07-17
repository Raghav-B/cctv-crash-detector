import pandas as pd

csv_file = pd.read_csv("train.csv", names = ["path", "x1", "y1", "x2", "y2", "label"])

paths = csv_file["path"]
path_set = set()

for i in paths:
    path_set.add(i)

print("Total Images: " + str(len(path_set)))