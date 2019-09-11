import numpy as np
import pandas as pd
import os

csv_file = pd.read_csv("csvs/train.csv")
src_path = "../training_data/"

new_paths = csv_file["filename"]
new_paths = new_paths.copy()

loop_index = 0
for i in new_paths:
	path = os.path.abspath(os.path.join(src_path, str(i)))
	path = path.replace("\\", "/")
	
	new_paths[loop_index] = path
	loop_index += 1

print(new_paths)

new_dataframe = pd.concat([new_paths, csv_file["xmin"], csv_file["ymin"], csv_file["xmax"],\
csv_file["ymax"], csv_file["class"]], axis = 1)

new_dataframe.to_csv("csvs/keras_train.csv", index = False)