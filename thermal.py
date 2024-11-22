#!/usr/bin/env python3
'''
Les Wright 21 June 2023
https://youtube.com/leslaboratory
A Python program to read, parse and display thermal data from the Topdon TC001 Thermal camera!
'''

import cv2
import numpy as np
import argparse
import time
import io
import os.path # included to save photos to a different folder for each hour
# from sensor import Sensor
import os
import threading
import settings #global var file

		
#TODO: GET RID OF CODE WHERE IT DISPLAYS AND LAUNCHES WINDOW, JUST KEEP RECORDING
class ThermalCamera():
	def __init__(self, file_path, us_lock, gps_lock):
# 		dev = 1 # removing argument "--device x" which allows to specify device, don't move the thermal camera location!
		
		#init video
# 		self.cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
# 
# 		self.cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)

		#256x192 General settings
		self.width = 256 #Sensor width
		height = 192 #sensor height
		self.scale = 3 #scale multiplier
		self.newWidth = self.width*self.scale 
		self.newHeight = height*self.scale
		self.alpha = 1.0 # Contrast control (1.0-3.0)
		self.colormap = 0
		font=cv2.FONT_HERSHEY_SIMPLEX
		dispFullscreen = False
		cv2.namedWindow('Thermal',cv2.WINDOW_GUI_NORMAL)
		cv2.resizeWindow('Thermal', self.newWidth,self.newHeight)
		self.rad = 0 #blur radius
		self.threshold = 2
		self.hud = True
		self.recording = True # changed to start automatically?
		self.elapsed = "00:00:00"
		self.snaptime = "None"
		self.start = time.time()
		self.now = time.strftime("%Y%m%d--%H%M%S")
		
		self.file_path = file_path
# 		self.file_path = 'data/' + time.strftime("%Y%m%d-%H%M") + '/'
# 		os.makedirs(self.file_path, exist_ok=True)

		self.videoOut = cv2.VideoWriter(self.file_path+'thermal_video'+self.now+'output.avi', cv2.VideoWriter_fourcc(*'XVID'),25, (self.newWidth,self.newHeight))
		# creating a file to write temperature data to and timestamp, eventually gps data too....
		self.file =open('data/' + time.strftime("%Y%m%d-%H%M")+".txt","a")
		self.is_running = False
		self.my_thread = None

		self.gps_lock = gps_lock
		self.us_lock = us_lock
        

	def _snapshot(self, heatmap):
		self.now = time.strftime("%Y%m%d-%H%M%S") 
		self.snaptime = time.strftime("%H:%M:%S")
		last=str(time.gmtime()[1])+"-"+str(time.gmtime()[2])+"-"+str(time.gmtime()[0])+"hr"+str(time.gmtime()[3]-5)
		
		# right now this is requiring sudo to create a directory...
# 		fileDir="/media/pi/126 GB Volume/ECE480/ThermalCam/src/"
		fileDir = self.file_path + "thermalcamera_summary/"
# 		fileDir=fileDir+last
		fileDir=fileDir+last
		os.makedirs(fileDir, exist_ok=True)
		name= str(os.path.join(fileDir, self.now+".png"))
		# file1=open(name,'wb')
		#file1.write(heatmap)
		cv2.imwrite(name, heatmap)
		return self.snaptime
	
	def _collect_data(self):
		global curr_gps 
		curr_gps = '000'
		

		dev = 1 # removing argument "--device x" which allows to specify device, don't move the thermal camera location!
		cap = cv2.VideoCapture('/dev/video'+str(dev), cv2.CAP_V4L)
		cap.set(cv2.CAP_PROP_CONVERT_RGB, 0.0)
