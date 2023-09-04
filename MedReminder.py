# Full medication demo
# here the user opens the cabinet and Pepper comes over

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
from subprocess import call
import numpy as np
import json
import os
from humandetect import Recognition
import multiprocessing as mp


# set connection values to the robot
robotIP = "192.168.1.91"
PORT = 9559
pepper = Pepper(robotIP, 9559)
localise = Localise(robotIP, PORT)
landmark = LandmarkFinder(robotIP, PORT)
vision = Vision(robotIP, 9559)

face_service = ALProxy("ALFaceDetection", robotIP, PORT)
face_service.enableTracking(False) # disable face tracking
motionProxy =  ALProxy("ALMotion", robotIP, PORT)
txt2s = ALProxy("ALTextToSpeech", robotIP, 9559)
txt2s.setParameter("speed", 90) # adjust the speed for the guide
tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)

tabletService = ALProxy("ALTabletService", robotIP, PORT)
smbclient.ClientConfig(username = 'homeassistant', password = 'HTH@IBST')

recognition = Recognition(robotIP, PORT)
basic_awareness = ALProxy("ALBasicAwareness", robotIP, PORT)
basic_awareness.setTrackingMode("Head") # stop unnecessary head rotations


# track the cabinet
def cabinetStatus():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor3.txt")
    with x as G:
        num = (G.read())
        print(num[-5:])
        cabinetState = num[-5:]
    return cabinetState


# clears the answer to the previous question answered by ChatGPT
def resetAnswer():
    if os.path.exists("gpt.txt"):
        open('gpt.txt', 'w').close()
resetAnswer()


# retrieve Pepper's distance from home assistant hub
def beaconPepper():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor6.txt")
    with x as G:
        num = (G.read())
        pepperDist = num[-2:]
        try:
            pepperDist = int(num[-2:])
        except:
            print("error reading beaconPepper")
        print(pepperDist)
    return pepperDist


# retrieve lemsip pack's distance from home assistant hub
def beaconLemsip():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor7.txt")
    with x as G:
        num = (G.read())
        lemsipDist = num[-2:]
        try:
            lemsipDist = int(num[-2:])
        except:
            print("error reading beaconLemsip")
        print(lemsipDist)
    return lemsipDist


# retrieve paracetamol pack's distance from home assistant hub
def beaconPara():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor8.txt")
    with x as G:
        num = (G.read())
        paraDist = num[-2:]
        try:
            paraDist = int(num[-2:])
        except:
            print("error reading beaconPara")
        print(paraDist)
    return paraDist


# retrieve ibruprofen pack's distance from home assistant hub
def beaconIbru():
    x = smbclient.open_file("192.168.1.135/config/logs/sensor9.txt")
    with x as G:
        num = (G.read())
        ibruDist = num[-2:]
        try:
            ibruDist = int(num[-2:])
        except:
            print("error reading beaconIbru")
        print(ibruDist)
    return ibruDist


# compare the distances of each iBeacon
def beaconDistances(dist_queue):
    pepperDist = []
    lemsipDist = []
    ibruDist = []
    paraDist = []

    # record for five seconds
    startTime = time.time()
    endTime = time.time()

    while (endTime - startTime) < 5:
        print("\n")
        print("vals: ", beaconPepper(), beaconLemsip(),  beaconPara(),  beaconIbru())

        pepperDist.append(beaconPepper())
        lemsipDist.append(beaconLemsip())
        ibruDist.append(beaconIbru())
        paraDist.append(beaconPara())
        endTime = time.time()

    pepperAvg = np.average(pepperDist)
    ibruAvg = np.average(ibruDist)
    paraAvg = np.average(paraDist)
    lemsipAvg = np.average(lemsipDist)

    print("pepperAvg: ", pepperAvg)
    print("ibruAvg: ", ibruAvg)
    print("paraAvg: ", paraAvg)
    print("lemsipAvg: ", lemsipAvg)

    allDist = [pepperAvg, ibruAvg, paraAvg, lemsipAvg]
    dist_queue.put(allDist)
    return dist_queue


# find the closest beacon to Pepper that is, a medication pack
def closestBeacon(arr, val):
    dists = []
    min_diff = float('inf')
    for num in arr:
        diff = abs(num - val)
        if diff < min_diff:
            min_diff = diff
            closest_nums = [num]
        elif diff == min_diff:
            closest_nums.append(num)
    return closest_nums


