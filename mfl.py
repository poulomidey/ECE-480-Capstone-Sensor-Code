#Source: hackster.io Mapping Road Conditions
import serial
import time
import threading

class MFL():
    def __init__(self):
        self.ser=serial.Serial('/dev/ttyACM0')

        self.is_running = False
        self.my_thread = None
        self.file = None

    def _create_file(self, file_path):
        self.file = open(file_path + 'MFLreadings.txt','w')


# with open('MFLreadings.txt','w') as log_file:
    def _collect_data(self):
        while self.is_running:
            msg=''
            c=self.ser.read(1).decode('utf-8')
            while c != '\n':
                c=self.ser.read(1).decode('utf-8')
            c=self.ser.read(1).decode('utf-8')
            while c != '\n':
                msg += c
                c=self.ser.read(1).decode('utf-8')
            self.file.write("Time: "+ str(time.gmtime()[1])+"-"+str(time.gmtime()[2])+"-"+str(time.gmtime()[0])+"  "+str(time.gmtime()[3])+":"+str(time.gmtime()[4])+":"+str(time.gmtime()[5])+"\n")
            self.file.write("MFL Reading: " +msg+'\n\n')
            # print(msg)
        self.file.close()

    def start_data_collection(self):
        self.my_thread = threading.Thread(target=self._collect_data)
        self.is_running = True
        self.my_thread.start()
    
    def stop_data_collection(self):
        # self.is_running = False
        if self.my_thread is not None:
#             self.my_thread.do_run = False
            self.is_running = False
            self.my_thread.join()
        
