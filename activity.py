# Activity logger/tracker

import smbclient
import time
from datetime import date
from subprocess import call
import os
import pandas as pd

robotIP = "192.168.1.91"
PORT = 9559

# connect to the home assistant instance
smbclient.ClientConfig(username = 'homeassistant', password = 'HTH@IBST')


# tracks the fridge status
def checkFridgeStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor2.txt")
    with x as G:
        num = (G.read())
        fridgeStatus = num[-4:]
    return fridgeStatus


# tracks the current temperature
def checkTempStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor.txt")
    currentTemp = 0
    with x as G:
        num = (G.read())
        currentTemp = num[-5:]
    return currentTemp


# tracks the medication cabinet
def checkCabinetStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor3.txt")
    cabinetState = 0
    with x as G:
        num = (G.read())
        cabinetState = num[-5:]
    return cabinetState


# tracks the oven
def checkOvenStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor5.txt")
    ovenState = 0
    with x as G:
        num = (G.read())
        ovenState = num[-5:]
    return ovenState


# retrieves the current time
def getCurrentTime():
    current_time = time.strftime("%H:%M")
    return current_time

# obtain date and time
today = date.today()
current_day = today.strftime("%B %d, %Y")
df = pd.DataFrame(columns=['Activity', 'Time', 'Day'])
df.to_csv("logdata.csv")


def storeInfo(logData):
    df = pd.DataFrame(logData) #columns=None
    df.to_csv("logdata.csv", mode = 'a', index = False, header = False)


# initialise time and details for core activities
logData = [["Medication to be taken at ", "10:00 am"]]
storeInfo(logData)

logData = [["Medication to be taken at ", "14:00 pm"]]
storeInfo(logData)

logData = [["Medication to be taken at ", "18:00 pm"]]
storeInfo(logData)

logData = [["Medication to be taken at ", "22:05 pm"]]
storeInfo(logData)


fridgeFlag = False
cabinetFlag = False
ovenFlag = False

# continuously tracks the activities
while True:
    # retrieves the current status
    fridgeStatus = checkFridgeStatus()
    cabinetStatus = checkCabinetStatus()
    ovenStatus = checkOvenStatus()

    if "on" in ovenStatus and ovenFlag == False:
        output = "I see you have opened the oven. What do you want to get?"
        print("The oven has been opened")
        logData = [["Oven opened at ", getCurrentTime(), current_day]]
        df = pd.DataFrame(logData)
        df.to_csv("logdata.csv", mode = 'a', index = False, header = False)
        ovenFlag = True

    if "off" in ovenStatus:
        ovenFlag = False


    if "on" in fridgeStatus and fridgeFlag == False:
        output = "I see you have opened the fridge. What do you want to get?"
        print("The drawer has been opened")
        logData = [["Fridge opened at ", getCurrentTime(), current_day]]
        df = pd.DataFrame(logData)
        df.to_csv("logdata.csv", mode = 'a', index = False, header = False)
        fridgeFlag = True

    if "off" in fridgeStatus:
        fridgeFlag = False


    if "on" in cabinetStatus and cabinetFlag == False:
        output = "I see you have opened the fridge. What do you want to get?"
        print("The cabinet has been opened")
        logData = [["Medication cabinet opened at ", getCurrentTime(), current_day]]
        df = pd.DataFrame(logData) # columns=None
        df.to_csv("logdata.csv", mode = 'a', index = False, header = False)
        cabinetFlag = True

    if "off" in cabinetStatus:
        cabinetFlag = False
