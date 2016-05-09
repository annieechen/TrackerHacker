import numpy as np
import cv2
import math
import random
import os
import os.path
from os import listdir
import shutil

#read in a directory of images.
#get images from oldest directory
pathToImages="/home/pi/launch/images"
directoryArray=[x[0] for x in os.walk(pathToImages)]
array2 = sorted(directoryArray)
pathToImages=array2[1]
imgArray=sorted(listdir(pathToImages))
print(pathToImages)
imNum=0
if imgArray[imNum] == ".DS_Store":
	imNum+=1

path=pathToImages + "/"

#backgroundImg1 = cv2.imread(path+imgArray[imNum],0)
backgroundImg1 = cv2.imread("/home/pi/launch/images/background.jpg",0)
width1, height1 = backgroundImg1.shape

CROPLEFT=150
CROPRIGHT=width1-150
CROPTOP=250
CROPBOTTOM=height1
LOWERTHRESHVAL=90

#scale backgroundImg
backgroundImg = backgroundImg1[CROPTOP:CROPBOTTOM, CROPLEFT:CROPRIGHT]
# cv2.imshow("background", backgroundImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

#write results to file (time vs. area)
f4=open('/home/pi/timestamp.txt', 'w+')
f4.write("Time        Area\n")

# Define dictionary to map index to Person.
ObjDict = {}

#Define Obj
class Person:
	def __init__(self, center=None, duration=1, color=None, time=None, area=None, date=None):
		self.center=center
		self.centers=[center]
		self.duration=duration
		self.color=color
		self.date=[date]
		self.time=[time]
		self.area=[area]
	def __str__(self):
		return str(self.duration)


#Define array of keys to compare frame-by-frame
keysToCompare = []

