#!/usr/bin/env python
from __future__ import absolute_import, print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from gpiozero import MotionSensor
import time
import json
import os


# update global state to desired state sent from shadow
def update_state(payload, responseStatus, token):
    # process payload
    payload = json.loads(payload)

    global state
    state = payload['state']['monitor']
    print('Updated listening state to ' + state)

    # let shadow know you've updated
    delta = json.dumps(payload['state'])
    newPayload = '{"state":{"reported":' + delta + '}}'
    myDeviceShadow.shadowUpdate(newPayload, my_shadow_update_callback, 5)


# Configure shadow client with localy stored creds, associate to thing
SHADOW_CLIENT = "myShadowClient"
HOST_NAME = "a1r58egst5kiuu-ats.iot.us-west-2.amazonaws.com"
ROOT_CA = "root-CA.crt"
PRIVATE_KEY = "056e1e33f1-private.pem.key"
CERT_FILE = "056e1e33f1-certificate.pem.crt"
SHADOW_HANDLER = "Pi"


# Callback function for AWS IOT
def my_shadow_update_callback(payload, responseStatus, token):
    print('Loading function')
    print('UPDATE: $aws/things/' + SHADOW_HANDLER + '/shadow/update/#')
    print("payload = " + payload)
    print("responseStatus = " + responseStatus)
    print("token = " + token)


# Create, configure, and connect a shadow client.
print('Starting up AWS IOT shadow...')
myShadowClient = AWSIoTMQTTShadowClient(SHADOW_CLIENT)
myShadowClient.configureEndpoint(HOST_NAME, 8883)
myShadowClient.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT_FILE)
myShadowClient.configureConnectDisconnectTimeout(10)
myShadowClient.configureMQTTOperationTimeout(5)
myShadowClient.connect()
# Create a programmatic representation of the shadow.
myDeviceShadow = myShadowClient.createShadowHandlerWithName(SHADOW_HANDLER, True)
print('Connected to AWS IOT with locally loaded shadow!')

# Listen for deltas from AWS IOT shadow in separate thread. Call update_state when triggered.
myDeviceShadow.shadowRegisterDeltaCallback(update_state)

# pickup motion sensor on RaspberryPi
pir = MotionSensor(4)
print('PIR sensor detected, using pin ' + str(pir.pin))

# listen for motion by default
state = "enabled"

while True:
    if state == "enabled":
        print("Switch ON!")
        print('Waiting for motion...')
        pir.wait_for_motion()
        # if switch was disconnected while waiting for motion
        if state == "enabled":
            print('////////////////////////Motion Detected, logging the sucker!////////////////////////')
            os.system("omxplayer -o local airhorn-siren.mp3")
            myDeviceShadow.shadowUpdate('{"state":{"reported":{"motion":"detected"}}}', my_shadow_update_callback, 5)
        else:
            print("switch turned of before ")
    else:
        print('Switch OFF :(')

    time.sleep(1)
