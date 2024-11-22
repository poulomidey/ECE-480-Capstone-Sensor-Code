# A program to use HC-SR04 Ultrasonic Sensor.
# Determine the distance to a target in cm - used for experimentation
# to determine performance of sensor
# Measure a specific number of distances - user input
# Write data to a file: data.txt

# Lori Pfahler
# December 2022

# load modules
import RPi.GPIO as GPIO
import time
import threading
import os
import settings #global var file
# from sensor import Sensor
# board numbering system to use

class Ultrasonic():
    def __init__(self, lock):
        # super().__init__()
        #GPIO.setmode(GPIO.BCM)
#         GPIO.setmode(GPIO.BOARD)

        # variable to hold a short delay time
        self.delayTime = 0.2

        # setup trigger and echo pins
        self.trigPin = 7
        self.echoPin = 11
#         GPIO.setup(self.trigPin, GPIO.OUT)
#         GPIO.setup(self.echoPin, GPIO.IN)

        self.is_running = False
        self.my_thread = None

#         file_path = 'data/' + time.strftime("%Y%m%d-%H%M") + '/' #change
#         print(file_path)
#         os.makedirs(file_path, exist_ok=True)

#         
        self.file = None

        # # ask user for number of replicate distances and short description of run
        # numReadings = int(input('Enter number of distance readings desired: '))
        # runText = input('Enter Short Description of Run Parameters: ')
        # # print to file
        # print('n =', numReadings, runText, file = open('distances.txt', 'a'))
        self.lock = lock
    
    def _create_file(self, file_path):
        self.file = open(file_path + 'ultrasonic_distance.txt', 'a')

    def _collect_data(self):

        # start loop to measure distances
#         print('in dist func')
#         try:
        # t = threading.current_thread()
        while self.is_running:
            GPIO.setup(self.trigPin, GPIO.OUT)
            GPIO.setup(self.echoPin, GPIO.IN)
#                 print('in while loop')
            # start the pulse to get the sensor to send the ping
            # set trigger pin low for 2 micro seconds
            GPIO.output(self.trigPin, 0)
            time.sleep(2E-6)
            # set trigger pin high for 10 micro seconds
            GPIO.output(self.trigPin, 1)
            time.sleep(10E-6)
            # go back to zero - communication compete to send ping
            GPIO.output(self.trigPin, 0)
            # now need to wait till echo pin goes high to start the timer
            # this means the ping has been sent
            while GPIO.input(self.echoPin) == 0:
                pass
            # start the time - use system time
            echoStartTime = time.time()
            # wait for echo pin to go down to zero
            while GPIO.input(self.echoPin) == 1:
                pass
            echoStopTime = time.time()
            # calculate ping travel time
            pingTravelTime = echoStopTime - echoStartTime
            # Use the time to calculate the distance to the target.
            # speed of sound at 72 deg F is 344.44 m/s
            # from weather.gov/epz/wxcalc_speedofsound.
            # equations used by calculator at website above.
            # speed of sound = 643.855*((temp_in_kelvin/273.15)^0.5)
            # temp_in_kelvin = ((5/9)*(temp_in_F - 273.15)) + 32
            #
            # divide in half since the time of travel is out and back
            dist_cm = (pingTravelTime*34444)/2
            # print data to shell and to the file
            print(round(dist_cm, 3))
            print(round(dist_cm, 3), file = self.file)
            
            # with self.lock:
            self.lock.acquire()
            settings.curr_dist = dist_cm
            print(f'us: {settings.curr_dist}')
#             time.sleep(.5)
            self.lock.release()
                
            # sleep to slow things down
            time.sleep(self.delayTime)
#         finally:
#         print("Here")
        self.file.close() #try
        GPIO.cleanup()


    def start_data_collection(self):
#         print('in start data collection')
        self.my_thread = threading.Thread(target=self._collect_data)
#         self.my_thread.do_run = True
        self.is_running = True
        # self.distance()
        self.my_thread.start()


    def stop_data_collection(self):
        # self.is_running = False
        if self.my_thread is not None:
#             self.my_thread.do_run = False
            self.is_running = False
            self.my_thread.join()
        

# testing wo button
if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    us = Ultrasonic()
    
    us.start_data_collection()
#     us.distance()
    time.sleep(3)
#     # us.is_running = False
    us.stop_data_collection()
#     GPIO.cleanup()