#''
#GPS Interfacing with Raspberry Pi using Pyhton
#http://www.electronicwings.com
#'''
import serial               #import serial pacakge
import time
import sys                  #import system package
import threading
# from sensor import Sensor
import os

class GPS():
    def __init__(self, lock):
        self.gpgga_info = "$GPGGA,"
        self.ser = serial.Serial ("/dev/ttyS0")              #Open port with baud rate
        self.GPGGA_buffer = 0
        self.NMEA_buff = 0
        self.lat_in_degrees = 0
        self.long_in_degrees = 0

        self.is_running = False
        self.my_thread = None
        # self.file = open('data/locations1108.txt', 'a')
        file_path = 'data/' + time.strftime("%Y%m%d-%H%M") + '/' #change
        os.makedirs(file_path, exist_ok=True)
        self.file = open(file_path + 'gps_data.txt', 'a')

        self.lock = lock

    def _GPS_Info(self):
        # global NMEA_buff
        # global lat_in_degrees
        # global long_in_degrees
        nmea_time = []
        nmea_latitude = []
        nmea_longitude = []
        nmea_time = self.NMEA_buff[0]                    #extract time from GPGGA string
        nmea_latitude = self.NMEA_buff[1]                #extract latitude from GPGGA string
        nmea_longitude = self.NMEA_buff[3]               #extract longitude from GPGGA string
        time=float(nmea_time)-30000  # time was exactly three hours off
        print("NMEA Time: ", time,'\n')
        print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
        print("NMEA Time: ", time, file = self.file)
        
        if nmea_latitude != '':
            lat = float(nmea_latitude)                  #convert string into float for calculation
            longi = float(nmea_longitude)               #convertr string into float for calculation
        else:
            raise Exception('no gps signal')
        
        self.lat_in_degrees = self._convert_to_degrees(lat)    #get latitude in degree decimal format
        self.long_in_degrees = self._convert_to_degrees(longi) #get longitude in degree decimal format
        
    #convert raw NMEA string into degree decimal format   
    def _convert_to_degrees(self,raw_value):
        decimal_value = raw_value/100.00
        degrees = int(decimal_value)
        mm_mmmm = (decimal_value - int(decimal_value))/0.6
        position = degrees + mm_mmmm
        position = "%.4f" %(position)
        return position
    
    def _collect_data(self):
        global curr_gps
        while self.is_running:
            received_data = (str)(self.ser.readline())                   #read NMEA string received
            GPGGA_data_available = received_data.find(self.gpgga_info)   #check for NMEA GPGGA string                 
            if (GPGGA_data_available>0):
                self.GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
                self.NMEA_buff = (self.GPGGA_buffer.split(','))               #store comma separated data in buffer
                self._GPS_Info()                                          #get time, latitude, longitude
    
                print("lat in degrees:", self.lat_in_degrees," long in degree: ", self.long_in_degrees, '\n')
                # time is off by three hours
                #nmea_time_new=nmea_time-30000
                print("Latitude: ", self.lat_in_degrees," Longitude: ", self.long_in_degrees, file = self.file)

                with self.lock:
                    curr_gps = f"Latitude: {self.lat_in_degrees}, Longitude: {self.long_in_degrees}"
        #webbrowser.open(map_link)        #open current position information in google map
        self.file.close()
        sys.exit(0)
    
    def start_data_collection(self):
        self.is_running = True
        self.my_thread = threading.Thread(target=self._collect_data)
        self.my_thread.start()
    
    def stop_data_collection(self):
        if self.my_thread is not None:
            self.is_running = False
            self.my_thread.join()

# testing wo button
if __name__ == "__main__":
    gps = GPS()
    gps.start_data_collection()
    time.sleep(20)
    gps.stop_data_collection()