for imgNum in range(imNum+1, len(imgArray)):

	test=datetime.utcnow()
	if d.hour == 16 and d.minute > 58 :
		break

	if imgArray[imgNum]=="background.jpg":
		continue

	timeData = imgArray[imgNum].split('-', 1)
	time=timeData[1].split('.', 1)[0]
	date=timeData[0]
	time=time.replace('_', ':')
	date=date.replace('_', '/')
	f4.write(time)
	f4.write("    ")

	origimg1 = cv2.imread(path+imgArray[imgNum], 1)
	img1 = cv2.imread(path+imgArray[imgNum], 0)
	height2, width2 = img1.shape
	img = img1[CROPTOP:CROPBOTTOM, CROPLEFT:CROPRIGHT]
	origimg = origimg1[CROPTOP:CROPBOTTOM, CROPLEFT:CROPRIGHT]
	newimage=img.copy()

	height, width = newimage.shape

	#newimage = abs(cv2.subtract(img, backgroundImg)) * 20
	personDetected=False
	for i in range(0, height):
	    for j in range(0, (width)):
	    	a=int(img[i,j])
	    	b=int(backgroundImg[i,j])

	    	num=abs(a-b) * 8

	    	if num > 0:
	    		personDetected=True
	    	
	    	if num > 255:
	    		num=255
	        newimage[i,j] = num
	if personDetected==False:
		f4.write("0") #area = 0
		f4.write("\n")
		continue

	#IMAGE PROCESSING

	blur = cv2.medianBlur(newimage, 9)
	kernel = np.ones((9,9),np.uint8)
	dilation = cv2.dilate(blur,kernel,iterations = 1)
	#blur = cv2.GaussianBlur(blurr, (5,5), 0)
	closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
	ret2,threshImg = cv2.threshold(closing,LOWERTHRESHVAL,255,cv2.THRESH_BINARY)#+cv2.THRESH_OTSU)


	(__, cnts, _) = cv2.findContours(threshImg.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# cv2.imshow("Subtracted Threshold", threshImg)
	# #cv2.imshow("Background", backgroundImg)
	# #cv2.imshow("Img", img)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()


	numObjs=0
	centers=[]
	areas=[]


	#PER IMAGE: how many objects are there? 
	#Store each object!
	tArea = 0
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 2000:
			continue
		tArea += cv2.contourArea(c)
		numObjs += 1
		(x, y, w, h) = cv2.boundingRect(c)
		centers.append([x+(w)/2, y+(h)/2])
		areas.append(w * h)
		cv2.rectangle(origimg, (x, y), (x + w, y + h), (255, 255, 255))

	f4.write(str(tArea))
	f4.write("\n")

	if (numObjs == 0) and (keysToCompare == []):
		continue

	#Compare this image to previous image (if previous image exists)
	remove = [] #stores keys to remove
	if imgNum == 1:
		#define objects
		for i in range(0, len(centers)):
			r = lambda: random.randint(0,255)
			color = (r(), r(), r())
			ObjDict[i] = Person(centers[i], 1, color, time, areas[i], date)
			keysToCompare.append(i)
	else:
		#compare to previous image
		for i in range(0, len(keysToCompare)):
			#compare these to centers
			closest = 1000
			closestDist = 1000
			if numObjs <= 0:
				remove.append(keysToCompare[i]) #index of keysToCompare
				continue #this person is no longer here
			for j in range(numObjs):
				#we want to ask - for each previous obj - is the obj still there?
				#take closest obj?

				diffX = ObjDict[keysToCompare[i]].center[0] - centers[j][0]
				diffY = ObjDict[keysToCompare[i]].center[1] - centers[j][1]
				displacement = math.sqrt(diffX*diffX + diffY*diffY)

				if min(displacement, closestDist) == displacement:
					closest=j #index of obj
					closestDist=displacement
			#after for loop, closest index = persisting obj. update center in dict.
			#if closest is > some num, then obj no longer persists. remove from keysToCompare.
			if closestDist > 400:
				remove.append(keysToCompare[i]) #remove ith key
			else:
				#print("Updating: ", imgArray[imgNum])
				ObjDict[keysToCompare[i]].center = centers[closest]
				ObjDict[keysToCompare[i]].centers.append(centers[closest])
				ObjDict[keysToCompare[i]].area.append(areas[closest])
				ObjDict[keysToCompare[i]].time.append(time)
				ObjDict[keysToCompare[i]].date.append(date)
				ObjDict[keysToCompare[i]].duration += 1
				#do not consider centers[closest] anymore
				del centers[closest]
				numObjs -= 1

		count = 0
		for k in range(len(remove)):
			# print("KeysToCompare", keysToCompare)
			# print("remove: ", remove)
			# print("Removing index ", k-count)
			# print(keysToCompare)
			keysToCompare.remove(remove[k-count])
			#del keysToCompare[remove[k-count]]
			remove.pop(0)
			count+=1
		remove[:]=[]
		if numObjs > 0:

			k=len(ObjDict)
			for f in range(len(centers)):
				r = lambda: random.randint(0,255)
				color = (r(), r(), r())
				ObjDict[k]=Person(centers[f], 1, color, time, areas[f], date)
				keysToCompare.append(k)
				k+=1

	for c in keysToCompare:
		color=ObjDict[c].color
		a=ObjDict[c].center[0]
		b=ObjDict[c].center[1]
		center=(a, b)
		cv2.circle(origimg, center, 5, color)

#write data to output files
f2=open('/home/pi/datawrite.txt', 'w+')
f3=open('/home/pi/overalldata.txt', 'w+')
print("writing data")
totalDuration=0
avgDuration=0
for i in range(len(ObjDict)):
	totalDuration += ObjDict[i].duration
if totalDuration != 0:
	avgDuration = totalDuration/len(ObjDict)
f2.write("Date: %s\n" % date)
f2.write("Total number of people: %d\n" % (len(ObjDict)))
f2.write("Total duration spent (s): %d\n" % totalDuration)
f2.write("Avg duration of each person (s): %d\n\n\n" % avgDuration)

data = [['Object #', 'Entry Time', 'Duration', 'Avg Area']]
for i in range(len(ObjDict)):
	totalArea=0
	avgArea=0
	for a in ObjDict[i].area:
		totalArea+=a
	avgArea=totalArea/len(ObjDict[i].area)
	data.append([str(i+1), str(ObjDict[i].time[0]), str(ObjDict[i].duration), str(avgArea)])

col_width = max(len(word) for row in data for word in row) + 3
for row in data:
	f3.write("".join(word.ljust(col_width) for word in row))
	f3.write("\n")

shutil.rmtree(pathToImages)