# retrieves the medication name via inference
def getMedName():
    call("python3.9 medPredict.py", shell = True)
    medName = ""
    if os.path.exists("medname.txt"):
        with open("medname.txt", "r") as f:
            medName = f.read()
        print("medName: " + medName)
    if os.path.exists("medname.txt"):
        os.remove("medname.txt")

    return medName


# Queries ChatGPT for a responseby reading the textfile storing the response
def askGPT(response):
    with open("askGPT.txt", "w") as file:
        file.write(response)

    GPT_response = ""
    if os.path.exists("gpt.txt"):
        while True:
            with open("gpt.txt", "r") as file:
                GPT_response = file.read()
            if len(str(GPT_response)) < 2:
                continue
            else:
                resetAnswer()
                break
    return GPT_response


# retrieves the current time of the day
def getCurrentTime():
    current_time = time.strftime("%H:%M")
    return current_time


# obtain user's response
def getResponse():
    listenCounter = 0 # no of times it listens for a response
    userInput = ""
    while listenCounter <= 2:
        try:
          userInput = pepper.listenTo()
          print("Original decoded speech: ", userInput)
          return userInput
          break
        except:
          tts.say("Sorry, I did not understand that")
          listenCounter += 1


# detect the user within the view
recognition.detectHuman()
face_detected = recognition.detectFace()

if face_detected:
    name = recognition.recognize_person()
    print("name found is: ", name)

time.sleep(4)
if name is "Michael":
    out = "Hi " + name + " it is time for you to take your medication."
    tts.say(out)

# waits for a specific time to check
current_time = 0
while True:
    current_time = getCurrentTime()
    if current_time == "10:00":
        print("Now is the time")
    break


regex = re.compile('[^a-zA-Z\s]')
pepper.say("Would you like to take your medication now?")
vocabulary1 = ["where is it", "where can I find it", "where", "can you find it", "what is it", "yes"]
response = getResponse()
vocabulary2 = ["yeah", "yes", "yes yes", "yea", "ya", "sure", "yes I did"]


# navigates to the medication cabinet with the user
if response in vocabulary1:
    pepper.say("I can show you. Please follow me")
    localise.moveToLocation("greenchair")
    basic_awareness.setTrackingMode("Head") # stop unnecessary rotations

    face_service.enableTracking(False) # disable face tracking
    call("python2.7 speechTest.py", shell = True) # does the prediction

    landmark.pointAtLandmark("cabinet")  # Check the medication drawer beside the green chair
    tts.say("You can now open the first drawer")
    tts.say("The medication cabinet is beside the green chair")


