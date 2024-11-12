import picamera
from sensor import Sensor

class Camera(Sensor):
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)

        self.file = 'data/camera.h264'
   
    def _collect_data(self):
        while self.is_running:
            self.camera.start_recording(self.file)
        self.camera.stop_recording()
        self.file.close()