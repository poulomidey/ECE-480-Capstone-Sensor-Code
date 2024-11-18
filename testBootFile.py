i=0
file=open("/home/pi/Documents/testFile.txt","a")
while(i<1000):
    file.write("Hi")
    i+=1
file.close()
