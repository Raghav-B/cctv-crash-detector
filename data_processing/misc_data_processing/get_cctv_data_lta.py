import json
import urllib
from urllib.request import urlretrieve
from urllib.parse import urlparse
import httplib2 as http #External library
import time

if __name__=="__main__":
    #Authentication parameters
    headers = { 'AccountKey' : 'eNtRO9TDQuKCXNE/FromgA==', 'accept' : 'application/json'} #this is by default

    total_image_index = 3185

    while True:
        #API parameters
        #Build query string & specify type of API call
        target = urlparse("http://datamall2.mytransport.sg/ltaodataservice/Traffic-Images")
        print(target.geturl())
        method = 'GET'
        body = ''

        #Get handle to http
        h = http.Http()
        #Obtain results
        response, content = h.request(target.geturl(), method, body, headers)
        #Parse JSON to print
        jsonObj = json.loads(content)
        
        images_col = len(jsonObj["value"])

        for i in range(0, len(jsonObj["value"])):
            image_link = jsonObj["value"][i]["ImageLink"]
            image_name = "Data/" + str(total_image_index) + "_" + jsonObj["value"][i]["CameraID"] + ".jpg"

            urlretrieve(image_link, image_name)

            total_image_index += 1
            print("Images downloaded: " + str(total_image_index))
           
        print("Now sleeping for 5 mins")
        time.sleep(60 * 5)

        #print(json.dumps(jsonObj, sort_keys=True, indent=4))
        
        #Save result to file
        #with open("bus_routes.json","w") as outfile:
            #Saving jsonObj["d"]
        #    json.dump(jsonObj, outfile, sort_keys=True, indent=4, ensure_ascii=False)