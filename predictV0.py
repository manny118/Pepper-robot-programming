#!/usr/bin/env python3.9
import time
import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')#avoid clashes with python2
from roboflow import Roboflow #using python3.9
import cv2
from PIL import Image
import numpy as np

class Predict:
    # crops the center of the palm with medication image
    def crop_center(pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))


    # extracts the colours of the pills
    def getColour(objectX, objectY, objectWidth, objectHeight, image):
        roi_x = int(objectX - objectWidth / 2)
        roi_y = int(objectY - objectHeight / 2)
        roi_width = int(objectWidth)
        roi_height = int(objectHeight)

        roi = image[roi_y : roi_y + roi_height, roi_x : roi_x + roi_width]

        cv2.imwrite("cropped_1.png", roi)
        im = Image.open('cropped_1.png')
        img = cv2.imread('cropped_1.png')
        print(img.shape)
        im_new = crop_center(im, 11, 11)
        croppedSeg = "cropped_1b.png" 
        im_new.save(croppedSeg, quality = 95)

        rf = Roboflow(api_key="rebe5aQSRWAGHWTPdVxS")
        project = rf.workspace("kh-9efja").project("cl-gorsx")
        model = project.version(1).model

        image = cv2.imread(croppedSeg)
        # infer on a local image
        prediction = model.predict(croppedSeg, confidence = 20, overlap = 30)#.json()
        print(prediction)
        #prediction.plot()
        print(prediction.json())
        colour = (prediction.json())
        colour = (dict((colour['predictions'][0])))['class']
        print("the col is: ", colour)
        return colour

    def checkMedication():
        rf = Roboflow(api_key="rebe5aQSRWAGHWTPdVxS")
        project = rf.workspace().project("pill-detection-0ixnz")
        model = project.version(4).model
        imgPath = "/home/generic/Emm/captures/img-1.png"
        image = cv2.imread(imgPath)

        prediction = model.predict(imgPath, confidence=30, overlap=30)
        print(prediction)
        # prediction.plot()
        # cv2.imshow(prediction)
        print(prediction.json())
        vals = dict(prediction.json())
        noOfItems = len(vals['predictions'])  # number of objects detected

        print("noOfItems: ", noOfItems)
        if noOfItems == 1:
          print("I see you have ", noOfItems, " pill")
        elif noOfItems > 1:
          print("I see you have ", noOfItems, " pills")

        arrayCols = []
        if(noOfItems == 0): # no object in the frame
          print("No items")
          print("I cannot see anything on your hand, please show me again")
        else:
          for i in range(noOfItems):
            objects = dict((vals['predictions'][i]))
            objectName = objects['class']
            objectX = objects['x']
            objectY = objects['y']
            objectWidth = objects['width']
            objectHeight = objects['height']
            print("objectName", " ", objectName)
            print("objectX", " ", objectX)
            print("objectY", " ", objectY)
            print("objectWidth", " ", objectWidth)
            print("objectHeight", " ", objectHeight)
            print("i: ", i)
            colour = getColour(objectX, objectY, objectWidth, objectHeight, image)
            arrayCols.append(colour)


        correct = ["blue", "green", "yellow"] 
        correct = np.sort(correct)
        
        cols = np.sort(arrayCols)
        print(cols)
        if (cols == correct).all():
            print("You have the correct dose")
        else:
            print("It seems you do not have the correct dose")
            print("You should have one blue, one green, one yellow")


if __name__ == "__main__":
    checkMedication()