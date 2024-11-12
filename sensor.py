import threading
import os
import time

class Sensor:
    def __init__(self):
        self.is_running = False
        self.my_thread = None
        self.file = 'data/' + time.strftime("%Y%m%d-%H%M") + '/'
        os.makedirs(self.file_path, exist_ok=True)
        #TODO: do I need to create this folder if it doesn't exist?
        #TODO: make this self.file = data/curr day hour min folder
        # in the child classes, make them self.file += filename

    def _collect_data(self):
        pass
    
    def start_data_collection(self):
        self.is_running = True
        self.my_thread = threading.Thread(target=self._collect_data())
        self.my_thread.start()

    def stop_data_collection(self):
        if self.my_thread is not None:
            self.is_running = False
            self.my_thread.join()