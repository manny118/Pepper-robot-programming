# User personalisation demo based on activity monitoring and user registration
# A background script that runs checks for ongoing conversation--ChatGPT

from naoqi import ALProxy
from subprocess import call
import json
import os
import csv
import time
from capture import Vision
from humandetect import Recognition
import sys
sys.path.insert(1, "/home/generic/Emm/pepper")
from robot import Pepper


# set connection values to the robot
robotIP = "192.168.1.91"
PORT = 9559
speech_engine = ALProxy("ALSpeechRecognition", robotIP, PORT)
speech_engine.subscribe("ASR")
tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)
txt2s = ALProxy("ALTextToSpeech", robotIP, 9559)
txt2s.setParameter("speed", 85) # adjust the speed for the guide
face_service = ALProxy("ALFaceDetection", robotIP, PORT)
memoryProxy = ALProxy("ALMemory", robotIP, PORT)
vision = Vision(robotIP, 9559)
recognition = Recognition(robotIP, PORT)
pepper = Pepper(robotIP, 9559)
speech_engine.unsubscribe("ASR")


# clears the answer to the previous question
def resetAnswer():
    if os.path.exists("gpt.txt"):
        open('gpt.txt', 'w').close()
resetAnswer()


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


# Retrieves the user's response
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


# retrieves the user's personalisation information from the JSON
def getUserInfo():
    with open("details.json", "r") as info:
        details = json.load(info)#info.read()

    details2 = dict(sorted(details.items(), reverse=True))
    responses = list(details2.values())
    output = ""
    for i in range(len(responses)):
        output += responses[i] + ". "
    print("user info: ", output)
    return output


# Retrieves the log of all sensor data from the house
def getActivityLog():
    output = ""
    with open('logdata.csv', 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            output += row[0] + row[1] + ". "
    print("activities: ", output)
    return output


# detect the user within the view
recognition.detectHuman()

# detect the user's face and recognises him/her
name = recognition.recognize_person()
print("name found is: ", name)

while True:
    if name == "Michael":
        out = "Hi " + name + " it is nice to see you."
        tts.say(out)
        break
    else:
        continue


out = "Hi " + name + " it is nice to see you."
tts.say(out)

userInfo = getUserInfo() # store user info from JSON
activities = getActivityLog() # store log of sensor data
activities = "These are the activities I have completed today: " + str(activities)


vocabulary1 = ["yeah", "yes", "yes yes", "yes I did", "yea", "ya", "sure", "ofcourse"]
tts.say("How are you today")
response = getResponse()
vocabulary = ["good",  "good good", "great", "fine", "I'm good", "I am good"]
if response in vocabulary:
    tts.say("Is there anything you would like to ask me")

response = getResponse()
if response in vocabulary1:
    tts.say("Is it a question about you")

response = getResponse()

# questions will be answered based on log and stored information
if response in vocabulary1:
    tts.say("You can please ask me")
    counter = 0
    while counter < 2:
        query = getResponse()
        GPT_question = str(activities) + ". " + userInfo  + ". Using the previous context only using the persona of an assistant, with a precise answer and little explanation. Simply say no if there is insufficient information and do not reference the context provided in your response" + query

        GPT_response = askGPT(GPT_question)
        tts.say(GPT_response)
        print(GPT_response)
        counter += 1

    time.sleep(1)
    tts.say("I can also help you with memory exercises. Would you like to try one?")
    response = getResponse()
    memChoice = ""

    if response in vocabulary1:
        while True:
            tts.say("Do you prefer word recall, story recall, or mind mapping")
            choice = getResponse()
            
            if choice in "word recall":
                memChoice = "word recall"
            elif choice in "story recall":
                memChoice = "story recall"
            elif choice in "mind mapping":
                memChoice = "mind mapping"
            else:
                tts.say("Sorry I did not get that")
                continue
            print("memChoice: ", memChoice)
            tts.say("Great choice. We can now start!")
            speech_engine.unsubscribe("ASR")

            query = "can you assume the persona of a memory coach for an elderly person and start an exercise without numbering your reponses and with little explanations. Continue the exercise with each response you receive. The user is given three options which include word recall, story recall and mind mapping. They prefer: " + choice
            GPT_response = askGPT(query)
            print(GPT_response)
            tts.say(GPT_response)
            break

        speech_engine.subscribe("ASR")
        counterAttempts = 0
        while counterAttempts < 5: # ask 5 times
            userResponse = getResponse()
            GPT_response = askGPT(userResponse)
            print(GPT_response)
            tts.say(GPT_response)
            counterAttempts += 1
        tts.say("Well done, we can continue again later")

else:
    tts.say("Sure, we can chat later")
