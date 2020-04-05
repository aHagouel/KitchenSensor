#!/usr/bin/env python
from __future__ import absolute_import, print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from gpiozero import MotionSensor
import gpio
from datetime import datetime
import time
import logging
import json

# A random programmatic shadow client ID.
SHADOW_CLIENT = "myShadowClient"

# The unique hostname that &IoT; generated for
# this device.
HOST_NAME = "a1r58egst5kiuu-ats.iot.us-west-2.amazonaws.com"

# The relative path to the correct root CA file for &IoT;,
# which you have already saved onto this device.
ROOT_CA = "root-CA.crt"

# The relative path to your private key file that
# &IoT; generated for this device, which you
# have already saved onto this device.
PRIVATE_KEY = "056e1e33f1-private.pem.key"
# The relative path to your certificate file that 
# &IoT; generated for this device, which you 
# have already saved onto this device.
CERT_FILE = "056e1e33f1-certificate.pem.crt"

# A programmatic shadow handler name prefix.
SHADOW_HANDLER = "Pi"

def myShadowUpdateCallback(payload, responseStatus, token):
 print('Loading function')
 print('UPDATE: $aws/things/' + SHADOW_HANDLER +
    '/shadow/update/#')
 print("payload = " + payload)
 print("responseStatus = " + responseStatus)
 print("token = " + token)

# Create, configure, and connect a shadow client.
myShadowClient = AWSIoTMQTTShadowClient(SHADOW_CLIENT)
myShadowClient.configureEndpoint(HOST_NAME, 8883)
myShadowClient.configureCredentials(ROOT_CA, PRIVATE_KEY,
  CERT_FILE)
myShadowClient.configureConnectDisconnectTimeout(10)
myShadowClient.configureMQTTOperationTimeout(5)
myShadowClient.connect()
# Create a programmatic representation of the shadow.
myDeviceShadow = myShadowClient.createShadowHandlerWithName(
  SHADOW_HANDLER, True)

# pickup sensor on RaspberryPi
def activateGPIO():
    pir = MotionSensor(4)
    print('PIR sensor using ' + str(pir.pin))
    switch_pin = 27
    return(switch_pin)

if __name__== "__main__":
    print('Starting up...')
    switch_pin = activateGPIO()
    while True:
        if(gpio.input(switch_pin) == 1):
            print("Switch ON!")
            print('Waiting for motion...')
            pir.wait_for_motion()
                #if switch was disconnected while waiting for motion
                if(gpio.input(switch_pin) == 1):
			                 print('Motion Detected, logging the sucker!')
                    myDeviceShadow.shadowUpdate('{"state":{"reported":{"motion":"detected"}}}',myShadowUpdateCallback,5)
        else:
            print('Switch off :(')
        print("Sleeping for 60 seconds")
        time.sleep(60)
