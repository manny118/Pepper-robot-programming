# Detect the opening and the cabinet and navigate to the user

import smbclient
import rospy
from naoqi import ALProxy
import re # regex expression
import sys
sys.path.insert(1, "/home/generic/Emm/pepper")
from robot import Pepper
from movecode2 import Localise
from Landmark import LandmarkFinder
import time
from capture import Vision
import subprocess
from subprocess import call
import numpy as np

# set connection values to the robot
robotIP = "192.168.1.91"
PORT = 9559
pepper = Pepper(robotIP, 9559)
localise = Localise(robotIP, PORT)
landmark = LandmarkFinder(robotIP, PORT)
vision = Vision(robotIP, 9559)

face_service = ALProxy("ALFaceDetection", robotIP, PORT)
face_service.enableTracking(False) # disable face tracking

basic_awareness = ALProxy("ALBasicAwareness", robotIP, PORT)
basic_awareness.setTrackingMode("Head")
motionProxy =  ALProxy("ALMotion", robotIP, PORT)

tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)
tabletService = ALProxy("ALTabletService", robotIP, PORT)

# connect to the home assistant instance
smbclient.ClientConfig(username = 'homeassistant', password = 'HTH@IBST')


# track the fridge status
def checkFridgeStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor2.txt")
    with x as G:
        #print(x)
        num = (G.read())
        print(num[-4:])
        fridgeStatus = num[-4:]
    return fridgeStatus


# track the current temperature
def checkTempStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor.txt")#10.167.82.163
    currentTemp = 0
    with x as G:
        num = (G.read())
        print(num[-5:])
        currentTemp = num[-5:]
    return currentTemp


# track the medication cabinet
def cabinetStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor3.txt")
    currentTemp = 0
    with x as G:
        num = (G.read())
        print(num[-5:])
        cabinetState = num[-5:]
    return cabinetState


# continuously track the med cabinet until it opens
while True:
    # check current status of the cabinet
    cabinetState = cabinetStatus()
    if "off" in cabinetState:
        output = "The drawer is close"
    elif "on" in cabinetState: # cabinet is open
        localise.moveToLocation("cabinet")
        output = "I see you have opened the drawer. please do not take your medication on an empty stomach"
        tts.say(output)
        tabletService.showWebview("https://images.everydayhealth.com/images/which-medications-are-best-for-anxiety-disorders-1440x810.jpg?w=1990")
        tts.say("Please show me the medication on your palm")
        time.sleep(3)
        vision.captureImage()
        tts.say("Give me a few seconds to check for you")
        call("python3.9 predict.py", shell = True)

        with open("pred1.txt") as f:
            cols = f.readlines()
        print(type(cols[0]))
        outspeech = "It seems you have " + str(cols[0]) + " pills"
        tts.say(outspeech)

        pred = []
        with open("pred2.txt") as f:
            cols = f.readlines()
            for i in range(len(cols)):
                pred.append(cols[i].strip())
        print(pred)

        outpred = "It seems you have "
        for i in range(len(pred)):
            outpred += pred[i] + ", "
        tts.say(outpred)

        # initialise the correct doses
        correct = ["blue", "grey", "yellow"]
        correct = np.sort(correct)
        pred = np.sort(pred)
        out = "You should have one " + correct[0] + "one " + correct[1] + " and one " + correct[2]

        # the number of pills is checked against the correct number of pills
        if len(pred) != 0:
            if ((len(pred) < len(correct)) or (len(pred) > len(correct))):
                tts.say("You do not have the correct number of pills")
                tts.say(out)
            elif (len(pred) == len(correct)):
                if (pred == correct).all():
                    tts.say("You have the correct dose")
                else:
                    tts.say("You do not have the correct number of pills")
                    tts.say(out)
        else:
            tts.say("It seems you do not have the correct dose")

        break
        exit(0)


# log the medication activity
call("python3.9 medlog.py", shell = True)
time.sleep(5)
tabletService.hideImage()
