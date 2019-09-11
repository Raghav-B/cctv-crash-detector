import glob
import shutil as sh
import os
import random

validation_percent = 0.1

labels = glob.glob("../training_data/*.xml")
random.shuffle(labels)

print("Total imgs: " + str(len(labels)))
validation_imgs_num = int(validation_percent * len(labels))
print("Validation imgs to take: " + str(int(validation_percent * len(labels))))

main_index = 0
for i in range(0, validation_imgs_num):
    name = os.path.basename(labels[i])
    name = name[:-4]
    
    sh.move("../training_data/" + name + ".xml", "../validation_data/" + name + ".xml")
    sh.move("../training_data/" + name + ".jpg", "../validation_data/" + name + ".jpg")

    print("Moved " + str(i) + " out of " + str(len(labels)) + " images.")