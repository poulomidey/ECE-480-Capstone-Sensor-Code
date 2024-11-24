#Source: hackster.io Mapping Road Conditions
import serial
import time
ser=serial.Serial('/dev/ttyACM0')
with open('MFLreadings.txt','w') as log_file:
    while True:
        msg=''
        c=ser.read(1).decode('utf-8')
        while c != '\n':
            c=ser.read(1).decode('utf-8')
        c=ser.read(1).decode('utf-8')
        while c != '\n':
            msg += c
            c=ser.read(1).decode('utf-8')
        log_file.write("Time: "+ str(time.gmtime()[1])+"-"+str(time.gmtime()[2])+"-"+str(time.gmtime()[0])+"  "+str(time.gmtime()[3])+":"+str(time.gmtime()[4])+":"+str(time.gmtime()[5])+"\n")
        log_file.write("MFL Reading: " +msg+'\n\n')
        print(msg)
