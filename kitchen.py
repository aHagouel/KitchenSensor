#!/usr/bin/env python
from __future__ import absolute_import, print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from gpiozero import MotionSensor
import time
import json
import os
import signal
import sys


# catch shutdowns and update AWS shadow that we're offline
def handler(signum, frame):
    #Update device state to offline
    myDeviceShadow.shadowUpdate('{"state":{"reported":{"status":"offline"}}}', my_shadow_update_callback, 5)
    sys.exit(0)


# register terminate signals that may come in if program is asked to shut down
# don't register the child process signal -- our program runs this :) 
for sig in (signal.Signals):
    try:
        if(sig != 17):
                signal.signal(sig, handler)
    except OSError:
        print('Skipping', sig)
        
        
# update global state to desired state sent from shadow
def update_state(payload, responseStatus, token):
    # process payload
    payload = json.loads(payload)

    # update state
    global state
    state = payload['state']['monitor']

    # let shadow know you've updated
    delta = json.dumps(payload['state'])
    newPayload = '{"state":{"reported":' + delta + '}}'
    myDeviceShadow.shadowUpdate(newPayload, my_shadow_update_callback, 5)


# Callback function for AWS IOT
def my_shadow_update_callback(payload, responseStatus, token):
    print('Loading function')
    print('UPDATE: $aws/things/' + SHADOW_HANDLER + '/shadow/update/#')
    print("payload = " + payload)
    print("responseStatus = " + responseStatus)
    print("token = " + token)


# Create, configure, and connect a shadow client with locally stored creds, associate to thing
SHADOW_CLIENT = "myShadowClient"
HOST_NAME = "a1r58egst5kiuu-ats.iot.us-west-2.amazonaws.com"
ROOT_CA = "/home/pi/Development/KitchenSensor/root-CA.crt"
PRIVATE_KEY = "/home/pi/Development/KitchenSensor/056e1e33f1-private.pem.key"
CERT_FILE = "/home/pi/Development/KitchenSensor/056e1e33f1-certificate.pem.crt"
SHADOW_HANDLER = "Pi"

myShadowClient = AWSIoTMQTTShadowClient(SHADOW_CLIENT)
myShadowClient.configureEndpoint(HOST_NAME, 8883)
myShadowClient.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT_FILE)
myShadowClient.configureConnectDisconnectTimeout(10)
myShadowClient.configureMQTTOperationTimeout(5)
myShadowClient.connect()

# Create a programmatic representation of the shadow & update state to online.
myDeviceShadow = myShadowClient.createShadowHandlerWithName(SHADOW_HANDLER, True)
myDeviceShadow.shadowUpdate('{"state":{"reported":{"status":"online", "monitor":"enabled"}}}', my_shadow_update_callback, 5)

# pickup motion sensor on RaspberryPi, give it 15 seconds to get used to the infrared :)
pir = MotionSensor(4)
time.sleep(5)

# listen for motion by default, adjustible by publishing to MTTQ subscription
state = "enabled"

# Listen for deltas from AWS IOT shadow in separate thread. Call update_state when triggered.
myDeviceShadow.shadowRegisterDeltaCallback(update_state)

#Loop forever, reporting on motion if state is enabled
while True:
    
    if state == "enabled":
        pir.wait_for_motion()
        # if switch was flipped while waiting for motion
        if state == "enabled":
            os.system("omxplayer -o local /home/pi/Development/KitchenSensor/maui-no.mp3")
            myDeviceShadow.shadowUpdate('{"state":{"reported":{"motion":"detected"}}}', my_shadow_update_callback, 5)
    
    time.sleep(3)