# point to the cabinet after navigating to it
while True:
    cabinetState = cabinetStatus() # obtain cabinet status
    if "off" in cabinetState:
        output = "The drawer is close"
    elif "on" in cabinetState:
        output = "I see you have opened the drawer. please do not take your medication on an empty stomach. Use it with water"
        tts.say(output)
        tabletService.showWebview("https://images.everydayhealth.com/images/which-medications-are-best-for-anxiety-disorders-1440x810.jpg?w=1990")

        tts.say("For your afternoon medication, you need to take a pill each of paracetamol, lemsip, and strepsils")
        currentmeds = ["paracetamol", "lemsip", "ibuprofen"]
        allmeds = ["paracetamol", "lemsip", "strepsils", "ibuprofen"]
        print("current list: ", currentmeds)
        counter = 0
        while counter < 5:
            if counter == 0:
                tts.say("Please show me the first medication pack to verify")
            else:
                tts.say("Please show me the next medication pack to verify")
            time.sleep(3)
            vision.captureImage()
            tts.say("Thank you")


            # multi processing to verify medication packs
            dist_queue = mp.Queue()
            dist_queue2 = mp.Queue()
            p1 = mp.Process(target = beaconDistances, args=(dist_queue,))
            p2 = mp.Process(target = getMedName, args=(dist_queue2,))
            print("\n\nprocesses called")
            p1.start()
            p2.start()
            print("\n\nprocesses started")
            p1.join()
            p2.join()
            print("\n\nprocesses joined")

            distances = dist_queue.get()
            medName = dist_queue2.get()

            print("Distances: ", distances)
            print("medName: ", medName)

            closest_beacon = closestBeacon(distances, robotDist)
            print("Closest:", closest_beacon)

            ind = distances.index(closest_beacon)
            print("ind: ", ind)

            # closest medication to Pepper
            if ind == 0:
                closeMed = 'lemsip'
            elif ind == 1:
                closeMed = 'paracetamol'
            elif ind == 1:
                closeMed = 'ibuprofen'
            else:
                closeMed = 'strepsils'

            print(closeMed)

            if medName == closeMed:
                print("verified")

            call("python3.9 medPredict.py", shell = True)
            medName = getMedName()
            beaconDistances()


            if medName in currentmeds:
                currentmeds.remove(medName)
                output = "Correct. That is the " + medName + " pack"
                tts.say(output)
            elif medName in allmeds:
                incorrectMed = "That is the " + medName + " and it is not to be taken now"
                tts.say(incorrectMed)
            else:
                tts.say("Sorry, please show me again")
                continue
            
            counter += 1
            if len(currentmeds) == 0:
                tts.say("Now you have all 3 medications. Please take one from each pack")
                break

        tts.say("Please show me the medication on your palm")
        landmark.moveHead(0, 0, motionProxy)
        time.sleep(1)

        # adjust the head position to capture the pills
        amntY = 0.2
        amntX = 0.2
        headJoints = ["HeadPitch", "HeadYaw"]
        headSpeed = 0.1
        headPos = [float(amntY), float(amntX)]
        motionProxy.angleInterpolationWithSpeed(headJoints, headPos, headSpeed)

        time.sleep(7)
        tts.say("please say yes when you are ready for me to verify")
        while True:
            userReady = getResponse()
            if response in vocabulary2:
                tts.say("Give me a few seconds to check for you")
                vision.captureImage()
            else:
                continue



        call("python3.9 predict.py", shell = True) # does the prediction

        medPrediction = []
        with open("predjs.json", "r") as f:
            medPrediction = json.load(f)

        medNo = int(medPrediction["number"])
        if medNo > 1:
            outspeech = "It seems you have " + str(medNo) + " pills"
        else:
            outspeech = "It seems you have " + str(medNo) + " pill"
        tts.say(outspeech)

        print(medPrediction["Colours"])
        pred = medPrediction["Colours"]
        outpred = "It seems you have "

        if len(pred) != 0:
            for i in range(medNo):
                outpred += str(pred[i])
                if i != medNo-1:
                    outpred += " and"
            tts.say(outpred)

        cabinetState = "off"
        correct = ["blue", "grey", "yellow"]#green
        correct = np.sort(correct)

        if len(pred) != 0:
            pred = np.sort((pred))   # pred = np.sort(pred)   # cols = np.unique(cols)
        out = "You should have one " + correct[0] + "one " + correct[1] + " and one " + correct[2]

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
            tts.say(out)
        break

        tts.say("Do you need some help or is there something you want to ask me")

        userResponse =  getResponse() #"should I use my medication with water"
        verifyQuestion = "with a yes or no response, does this make sense: " + userResponse
        askQuestion = "in a few words: " + userResponse

        tts.say("Give me a few seconds please")
        with open("askGPT.txt", "w") as file:
            file.write(verifyQuestion)
        verifyAnswer = ""
        verifyAnswer = askGPT(verifyQuestion)
        print("verifyAnswer: ", verifyAnswer)

        countResponses = 0
        while countResponses < 3:
            if verifyAnswer == "Yes." or verifyAnswer == "Yes":
                GPT_response = askGPT(askQuestion) # readGPT()
                print("final GPT_response: " + GPT_response)
                break

            elif verifyAnswer == "no":
                tts.say("please can you say that again")
            countResponses += 1

        time.sleep(7)
        tts.say("did you take it with water?")

        response = getResponse()
        if response in vocabulary2:
            tts.say("Good")

        tts.say("did you take all pills you showed me?")
        response = getResponse()
        if response in vocabulary2:
            tts.say("Well done")

        exit(0)

# update the medication log and send email update
call("python3.9 medlog.py", shell = True)
call("python3.9 sendEmail.py", shell = True)
time.sleep(10)
tabletService.hideImage()
