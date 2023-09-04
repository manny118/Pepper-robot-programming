# User registration demo with reminder of who they are

from naoqi import ALProxy
from subprocess import call
import json
import sys
from capture import Vision
import time
import os
from humandetect import Recognition
sys.path.insert(1, "/home/generic/Emm/pepper")
from robot import Pepper


# set connection values to the robot
robotIP = "192.168.1.91"   #"192.168.1.139"
PORT = 9559
pepper = Pepper(robotIP, 9559)
face_service = ALProxy("ALFaceDetection", robotIP, PORT)
tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)
txt2s = ALProxy("ALTextToSpeech", robotIP, 9559)
txt2s.setParameter("speed", 85) # adjust the speed for the guide
memoryProxy = ALProxy("ALMemory", robotIP, PORT)
vision = Vision(robotIP, 9559)
basic_awareness = ALProxy("ALBasicAwareness", robotIP, PORT)
basic_awareness.setTrackingMode("Head")
recognition = Recognition(robotIP, PORT)


# obtains the response from the user
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


# detect a human within the view
face_detected = recognition.detectHuman()
tts.say("Hey there, how are you?")
vocabulary = ["good", "great", "fine"]
response = getResponse()
if response in vocabulary:
    tts.say("That is lovely. I'm Pepper, and I would like to know you. What is your first name?")


details = {} # JSON to store user details
response = getResponse()
details['name'] = "My first name is " + response
print(response)
tts.say("Good thanks.")


# detect the user's face within the view
face_detected = recognition.detectFace()

# face detection successfully completed
if face_detected:
    # store the user face for recognition later
    face_detected, name = recognition.learn_face(response)
    print("user recognition done")
    tts.say("I will remember your face")


tts.say("What is your favorite meal")
response = getResponse()
details['favmeal'] = "My favorite meal is " + response
print(response)


tts.say("what is your favorite drink")
response = getResponse()
details['favdrink'] = "My favorite drink is " + response
print(response)


tts.say("Good choice. what about your favorite song")
response = getResponse()
details['favsong'] = "My favorite song is " + response
print(response)


tts.say("Thanks. I like that. So what is your hobby")
response = getResponse()
details['favhobby'] = "My favorite hobby is " + response
print(response)


tts.say("Tell me about an interesting place you've travelled to")
response = getResponse()
details['favplace'] = "I visited " + response
print(response)


tts.say("Hmm that is really cool. Can you please tell me what are you most passionate about")
response = getResponse()
details['favinterest'] = "I am passionate about " + response
print(response)


# Additional information for personalisation
details['location'] = "I am in my house."

print("final details: ", details)
details = json.dumps(details, indent = 3)
with open("details.json", "w") as f:
    f.write(details)


print("User created!")
tts.say("I have now registered you on my system, thank you")
