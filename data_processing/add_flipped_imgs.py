import os
import glob
import xml.etree.ElementTree as ET
import cv2

labels = glob.glob("../training_data/*.xml")

cur_index = 0
for xml_file in labels:
    name = os.path.basename(xml_file)
    name = name[:-4]

    to_flip_img = cv2.imread("../training_data/" + name + ".jpg")
    to_flip_img = cv2.flip(to_flip_img, 1)
    cv2.imwrite("../training_data/" + name + "_flipped.jpg", to_flip_img)

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for member in root.findall("object"):
        width = int(root.find("size")[0].text)
        xmin = int(member[4][0].text)
        xmax = int(member[4][2].text)
        member[4][0].text = str(width - xmax)
        member[4][2].text = str(width - xmin)
    
    tree.write(open("../training_data/" + name + "_flipped.xml", "w+"), encoding="unicode")

    cur_index += 1
    print("Flipped " + str(cur_index) + " out of " + str(len(labels)) + " images.")