# 		print(cap.isOpened())v
# 		print(self.is_running)
		while(self.is_running and cap.isOpened()):
			# with self.gps_lock:
			self.gps_lock.acquire()
			gps = curr_gps
			self.gps_lock.release()

			# with self.us_lock:
			self.us_lock.acquire()
			dist = settings.curr_dist
			print(f'tc: {dist}')
			self.us_lock.release()
			# Capture frame-by-frame
			ret, frame = cap.read()
			if ret == True:
				imdata,thdata = np.array_split(frame, 2)
				hi = thdata[96][128][0]
				lo = thdata[96][128][1]
				lo = lo*256
				rawtemp = hi+lo
				temp = (rawtemp/64)-273.15
				temp = round(temp,2)

				#find the max temperature in the frame
				lomax = thdata[...,1].max()
				posmax = thdata[...,1].argmax()
				#since argmax returns a linear index, convert back to row and col
				mcol,mrow = divmod(posmax,self.width)
				himax = thdata[mcol][mrow][0]
				lomax=lomax*256
				maxtemp = himax+lomax
				maxtemp = (maxtemp/64)-273.15
				maxtemp = round(maxtemp,2)

				
				#find the lowest temperature in the frame
				lomin = thdata[...,1].min()
				posmin = thdata[...,1].argmin()
				#since argmax returns a linear index, convert back to row and col
				lcol,lrow = divmod(posmin,self.width)
				himin = thdata[lcol][lrow][0]
				lomin=lomin*256
				mintemp = himin+lomin
				mintemp = (mintemp/64)-273.15
				mintemp = round(mintemp,2)

				#find the average temperature in the frame
				loavg = thdata[...,1].mean()
				hiavg = thdata[...,0].mean()
				loavg=loavg*256
				avgtemp = loavg+hiavg
				avgtemp = (avgtemp/64)-273.15
				avgtemp = round(avgtemp,2)

				# Convert the real image to RGB
				bgr = cv2.cvtColor(imdata,  cv2.COLOR_YUV2BGR_YUYV)
				#Contrast
				bgr = cv2.convertScaleAbs(bgr, alpha=self.alpha)#Contrast
				#bicubic interpolate, upscale and blur
				bgr = cv2.resize(bgr,(self.newWidth,self.newHeight),interpolation=cv2.INTER_CUBIC)#Scale up!
				if self.rad>0:
					bgr = cv2.blur(bgr,(self.rad,self.rad))

				#apply colormap
				if self.colormap == 0:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_JET)
					cmapText = 'Jet'
				if self.colormap == 1:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_HOT)
					cmapText = 'Hot'
				if self.colormap == 2:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_MAGMA)
					cmapText = 'Magma'
				if self.colormap == 3:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_INFERNO)
					cmapText = 'Inferno'
				if self.colormap == 4:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PLASMA)
					cmapText = 'Plasma'
				if self.colormap == 5:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_BONE)
					cmapText = 'Bone'
				if self.colormap == 6:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_SPRING)
					cmapText = 'Spring'
				if self.colormap == 7:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_AUTUMN)
					cmapText = 'Autumn'
				if self.colormap == 8:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_VIRIDIS)
					cmapText = 'Viridis'
				if self.colormap == 9:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_PARULA)
					cmapText = 'Parula'
				if self.colormap == 10:
					heatmap = cv2.applyColorMap(bgr, cv2.COLORMAP_RAINBOW)
					heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
					cmapText = 'Inv Rainbow'

				#print(heatmap.shape)

				# draw crosshairs
				cv2.line(heatmap,(int(self.newWidth/2),int(self.newHeight/2)+20),\
				(int(self.newWidth/2),int(self.newHeight/2)-20),(255,255,255),2) #vline
				cv2.line(heatmap,(int(self.newWidth/2)+20,int(self.newHeight/2)),\
				(int(self.newWidth/2)-20,int(self.newHeight/2)),(255,255,255),2) #hline

				cv2.line(heatmap,(int(self.newWidth/2),int(self.newHeight/2)+20),\
				(int(self.newWidth/2),int(self.newHeight/2)-20),(0,0,0),1) #vline
				cv2.line(heatmap,(int(self.newWidth/2)+20,int(self.newHeight/2)),\
				(int(self.newWidth/2)-20,int(self.newHeight/2)),(0,0,0),1) #hline
				#show temp
				cv2.putText(heatmap,str(temp)+' C', (int(self.newWidth/2)+10, int(self.newHeight/2)-10),\
				cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 0, 0), 2, cv2.LINE_AA)
				cv2.putText(heatmap,str(temp)+' C', (int(self.newWidth/2)+10, int(self.newHeight/2)-10),\
				cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

				if self.hud==True:
					# display black box for our data
					cv2.rectangle(heatmap, (0, 0),(160, 120), (0,0,0), -1)
					# put text in the box
					cv2.putText(heatmap,'Avg Temp: '+str(avgtemp)+' C', (10, 14),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

					cv2.putText(heatmap,'Label Threshold: '+str(self.threshold)+' C', (10, 28),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

					cv2.putText(heatmap,'Colormap: '+cmapText, (10, 42),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

					cv2.putText(heatmap,'GPS: '+ gps +' ', (10, 56),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

					cv2.putText(heatmap,'Distance: '+str(round(dist,3))+' ', (10, 70),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

					cv2.putText(heatmap,'Contrast: '+str(self.alpha)+' ', (10, 84),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)


					cv2.putText(heatmap,'Snapshot: '+self.snaptime+' ', (10, 98),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)

					if self.is_running == False:
						cv2.putText(heatmap,'Recording: '+self.elapsed, (10, 112),\
						cv2.FONT_HERSHEY_SIMPLEX, 0.4,(200, 200, 200), 1, cv2.LINE_AA)
					if self.is_running == True:
						cv2.putText(heatmap,'Recording: '+self.elapsed, (10, 112),\
						cv2.FONT_HERSHEY_SIMPLEX, 0.4,(40, 40, 255), 1, cv2.LINE_AA)
# 					cv2.putText(heatmap,'GPS: ' + gps, (10, 116), \
# 					cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0, 255, 255), 1, cv2.LINE_AA)
				
				if maxtemp > avgtemp+self.threshold:
					cv2.circle(heatmap, (mrow*self.scale, mcol*self.scale), 5, (0,0,0), 2)
					cv2.circle(heatmap, (mrow*self.scale, mcol*self.scale), 5, (0,0,255), -1)
					cv2.putText(heatmap,str(maxtemp)+' C', ((mrow*self.scale)+10, (mcol*self.scale)+5),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,0), 2, cv2.LINE_AA)
					cv2.putText(heatmap,str(maxtemp)+' C', ((mrow*self.scale)+10, (mcol*self.scale)+5),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

				#display floating min temp
				if mintemp < avgtemp-self.threshold:
					cv2.circle(heatmap, (lrow*self.scale, lcol*self.scale), 5, (0,0,0), 2)
					cv2.circle(heatmap, (lrow*self.scale, lcol*self.scale), 5, (255,0,0), -1)
					cv2.putText(heatmap,str(mintemp)+' C', ((lrow*self.scale)+10, (lcol*self.scale)+5),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0,0,0), 2, cv2.LINE_AA)
					cv2.putText(heatmap,str(mintemp)+' C', ((lrow*self.scale)+10, (lcol*self.scale)+5),\
					cv2.FONT_HERSHEY_SIMPLEX, 0.45,(0, 255, 255), 1, cv2.LINE_AA)

				# display gps


				
				#display image
				#cv2.imshow('Thermal',heatmap)

				# if recording == True:
				self.elapsed = (time.time() - self.start)
				self.elapsed = time.strftime("%H:%M:%S", time.gmtime(self.elapsed)) 
				#print(self.elapsed)
				self.videoOut.write(heatmap)
				print("video Out")
				self.file.write("Time: "+ str(time.gmtime()[1])+"-"+str(time.gmtime()[2])+"-"+str(time.gmtime()[0])+"  "+str(time.gmtime()[3]-5)+":"+str(time.gmtime()[4])+":"+str(time.gmtime()[5])+"\n")
				self.file.write("Max Temp: "+ str(maxtemp)+"\n")
				self.file.write("Min Temp: "+ str(mintemp)+"\n")
				self.file.write("Average Temp:"+ str(avgtemp)+"\n")
				self.file.write("Location: "+ gps)
				self._snapshot(heatmap)
				
				if not self.is_running:
					self.file.close()
					self.recording == False
					cap.release()
					self.videoOut.release()
					print("closing funcs")
					cv2.destroyAllWindows()
					break
			else:
				break
		print('out of loop')
		
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
    tc = ThermalCamera()
    tc.start_data_collection()
    time.sleep(10)
    tc.stop_data_collection()
    print('stop')