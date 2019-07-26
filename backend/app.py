from flask import Flask, render_template, request,Response,jsonify
import pandas as pd
import cv2
import numpy as np
import base64
from base64 import b64encode


app = Flask(__name__)
dict_cctv  ={}

imageString =""
@app.route('/check_for_crash',methods = ['GET','POST'])
def check_for_crash():
    i = 1
    li = []
    while(i<11):
        if(str(i) in dict_cctv ):
            if(dict_cctv[str(i)]!=''):
                li.append(i)
        i+=1
    print(li)
    return jsonify(customers=li)
@app.route('/add_face', methods=['GET', 'POST'])
def add_face():
    if request.method == 'POST':
        #  read encoded image
        global imageString
        num = request.form['num']
        imageString = base64.b64decode(request.form['img'])
        #print(imageString)
        #  convert binary data to numpy array
        #nparr = np.fromstring(imageString, np.uint8)
        global dict_cctv
        dict_cctv[num] = imageString
        image = np.asarray(bytearray(imageString), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        #print(nparr)
        #img=cv2.imdecode(nparr,cv2.IMREAD_COLOR)
        #  let opencv decode image to correct format
        #img = cv2.imdecode(np.fromstring(imageString, np.uint8), cv2.IMREAD_UNCHANGED)
        #cv2.imshow("frame", image)
        #cv2.waitKey(0)
        #print(image)
    return "list of names & faces"

@app.route("/show", methods=['GET', 'POST'])
def show():
    if request.method == 'POST':
        camera_num = request.form['num']
        image1 = b64encode(imageString).decode("utf-8")
        global dict_cctv
        dict_cctv[camera_num] = ''
        return render_template("photo_display.html", image=image1)
@app.route('/send')
def send():
    return render_template('form.html')
@app.route('/')
def send1():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, port=5002,host='0.0.0.0')
