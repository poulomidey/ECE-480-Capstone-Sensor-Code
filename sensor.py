import threading

class Sensor:
    def __init__(self):
        self.is_running = False
        self.my_thread = None
        self.file = None

    def _collect_data(self):
        pass
    
    def start_data_collection(self):
        self.my_thread = threading.Thread(target=self._collect_data())
        self.is_running = True
        self.my_thread.start()

    def stop_data_collection(self):
        if self.my_thread is not None:
            self.is_running = False
            self.my_thread.join()