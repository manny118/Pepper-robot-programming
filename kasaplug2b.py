# turns plug on and tracks its status
# same version as kasaplug2b but with MQTT

import asyncio
import kasa
import time
import kasa as plug
import paho.mqtt.client as mqtt


global kettleStatus
kettleStatus = "OFF"


# Define callback function for successful connection
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("request/topic")

# Define callback function for received request messages
def on_message(client, userdata, msg):
    print("Request received: " + msg.payload.decode())
    command = msg.payload.decode()

    if command == "Toggle kettle":
        asyncio.run(main()) #checks for current status

    response = "Boiled"

    # Publish the response message with the same correlation ID
    client.publish("response/topic", response)


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
            print("The kettle is boiled")
            continue
        break

    # monitor later state when it is on
    while currPower > 0:
        await plug.update()
        currPower = (plug.emeter_realtime)['power']
        print("currPower: ", currPower)
        await asyncio.sleep(1)

    time.sleep(1)
    if currPower == 0:
        print("The kettle is boiled")
        kettleStatus = "Boiled"
        await plug.turn_off()
    kettleStatus = "Boiled"
    return kettleStatus


if __name__ == "__main__":
    # Create MQTT client instance
    client = mqtt.Client()

    # Assign callback functions to respective events
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to MQTT broker
    client.connect("localhost", 1883, 60)

    print("\n kettleStatus: ", kettleStatus)
    # Start the network loop
    client.loop_forever()
    print("kettleStatus after: ", kettleStatus)
