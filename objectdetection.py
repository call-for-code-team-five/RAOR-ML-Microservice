import os
import cv2
import requests
import asyncio
import lxml.etree as ET
import numpy as np
from flask import Flask, send_file, send_from_directory, request
from flask_cors import CORS, cross_origin


port = os.getenv("PORT")
apikey = os.getenv("APIKEY")
bucketid = os.getenv("BUCKETID")
# port = 8080
# apikey = "M7m1jpF9nzFVFSqoJusmI7drwf77IR7bfRKm8OdMFIRb"
# bucketid = "roks-c5ooaecl02kmaahb914g-8c2f"

application = Flask(__name__)
cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'

parser = ET.XMLParser(recover=True)
loop = asyncio.get_event_loop()

async def retrieve_token():
    url = "https://iam.cloud.ibm.com/identity/token?apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"

    payload={}
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    token = response.json()['access_token']

    return token

def retrieve_bounding_boxes(token, image_no):
    url = "https://s3.eu.cloud-object-storage.appdomain.cloud/" + bucketid + "/image" + image_no + ".xml"

    payload={}
    headers = {
    'Content-Type': 'image/jpeg',
    'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    xmlresponse = response.text

    return xmlresponse


def abc(access_token, image_no):
    
    url = "https://s3.eu.cloud-object-storage.appdomain.cloud/" + bucketid + "/image" + image_no + ".jpg"

    payload={}
    headers = {
    'Content-Type': 'image/jpeg',
    'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    imgresponse = response._content
    
    arr = np.asarray(bytearray(imgresponse), dtype=np.uint8)
    
    # image = cv2.imread("image0.jpg")
    image = cv2.imdecode(arr, -1)

    # Window name in which image is displayed
    window_name = 'Image'

    tree = ET.ElementTree(ET.fromstring(retrieve_bounding_boxes(access_token, image_no), parser=parser)) 
    root = tree.getroot()

    
    for child in root:
        if child.tag == "object":
            
            # represents the top left corner of rectangle
            (x1, y1) = (int(child[4][0].text), int(child[4][1].text))
            
            # represents the bottom right corner of rectangle
            (x2, y2) = (int(child[4][2].text), int(child[4][3].text))
            
            label = child[0].text
            
            if label == 'fire':
                # red color
                color = (0, 0, 255)

            elif label == 'smoke':
                # orange color  
                color = (0, 128, 255)

            image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            (w, h), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)

            # Prints the text.    
            image = cv2.rectangle(image, (x1, y1 - 20), (x1 + w, y1), color, -1)
            image = cv2.putText(image, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)

    # cv2.imwrite("DetectedImage" + str(image_no) + ".jpg", image)
    
    # CV2 to Base64
    # base64_str = cv2.imencode('.jpg',image)[1].tostring()
    # base64_str = base64.b64encode(base64_str)

    # CV2 to PIL
    # image = Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))


    # cv2.imshow(window_name, image)

    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # return image


@application.route('/')
def initrun():
    return "Python ML Microservice is running"

@application.route('/detectObject')
def detectObject():
    image_no = request.args['imageNo']
    # image_no = '0'
    # image_no = '168'
    # image_no = '1062'

    access_token = loop.run_until_complete(retrieve_token())

    abc(access_token, image_no)

    # loop.close()

    try:
        return send_from_directory("", "DetectedImage" + str(image_no) + ".jpg")
        
    except FileNotFoundError:
        return "File Not Found"

    # return "Success"

if __name__ == '__main__':
    print ("Python ML Microservice is running in " + str(port))
    application.run(host="0.0.0.0", port=port)



