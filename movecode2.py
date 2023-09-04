# -*- encoding: UTF-8 -*-
# Python script for navigating within the living studio
import qi
import argparse
import sys
import almath
import socket
import paramiko
from scp import SCPClient
import time

class Localise:
    def __init__(self, ip_address, port):
        self.session = qi.Session()
        self.session.connect("tcp://" + ip_address + ":" + str(port))

        self.ip_address = ip_address
        self.port = port

        ssh = paramiko.client.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=self.ip_address, username="nao", password="pepper")
        self.scp = SCPClient(ssh.get_transport())

        self.motion_service = self.session.service("ALMotion")
        self.motion_service  = self.session.service("ALMotion")
        self.posture_service = self.session.service("ALRobotPosture")
        self.face_service = self.session.service("ALFaceDetection")
        self.localise_service = self.session.service("ALLocalization")
        self.navigation_service = self.session.service("ALNavigation")
        self.face_service.enableTracking(False)


    # directs Pepper to a specified location
    def moveToLocation(self, location):
        # Send robot to Pose Init
        self.posture_service.goToPosture("StandInit", 0.5)
        navigation_service = self.session.service("ALNavigation")
        map_path = "/home/nao/.local/share/Explorer/2023-06-16T101620.002Z.explo"
        self.navigation_service.stopLocalization()
        map = self.navigation_service.loadExploration(map_path)
        guess = [0., 0.]
        navigation_service.startLocalization()

        print ("I start at: " + str(self.navigation_service.getRobotPositionInMap()[0]))
        coord = 0
        startPos = self.navigation_service.getRobotPositionInMap()[0]

        # navigation coordinates
        kitchen = [1.213788390159607, 2.2214889526367188, 1.5952200889587402] #goes to kitchen
        fridge31 = [2.4290403714179993, 0.11208732414245605, 3.907877826690674] # travels to fridge
        greenchair = [-1.2300403714179993, -0.78, 0.43] # cabinet's location

        if location == "fridge":
            print("the location selected is: ", location)
            coord = fridge31

        elif location == "kitchen":
            coord = kitchen
            print("the location selected is: ", location)

        elif location == "greenchair": # medication cabinet
            coord = greenchair
            print("the location selected is: ", location)
        self.navigation_service.navigateToInMap(coord)

        # Check where the robot arrived
        print "I reached: " + str(self.navigation_service.getRobotPositionInMap()[0])

        result = self.navigation_service.getRobotPositionInMap()
        print "Robot Position", result
        # Stop localization
        print "About to go home now.."
        self.navigation_service.stopLocalization()
        return startPos


    # specifies where the robot should return to
    def returnTo(self, location):
        self.posture_service.goToPosture("StandInit", 0.5)
        navigation_service = self.session.service("ALNavigation")
        map_path = "/home/nao/.local/share/Explorer/2023-04-03T145157.758Z.explo"
        map = self.navigation_service.loadExploration(map_path)
        navigation_service.startLocalization()
        print "I start at: " + str(self.navigation_service.getRobotPositionInMap()[0])
        self.navigation_service.navigateToInMap(location)
        self.navigation_service.stopLocalization()


def main(session):
    # Get the services ALMotion & ALRobotPosture.
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type = str, default = "10.167.81.120",
                        help = "Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type = int, default = 9559,
                        help = "Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
