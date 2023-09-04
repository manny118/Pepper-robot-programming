# Kettle demo
# Here the robot asks the user to have a drink
# The kettle must be in its on position but without power

from naoqi import ALProxy
import sys
sys.path.insert(1, "/home/generic/Emm/pepper")
from robot import Pepper
import time
import re
from subprocess import call
from movecode2 import Localise
from Landmark import LandmarkFinder
import os
import pandas as pd
from datetime import date
from humandetect import Recognition


robotIP = "192.168.1.91"
PORT = 9559
pepper = Pepper(robotIP, 9559)      #10.167.86.37
tabletService = ALProxy("ALTabletService", robotIP, PORT)
tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)
txt2s = ALProxy("ALTextToSpeech", robotIP, 9559)
speech_engine = ALProxy("ALSpeechRecognition", robotIP, PORT)
speech_engine.subscribe("ASR")
tabletService.setVolume(15)

txt2s.setParameter("speed", 90) # adjust the speed for the guide
localise = Localise(robotIP, PORT)
landmark = LandmarkFinder(robotIP, PORT)
recognition = Recognition(robotIP, PORT)
speech_engine.unsubscribe("ASR")

# obtain date and time
today = date.today()
current_day = today.strftime("%B %d, %Y")


# function that checks the response of the user from a list
def checkResponse(vocabulary):
    listenCounter = 0 # no of times it listens for a response
    while listenCounter <= 2:
        try:
          userInput = pepper.listenTo()
          print("Original decoded speech: ", userInput)
          if i in range(len(vocabulary1)):
              if userInput in vocabulary1[i]:
                  return True
          else:
              pepper.say("Please can you say that again?")
              listenCounter += 1
        except:
          tts.say("Sorry, I did not understand that")
          listenCounter += 1
    return False


# clears the answer to the previous question answered by ChatGPT
def resetAnswer():
    if os.path.exists("gpt.txt"):
        open('gpt.txt', 'w').close()
resetAnswer()


# retrieves the user's input
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
    # return userInput


# retrieves the current time of the day
def getCurrentTime():
    current_time = time.strftime("%H:%M")
    return current_time


# Queries ChatGPT for a response
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


# toggles the state of the smart plug - on or off
def togglePlug():
    call("python3.9 kasaplug2.py", shell = True)
    while True:
        if os.path.exists("plug.txt"):
            logFile = open("plug.txt", "r")
            plugStatus = logFile.read()
            print("logFile: ", logFile)
            if plugStatus == "Boiled":
                tts.say("The kettle is boiled.")
            break
        else:
            continue


# plays a song using the robot's tablet
def playmusic():
    call("python3.9 playmusic.py", shell = True)
    URL = ""
    with open("music.txt", "r") as f:
        URL = f.read()
    newURL = '"'
    for i in range(len(URL)):
        newURL += URL[i]
    newURL = newURL + '"'
    tabletService.showWebview(URL)
    time.sleep(90)


# Queries ChatGPT for a response
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

        # logText = "Drank water at "    # tea, water
        logText = "Drank " + drink + " at "    # tea, water
        logData = [[logText, getCurrentTime(), current_day]]

        # update the activity log
        df = pd.DataFrame(logData) #columns=None
        df.to_csv("logdata.csv", mode = 'a', index = False, header = False)

# waits for a specific time to check
current_time = 0
while True:
    current_time = getCurrentTime()
    if current_time == "10:51":
        print("Now is the time")
        #break
    break

txt2s.setParameter("speed", 90) # adjust the speed for the guide

vocabulary1 = ["yeah", "yes", "yes I would", "yea", "ya", "sure", "ofcourse", "yes yes", "yes yes yes"]
vocabulary2 = ["no", "I'm fine", "I am fine", "I'm okay", "no thanks"]
beverages = ["tea", "coffee", "a cup of tea", "cup of tea", "t"]
drinks = ["juice", "coke", "fanta"]

# checks for a specific user
while True:
    # detect the user within the view
    recognition.detectHuman()

    # detect the user's face and recognises him/her
    name = "Micheal" #recognition.recognize_person() #
    print("name found is: ", name)
    time.sleep(3)
    if name is "Micheal":
        out = "Hi " + name + "it is nice to see you."
        tts.say(out)
        break
    else:
        continue


# check logs for activity
checkLog = checkActivityInLogs("drink")

