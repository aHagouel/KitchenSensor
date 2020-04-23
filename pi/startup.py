from threading import Thread
import time
import os  
    
def start_kitchen():
    os.system("sudo python3 /home/pi/Development/KitchenSensor/kitchen.py")

def start_shutdown():
    os.system("sudo python3 /home/pi/Development/KitchenSensor/pi/shutdown.py")

t1 = Thread(target=start_kitchen)
time.sleep(2)
t1.start()

t2 = Thread(target=start_shutdown)
time.sleep(2)
t2.start()
