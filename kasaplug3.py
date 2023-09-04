# turns plug on and tracks its status with a timer

import asyncio
import kasa
import time
import os
import kasa as plug

poweLevel = []

# main function
async def main():
    found_devices = await (kasa.Discover.discover())
    ip_address = (list(found_devices.keys()))[0]
    plug = kasa.SmartPlug(ip_address)
    # asyncio.run(plug.update())
    await plug.update()
    plug = kasa.SmartPlug(ip_address) #'192.168.1.133'
    await plug.update()
    currPower = (plug.emeter_realtime)['power']
    print("here")

    await plug.turn_on() # turn on the kettle

    # monitor initial state when it is off
    while True:
        await plug.update()
        currPower = (plug.emeter_realtime)['power']
        if currPower == 0:
            continue
        break

    setTime = 0
    if os.path.exists("plug2.txt"):
        with open("plug2.txt", "r") as file:
            setTime = int(file.read())

    startTime = time.time()
    endTime = time.time()

    # monitor state for a set time
    while (endTime - startTime) < setTime:
        await plug.update()
        currPower = (plug.emeter_realtime)['power']
        print("currPower: ", currPower)
        await asyncio.sleep(0.5)
        endTime = time.time()

        # check if kettle fully boils before set time
        if currPower == 0:
            break

    await plug.turn_off()

    print("The kettle is boiled")
    logFile = open("plug.txt", "w")
    logFile.write("Boiled")


if __name__ == "__main__":
    asyncio.run(main()) #checks for current status

# await plug.turn_off()
