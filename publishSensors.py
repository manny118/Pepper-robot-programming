# ROS script for publishing sensor data

import smbclient
import rospy
from std_msgs.msg import String
import multiprocessing as mp

# connect to the home assistant instance
smbclient.ClientConfig(username = 'homeassistant', password = 'HTH@IBST')


# track the current temperature
def checkTempStatus():
    rospy.init_node("temp_status_pub_node")
    pub = rospy.Publisher("temp_status", String, queue_size = 15) # topic name
    print("\nfrom pub temp")
    i = 0
    rate = rospy.Rate(1) # 1 msg a second

    while not rospy.is_shutdown():
        x = smbclient.open_file("192.168.1.135/config/logs/sensor.txt")
        with x as G:
            num = (G.read())
            print(num[-4:])
            currentTemp = num[-4:]
        print("str(currentTemp): ", str(currentTemp))
        pub.publish(str(currentTemp))
        print("i: ", i)
        i += 1
        rate.sleep()


# track the current temperature
def cabinetStatus():
    rospy.init_node("cabinet_status_pub_node")
    pub = rospy.Publisher("cabinet_status", String, queue_size = 15) # topic name
    print("\nfrom pub cab")
    i = 0
    rate = rospy.Rate(1) # 1 msg a second

    while not rospy.is_shutdown():
        x = smbclient.open_file("192.168.1.135/config/logs/sensor3.txt")
        with x as G:
            num = (G.read())
            print(num[-4:])
            cabinetState = num[-4:]
        print("str(cabinetState): ", str(cabinetState))
        pub.publish(str(cabinetState))
        print("i: ", i)
        i += 1
        rate.sleep()


# track the fridge status
def checkFridgeStatus():
    rospy.init_node("fridge_status_pub_node")
    pub = rospy.Publisher("fridge_status", String, queue_size = 15) # topic name
    print("\nfrom pub fridge")
    i = 0
    rate = rospy.Rate(1) # 1 msg a second

    while not rospy.is_shutdown():
        x = smbclient.open_file("192.168.1.135/config/logs/sensor2.txt")
        with x as G:
            num = (G.read())
            print(num[-4:])
            fridgeStatus = num[-4:]
        print("str(fridgeStatus): ", str(fridgeStatus))
        pub.publish(str(fridgeStatus))
        print("i: ", i)
        i += 1
        rate.sleep()


if __name__ == '__main__':
    try:
        
        p1 = mp.Process(target = checkFridgeStatus)
        p2 = mp.Process(target = cabinetStatus)
        p3 = mp.Process(target = checkTempStatus)

        print("\n\nprocesses called")
        p1.start()
        p2.start()
        p3.start()
        print("\n\nprocesses started")

        p1.join()
        p2.join()
        p3.join()
        print("\n\nprocesses joined")

    except rospy.ROSInterruptException:
        pass
