# -*- encoding: UTF-8 -*-
# Script for detecting landmarks
# Adapted from Aldabaran's example use of the fucntion 
from naoqi import ALProxy

import math
import qi
import argparse
import sys
import almath
import socket
import paramiko
from scp import SCPClient


class LandmarkFinder:
    def __init__(self, ip_address, port):
        self.session = qi.Session()
        self.session.connect("tcp://" + ip_address + ":" + str(port))

        self.ip_address = ip_address
        self.port = port

        ssh = paramiko.client.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=self.ip_address, username = "nao", password = "pepper")
        self.scp = SCPClient(ssh.get_transport())

        self.face_service =  self.session.service("ALFaceDetection")
        self.tts = self.session.service("ALTextToSpeech")
        self.memoryProxy = self.session.service("ALMemory")
        self.landmarkProxy = self.session.service("ALLandMarkDetection")
        self.motionProxy =  self.session.service("ALMotion")
        self.trackerProxy =  self.session.service("ALTracker")


    # move head around to find landmarks
    def moveHead(self, amntX, amntY, motionProxy):
        headJoints = ["HeadPitch", "HeadYaw"]
        headSpeed = 0.1
        headPos = [float(amntY),float(amntX)]
        self.motionProxy.angleInterpolationWithSpeed(headJoints, headPos, headSpeed)


    # function for pointing at a landmark
    def pointAtLandmark(self, item = "fridge"):
        period = 500

        # landmark size in meters.
        landmarkTheoreticalSize = 0.06 # in meters
        # current camera ("CameraTop" or "CameraBottom")
        currentCamera = "CameraTop"

        # LandmarkDetected event from ALLandMarkDetection proxy
        self.landmarkProxy.subscribe("landmarkTest", period, 0.0)
        self.face_service.enableTracking(False) # disable face tracking

        # Wait for a landmark to be detected
        counter = 0
        markData = self.memoryProxy.getData("LandmarkDetected")

        while (len(markData) == 0):
            markData = self.memoryProxy.getData("LandmarkDetected")

            # rotate head in various angles to spot landmark
            if counter == 0 :
                self.moveHead(0, 0, self.motionProxy)
            elif counter == 1:
                self.moveHead(-0.3, 0, self.motionProxy)
            elif counter == 2:
                self.moveHead(0.4, 0, self.motionProxy)
            elif counter == 3:
                self.moveHead(0.8, 0.1, self.motionProxy)
            elif counter == 4:
                self.moveHead(0.1, 0.8, self.motionProxy)
            elif counter == 5:
                self.moveHead(0.5, 0.1, self.motionProxy)
            elif counter == 6:
                self.moveHead(0.8, 0.5, self.motionProxy)
            elif counter == 7:
                self.moveHead(0.5, 0.1, self.motionProxy)
            elif counter == 8:
                self.moveHead(0.7, 0.5, self.motionProxy)
            elif counter == 9:
                self.moveHead(0.4, 0.8, self.motionProxy)
            elif counter == 10:
                self.moveHead(1, 0.8, self.motionProxy)
            elif counter == 11:
                self.moveHead(1, 0.5, self.motionProxy)
            elif counter == 12:
                self.moveHead(1, 0.7, self.motionProxy)
            elif counter == 13:
                self.moveHead(1, 0.6, self.motionProxy)
            elif counter == 14:
                self.moveHead(0.9, 0.6, self.motionProxy)
            elif counter == 15:
                self.moveHead(0.95, 0.6, self.motionProxy)
            elif counter == 16:
                self.moveHead(0.85, 0.6, self.motionProxy)
            elif counter == 17:
                self.moveHead(0.8, 0.6, self.motionProxy)
            elif counter == 18:
                self.moveHead(0.8, 1, self.motionProxy)
            elif counter == 19:
                self.moveHead(0.8, 0.9, self.motionProxy)
            elif counter == 20:
                self.moveHead(0.84, 0.9, self.motionProxy)
            elif counter == 21:
                self.moveHead(0.81, 0.61, self.motionProxy)
            elif counter == 22:
                self.moveHead(0.9, 0.3, self.motionProxy)
            elif counter == 23:
                self.moveHead(0.9, 0.61, self.motionProxy)
            elif counter == 24:
                self.moveHead(0.9, 0.9, self.motionProxy)
            elif counter == 25: 
                self.moveHead(0.9, 0.61, self.motionProxy)
            elif counter == 26:
                self.moveHead(0.9, 0.9, self.motionProxy)
            elif counter == 27:
                self.moveHead(0.9, 0.61, self.motionProxy)
            elif counter == 28:
                self.moveHead(0.92, 0.65, self.motionProxy)
            elif counter == 29:
                self.moveHead(0.94, 0.67, self.motionProxy)
            elif counter == 30: 
                self.moveHead(0.96, 0.69, self.motionProxy)
            elif counter == 31:
                self.moveHead(0.98, 0.74, self.motionProxy)
            elif counter == 32:
                self.moveHead(0.87, 0.78, self.motionProxy)
            elif counter == 33:
                self.moveHead(0.85, 0.84, self.motionProxy)
            elif counter == 34:
                self.moveHead(0.85, 0.61, self.motionProxy)
            elif counter == 35:
                self.moveHead(0.80, 0.61, self.motionProxy)
            elif counter == 36:
                self.moveHead(0.75, 0.61, self.motionProxy)
            elif counter == 37:
                self.moveHead(0.80, 0.71, self.motionProxy)
            elif counter == 38:
                break
            counter += 1
        
        print("landmark detected, counter value: ", counter)

        try:
            # Retrieve landmark center position in radians
            wzCamera = markData[1][0][0][1]
            wyCamera = markData[1][0][0][2]

            # Retrieve landmark angular size in radians.
            angularSize = markData[1][0][0][3]

            # Compute distance to landmark
            distanceFromCameraToLandmark = landmarkTheoreticalSize / ( 2 * math.tan( angularSize / 2))

            # Get current camera position in NAO space
            transform = self.motionProxy.getTransform(currentCamera, 2, True)
            transformList = almath.vectorFloat(transform)
            robotToCamera = almath.Transform(transformList)

            # Compute the rotation to point towards the landmark
            cameraToLandmarkRotationTransform = almath.Transform_from3DRotation(0, wyCamera, wzCamera)
            print("cameraToLandmark: ", cameraToLandmarkRotationTransform)

            # Compute the translation to reach the landmark
            cameraToLandmarkTranslationTransform = almath.Transform(distanceFromCameraToLandmark, 0, 0)
            print("cameraToLandmarkDist: ", cameraToLandmarkTranslationTransform)

            # Combine all transformations to get the landmark position in NAO space.
            robotToLandmark = robotToCamera * cameraToLandmarkRotationTransform *cameraToLandmarkTranslationTransform

            print "x " + str(robotToLandmark.r1_c4) + " (in meters)"
            print "y " + str(robotToLandmark.r2_c4) + " (in meters)"
            print "z " + str(robotToLandmark.r3_c4) + " (in meters)"

            self.landmarkProxy.unsubscribe("landmarkTest")

            x_cord = robotToLandmark.r1_c4
            y_cord = robotToLandmark.r2_c4
            z_cord = robotToLandmark.r3_c4
            point = [x_cord, y_cord, z_cord]

            # look at object and point at it
            out = "That is the " + item
            self.tts.say(out)

            self.trackerProxy.pointAt('LArm', point, 2, 0.6)
            self.trackerProxy.lookAt(point, 1, 0.6, True)
        except:
            print("error finding item")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.91",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
