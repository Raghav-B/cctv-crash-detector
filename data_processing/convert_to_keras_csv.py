import numpy as np
import pandas as pd
import os

csv_file = pd.read_csv("validation.csv")
cur_dir = os.getcwd()
print(cur_dir)

new_paths = csv_file["filename"]
new_paths = new_paths.copy()

loop_index = 0
for i in new_paths:
	temp = os.path.join(cur_dir + "/validation_extracted_frames/" + str(i))
	temp = temp.replace("\\", "/")
	new_paths[loop_index] = temp
	loop_index += 1

print(new_paths)

new_dataframe = pd.concat([new_paths, csv_file["xmin"], csv_file["ymin"], csv_file["xmax"],\
csv_file["ymax"], csv_file["class"]], axis = 1)

new_dataframe.to_csv("keras_validation.csv", index = False)