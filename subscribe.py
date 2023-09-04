# MQTT subscribe script

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
    if command == "Hello, MQTT!":
        response = "Got your msg!"
    else:
        # Process the request message
        response = "Replying to your message!"
    # Publish the response message with the same correlation ID
    client.publish("response/topic", response)
    print("state: ", kettleStatus)
# Create MQTT client instance
client = mqtt.Client()

# Assign callback functions to respective events
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect("localhost", 1883, 60)

# Start the network loop
client.loop_forever()
