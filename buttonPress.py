import RPi.GPIO as GPIO
import time
from ultradistant import Ultrasonic
from gps import GPS
from thermal import ThermalCamera
from camera import Camera
import threading
import settings #global var file
import os


#button setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

previousSetting=False
currSetting = False
state = False

gps_lock = threading.Lock()
us_lock = threading.Lock()


# initialize sensors
us = Ultrasonic(us_lock) # ultrasonic sensor
# gps = GPS(file_path, gps_lock) # GPS
# tc = ThermalCamera(file_path, us_lock, gps_lock)
# cm = Camera(file_path)
# sensors = [us, gps, tc]
# sensors = [us]

settings.init() #initialize global vars

while True:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    if GPIO.input(12)==GPIO.HIGH:
        if (previousSetting==False):
                
            currSetting = True
            previousSetting = currSetting

            state = not state
#             print(state)

            if state == True:
                # create folder and paths
                #create folder
                file_path = 'data/' + time.strftime("%Y%m%d-%H%M%S") + '/' #change
                print(file_path)
                os.makedirs(file_path, exist_ok=True)
                
                us._create_file(file_path)
                
                
                # call sensors
                us.start_data_collection()
#                 cm.start_data_collection()
#                 tc.start_data_collection()
                print('start')
#                 gps.start_data_collection()
#                 for sensor in sensors:
#                     sensor.start_data_collection()
            else:
                # stop sensors
                us.stop_data_collection()
#                 cm.stop_data_collection()
#                 tc.stop_data_collection() #change
#                 gps.stop_data_collection()
#                 for sensor in sensors:
#                     sensor.stop_data_collection()
                print('stop')

            # TODO: Make it so each button press creates a new subfolder within the data folder (ideally timestamped),
            # which will hold all the data from all the sensors for that button press

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)        
    if GPIO.input(12)==GPIO.LOW:
        if (previousSetting==True):
            currSetting = False
            previousSetting = False
            

            
            

       
        
