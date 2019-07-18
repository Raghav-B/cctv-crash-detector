import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import cv2
import random

image_path = '../validation_data/'

def xml_to_csv(path):
    xml_list = []
    xml_files = glob.glob(path + '/*.xml')
    
    
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                    int(root.find('size')[0].text),
                    int(root.find('size')[1].text),
                    member[0].text,
                    int(member[4][0].text),
                    int(member[4][1].text),
                    int(member[4][2].text),
                    int(member[4][3].text)
                    )
            xml_list.append(value)
        
        just_img_name = os.path.basename(xml_file)
        just_img_name = just_img_name[:-4]
        to_flip_img = cv2.imread(image_path + just_img_name + ".jpg")
        to_flip_img = cv2.flip(to_flip_img, 1)
        cv2.imwrite(image_path + "flipped" + just_img_name + ".jpg", to_flip_img)

        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = ("flipped" + just_img_name + ".jpg",
                    int(root.find('size')[0].text),
                    int(root.find('size')[1].text),
                    member[0].text,
                    int(root.find('size')[0].text) - int(member[4][2].text),
                    int(member[4][1].text),
                    int(root.find('size')[0].text) - int(member[4][0].text),
                    int(member[4][3].text)
                    )
            xml_list.append(value)


    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

def main():
    xml_df = xml_to_csv(image_path)
    xml_df.to_csv('csvs/validation.csv', index=None)
    print('Successfully converted xml to csv.')

main()
