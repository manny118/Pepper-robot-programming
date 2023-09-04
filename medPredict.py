#!/usr/bin/env python3.9

# script for loading the ML model that verifies the medication packs

import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
from roboflow import Roboflow
rf = Roboflow(api_key = "AUv2OyA6686LhvmIAHas")
project = rf.workspace("packs").project("pks")
model = project.version(1).model

imgPath = "/home/generic/Emm/captures/img-1.png"
image = cv2.imread(imgPath)

prediction = model.predict(imgPath, confidence = 30, overlap = 30)
# prediction.plot()
# print(prediction.json())
vals = dict(prediction.json())

objects = dict((vals['predictions'][0]))
objectName = objects['class']

with open("medname.txt", "w") as f:
    f.write(str(objectName))
