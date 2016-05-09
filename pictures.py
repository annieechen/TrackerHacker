import os
import time

FRAMES = 8500
#FRAMES = 5


frameCount = 0
while frameCount < FRAMES:
	intNum = frameCount
	#imageNumber=str(intNum)
	imageNumber =time.strftime("%Y_%m_%d-%H_%M_%S")
	timeData = imageNumber.split('-', 1)
	date=timeData[0]
	#print(date)
	path = "/home/pi/launch/images/"
	dirpath = path+date
	if not os.path.exists(dirpath):
    		os.makedirs(dirpath)
	fname = imageNumber + ".jpg"
	while os.path.isfile(path+fname) == True:
		intNum+=1
		imageNumber = str(intNum)
		fname ="error" + imageNumber + ".jpg"
	os.system("raspistill -t 1000 --colfx 128:128 -awb sun -w 680 -h 680 -o %s/%s"%(dirpath, fname))
	frameCount +=1 
