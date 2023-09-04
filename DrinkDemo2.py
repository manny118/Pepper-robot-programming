# Pepper points to the fridge for the user to get some water

#!/usr/bin/env python3

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


# set connection values to the robot
robotIP = "192.168.1.109"
PORT = 9559
pepper = Pepper(robotIP, 9559)
localise = Localise(robotIP, PORT)
landmark = LandmarkFinder(robotIP, PORT)

face_service = ALProxy("ALFaceDetection", robotIP, PORT)
face_service.enableTracking(False) # disable face tracking
basic_awareness = ALProxy("ALBasicAwareness", robotIP, PORT)
basic_awareness.setTrackingMode("Head")

tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)
tabletService = ALProxy("ALTabletService", robotIP, PORT)
smbclient.ClientConfig(username = 'homeassistant', password = 'HTH@IBST')


# obtains the user's response
def getResponse():
    userIn = raw_input("Please enter response: ")
    return userIn


# tracks the fridge status
def checkFridgeStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor2.txt")
    with x as G:
        num = (G.read())
        print(num[-4:])
        fridgeStatus = num[-4:]
    return fridgeStatus


# tracks the current temperature
def checkTempStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor.txt")
    currentTemp = 0
    with x as G:
        num = (G.read())
        print(num[-5:])
        currentTemp = num[-5:]
    return currentTemp


# checks the activity log
def checkActivityInLogs(activity):
    logged = False
    if activity == "drink":
        label = "Drank"
    elif activity == "medication":
        label = "Medication taken at"
    else:
        label = "Unknown"

    with open("logdata.csv", "r") as file:
        output = file.readline()
        while output != "":
            if label in output:
                logged = True
                print("output: ", output)
            output = file.readline()
    return logged


# verify activity to be logged--promps the user for verification
def verifyLogActivity(drink):
    # log the activity
    time.sleep(7)
    output = "are you drinking the " + drink
    tts.say(output)

    response = getResponse()
    if response in vocabulary1:
        tts.say("Great!")

        logText = "Drank " + drink + " at "    # tea, water
        logData = [[logText, getCurrentTime(), current_day]]

        # update the activity log
        df = pd.DataFrame(logData)
        df.to_csv("logdata.csv", mode = 'a', index = False, header = False)


drinkStatus = checkActivityInLogs("drink")
if drinkStatus == False:
    currentTemp = checkTempStatus()
    currentTemp = str(currentTemp)
    print("currentTemp: ", float(currentTemp))
    output = ("The current temperature is " + currentTemp + " degrees")
    tts.say(output)
    tts.say("It seems you have not had a drink today. Would you like to have a glass of water now")

tabletService.showWebview("https://cdn.powerofpositivity.com/wp-content/uploads/2020/06/Nutritionists-Weigh-the-Pros-and-Cons-of-Water-Fasting_-1600x900.jpg")

vocabulary1 = ["yeah", "yes", "yes I would", "yea", "ya", "sure", "ofcourse", "yes yes", "yes yes yes"]
response = getResponse()
if response in vocabulary1:
    tts.say("I can show you the fridge, please follow me!")

    # navigate to the fridge and point at it
    localise.moveToLocation("fridge")
    landmark.pointAtLandmark("fridge")

else:
    tts.say("You can have a drink when you want to but do not forget.")

tabletService.showWebview("https://cdn.powerofpositivity.com/wp-content/uploads/2020/06/Nutritionists-Weigh-the-Pros-and-Cons-of-Water-Fasting_-1600x900.jpg")

verifyLogActivity("water")
