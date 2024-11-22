import picamera
# from sensor import Sensor
import os
import threading
import time
import RPi.GPIO as GPIO

class Camera():
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)

        self.is_running = False
        self.my_thread = None
        
        # self.file = 'data/camera.h264'
#         file_path = 'data/' + time.strftime("%Y%m%d-%H%M") + '/'
#         os.makedirs(file_path, exist_ok=True)
        
        self.file = None
        # self.file = open(self.file, 'a')
   
    def _create_file(self, file_path):
        file_path += 'camera_data.h264'
        self.file = file_path

    def _collect_data(self):
        self.camera.start_recording(self.file)
#         while self.is_running:
#             pass
#         self.camera.stop_recording()
#         self.file.close()

    def start_data_collection(self):
        self.is_running = True
        self.my_thread = threading.Thread(target=self._collect_data)
        self.my_thread.start()
    
    def stop_data_collection(self):
        if self.my_thread is not None:
            self.is_running = False
            self.camera.stop_recording()
            self.my_thread.join()
            
            
# testing wo button
if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    cm = Camera()
    
    cm.start_data_collection()
#     us.distance()
    time.sleep(3)
#     # us.is_running = False
    cm.stop_data_collection()
    print(done)
#     GPIO.cleanup()