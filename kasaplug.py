# Monitors when user turns on kettle

import asyncio
import kasa
import time
import kasa as plug

poweLevel = []

# main function
async def main():
    found_devices = await (kasa.Discover.discover())
    ip_address = (list(found_devices.keys()))[0]
    plug = kasa.SmartPlug(ip_address)
    # asyncio.run(plug.update())
    await plug.update()
    plug = kasa.SmartPlug(ip_address)
    await plug.update()
    currPower = (plug.emeter_realtime)['power']
    

    # monitor initial state when it is off
    while True:
        await plug.update()
        currPower = (plug.emeter_realtime)['power']
        if currPower == 0:
            print("The kettle is boiled")
            continue
        break

    logFile = open("plug3.txt", "w")
    logFile.write("Toggled")

    # monitor later state when it is on
    while currPower > 0:
        await plug.update()
        currPower = (plug.emeter_realtime)['power']
        print("currPower: ", currPower)
        await asyncio.sleep(1)

    time.sleep(1)
    if currPower == 0:
        print("The kettle is boiled")
        logFile = open("plug3.txt", "w")
        logFile.write("Boiled")
        await plug.turn_off()

if __name__ == "__main__":
    asyncio.run(main()) # checks for current status
