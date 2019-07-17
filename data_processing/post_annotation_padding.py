import numpy as np
import pandas as pd
import os

csv_file = pd.read_csv("validation.csv")

for i in range(0, len(csv_file)):
	rows = csv_file.ix[i,2]
	cols = csv_file.ix[i,1]

	padding = 0
	if rows < cols:
		padding = int((cols - rows) / 2)
	elif rows > cols:
		padding = int((rows - cols) / 2)
	
	csv_file.ix[i,5] += padding
	csv_file.ix[i,7] += padding

csv_file.to_csv("validation_new.csv", index = False)