# False if no drink has been taken during the day
if checkLog == False:
    output = "It is" + current_time + " and it seems you have not had a drink today"
    tts.say(output)


tts.say("Would you like to have something to drink")

response = getResponse()
print("response: ", response)

if response in vocabulary1:
    print("What would you like to have?")
    tts.say("What would you like to have?")
    response = getResponse()
    print("response: ", response)

    if (response in beverages) or ("tea" in response):
        tts.say("should I turn the kettle on for you?")
        response = getResponse()
        print("response: ", response)

        if response in vocabulary1:
            tts.say("okay I will turn on the kettle for you and remind you when it is boiled.")

            togglePlug() # turn kettle on and track status
            tts.say("Do you want me to come with you to the kitchen to prepare the tea?")
            response = getResponse()

            if response == "yes":
                tts.say("Okay, let's go")
                # NAVIGATE TO THE KITCHEN -------
                localise.moveToLocation("kitchen")
                tabletService.showWebview("https://static.independent.co.uk/s3fs-public/thumbnails/image/2018/01/17/11/istock-466073662.jpg?quality=75&width=1800&auto=webp")

                GPT_response = askGPT("in simple steps without a prelude sentence and with no numbering of steps, how can I make a cup of tea after water is boiled")
                tts.say(GPT_response)

                tts.say("Do you have a question?")
                response = getResponse()

                while True:
                    if response in vocabulary1:
                        tts.say("Please ask")
                        question = getResponse()
                        GPT_response = askGPT(question)
                        tts.say(GPT_response)
                        tts.say("Do you have another question?")
                        response = getResponse()
                        continue
                    break
            elif response in vocabulary2:
                tts.say("Please be careful with the hot water.")

            verifyLogActivity("tea") # verify that activity was completed

        elif response == "no":
            tts.say("Sure, let me know when you need my help.")

        time.sleep(3)
        tts.say("Should I play your favourite song")
        response = getResponse()
        if response in vocabulary1:
            playmusic() # retrieves user information for fav song
            time.sleep(140)
        else:
            tts.say("Okay, that is fine.")

    elif response == "water":
        tts.say("would you like water from the kettle or fridge")
        response = getResponse()
        print("response: ", response)

        if response == "kettle":
            tts.say("should I turn the kettle on for you?")
            response = getResponse()
            print("response: ", response)

            if response in vocabulary1:
                tts.say("How long should I turn the kettle on?")
                response = getResponse()
                print("response: ", response)

                if "minutes" in response or "minute" in response:
                    duration = int(re.findall(r'\d+', response)[0])
                    duration = duration * 60
                elif "seconds" in response:
                    duration = int(re.findall(r'\d+', response)[0])
                print(duration)
                with open("plug2.txt", "w") as f:
                    f.write(str(duration))
                call("python3.9 kasaplug3.py", shell = True)
                tts.say("The kettle is boiled")

        elif response == "fridge":
            # fridge locator
            tts.say("Should I show you where it is?")
            vocabulary = ["yeah", "yes", "yes please", "yea", "ya", "sure", "ofcourse", "please do"]
            vocabulary2 = ["no", "no thanks", "I can find it", "I know where it is", "don't bother"]
            response = checkResponse(vocabulary)
            if response in vocabulary:
                tts.say("okay, please come with me to the fridge")
                coord = localise.moveToLocation("fridge")  ########talk while walking API proxy
                landmark.pointAtLandmark("fridge")
                tts.say("You can open the fridge and get some water")
            elif response in vocabulary2:
                tts.say("okay, that's fine")

        tabletService.showWebview("https://cdn.powerofpositivity.com/wp-content/uploads/2020/06/Nutritionists-Weigh-the-Pros-and-Cons-of-Water-Fasting_-1600x900.jpg")
        verifyLogActivity("water")


    elif response in drinks:
        tts.say("You might find some in the fridge. Would you like me to show you the fridge?")
        response = getResponse()

        if response in vocabulary1:
            # navigate to the fridge
            localise.moveToLocation("fridge")
            landmark.pointAtLandmark("fridge")
            tts.say("You can open the fridge and get a drink")
            tabletService.showWebview("https://cdn.powerofpositivity.com/wp-content/uploads/2020/06/Nutritionists-Weigh-the-Pros-and-Cons-of-Water-Fasting_-1600x900.jpg")
            verifyLogActivity("a soft drink")

elif response in vocabulary2:
    tts.say("Okay, I think you should have a drink soon.")
