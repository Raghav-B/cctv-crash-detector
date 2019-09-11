import glob
import shutil as sh
import os
import xml.etree.ElementTree as ET
import random

validation_percent = 0.1

labels = glob.glob("training_data/*.xml")
random.shuffle(labels)

print("Total imgs: " + str(len(labels)))
validation_imgs_num = int(validation_percent * len(labels))
print("Validation imgs to take: " + str(int(validation_percent * len(labels))))

main_index = 0
for i in range(0, validation_imgs_num):
    name = os.path.basename(labels[i])
    name = name[:-4]
    
    sh.move("training_data/" + name + ".xml", "validation_data/" + name + ".xml")
    sh.move("training_data/" + name + ".jpg", "validation_data/" + name + ".jpg")

    print("Moved " + str(i) + " out of " + str(len(labels)) + " images.")

    #tree = ET.parse(i)
    #root = tree.getroot()
    #rows = int(root.find("size").find("height").text)
    #cols = int(root.find("size").find("width").text)

    #if (root.find("folder").text == "validation_extracted_frames"):
    #for member in root.findall("object"):
    #    if (member[0].text == "vehicle"):
            #member[0].text = "non-bike"

            #padding = 0
            #Eif rows < cols:
            #    padding = int((cols - rows) / 2)
            #elif rows > cols:
            #    padding = int((rows - cols) / 2)
            
            #member[4].find("ymin").text = str(int(member[4].find("ymin").text) + padding)
            #member[4].find("ymax").text = str(int(member[4].find("ymax").text) + padding)

    #tree.write(open(i, "w+"), encoding="unicode")


    #sh.copy("test/" + name + ".jpg", "training_data/" + str(main_index) + ".jpg")
    #sh.copy("test/" + name + ".xml", "training_data/" + str(main_index) + ".xml")
    #main_index += 1