# vision algorithm for detecting humans

from naoqi import ALProxy
import qi
import paramiko
import time
import random
from PIL import Image
import numpy as np
import cv2


class Recognition:
    def __init__(self, ip_address, port = 9559):
        self.session = qi.Session()
        self.session.connect("tcp://{0}:{1}".format(ip_address, port))
        self.ip_address = ip_address
        self.port = port
        connection_url = "tcp://" + ip_address + ":" + str(port)
        ssh = paramiko.SSHClient()

        self.memoryProxy = self.session.service("ALMemory")
        self.face_detection = self.session.service("ALFaceDetection")
        self.awareness_service = self.session.service("ALBasicAwareness")
        self.tts = self.session.service("ALAnimatedSpeech")
        self.video = self.session.service("ALVideoDevice")

        # Connect to the event callback.
        try:
            self.subscriber = self.memoryProxy.subscriber("FaceDetected")
        except:
            self.subscriber = None
            

    # Performs face detection
    def detectFace(self, getName = False):
        period = 500
        face_detected = False
        name = ""
        self.face_detection.subscribe("Test_Face", period, 0.0)
        # ALMemory variable where the ALFacedetection modules
        # outputs its results
        memValue = "FaceDetected"
        attempts = 0

        # A simple loop that reads the memValue and checks whether faces are detected.
        for i in range(0, 150):
          time.sleep(0.15)
          val = self.memoryProxy.getData(memValue)

          if getName == True:
              # Check whether we got a valid output.
              if(val and isinstance(val, list) and len(val) >= 2):
                face_detected = True
                print("face detected!")
                timeStamp = val[0]
                faceInfoArray = val[1]

                faceExtraInfo1 = faceInfoArray[1]
                print("faceExtraInfo1: ", faceExtraInfo1)
                faceExtraInfo1 = faceInfoArray[1]
                print("faceExtraInfo1: ", faceExtraInfo1)
                try:
                    name = faceExtraInfo1[1][0]
                    print("name: ", name)
                except:
                    print("Name not found")
                    attempts += 1

                    if attempts == 25:
                        break
                    else:
                        continue
                break
        return face_detected, name


    # Learns a face within its view with an associated name
    def learn_face(self, name):
        self.awareness_service.resumeAwareness()
        face_detected = self.detectFace()
        self.tts.say("face detected ...")
        if name is not "":
            return self.face_detection.learnFace(name)
            

    # Recollects the name of the person
    def recognize_person(self):
        self.awareness_service.resumeAwareness()
        face_detected, name = self.detectFace(True)

        if name is not "":
            return name
        else:
            return ""


    # Retrieves the list of names in the database
    def getLearnedFaces(self):
        return self.face_detection.getLearnedFacesList()


    # performs human detection using HOG descriptor    
    def detectHuman(self):
        detectedHuman = False

        while detectedHuman == False:
            cameraId = 1 # 1 for head camera
            strName = "capture2DImage_{}".format(random.randint(1, 10000000000))

            clientRGB = self.video.subscribeCamera(strName, cameraId, 2, 11, 10)
            imageRGB = self.video.getImageRemote(clientRGB)
            array = imageRGB[6]
            image_string = str(bytearray(array))

            # Create a PIL Image from our pixel array.
            im = Image.frombytes("RGB", (imageRGB[0], imageRGB[1]), image_string)
            im = np.array(im)

            hogDescriptor = cv2.HOGDescriptor()
            out = hogDescriptor.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

            boxes, weights = hogDescriptor.detectMultiScale(im, winStride=(8, 8))
            print("boxes size: ", np.size(boxes))

            if np.size(boxes) != 0:
                self.tts.say("hey there")
                #stop moving once detected
                detectedHuman = True
        return detectedHuman


if __name__ == "__main__":
    rec = Recognition(robotIP, PORT)
    time.sleep(6)
    recUser = rec.detectHuman()
    recFace = rec.recognize_person()
    print("recFace: ", recFace)
