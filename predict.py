#!/usr/bin/env python3.9

import sys
# avoid clashes with python2
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
from roboflow import Roboflow #using python3.9
import cv2
from PIL import Image
import numpy as np
import json


class Predict:
    def __init__(self):
        self.checkMedication()

    # verifies the medication pils
    def checkMedication(self):
        rf = Roboflow(api_key = "XEcH3oe1640vgANKBAtL")
        project = rf.workspace("ms-uy4dq").project("mms-ptw9m")
        model = project.version(1).model
        imgPath = "/home/generic/Emm/captures/img-1.png"#"med2.jpg"
        image = cv2.imread(imgPath)

        prediction = model.predict(imgPath, confidence = 30, overlap = 30)


        print(prediction.json())
        vals = dict(prediction.json())
        noOfItems = len(vals['predictions'])  #number of objects detected
        print("noOfItems: ", noOfItems)

        with open("pred1.txt", "w") as f:
            f.write(str(noOfItems))

        arrayCols = []
        if(noOfItems == 0): # no object in the frame
          pass
        else:
          for i in range(noOfItems):
            objects = dict((vals['predictions'][i]))
            objectName = objects['class']
            objectX = objects['x']
            objectY = objects['y']
            objectWidth = objects['width']
            objectHeight = objects['height']
            arrayCols.append(objectName)

        print("arrayCols: ", arrayCols)
        jsonOut = {"number": noOfItems, "Colours": arrayCols}
        json_object = json.dumps(jsonOut, indent = 4)

        with open("predjs.json", "w") as f:
            f.write(json_object)


if __name__ == "__main__":
    mv1 = Predict()
