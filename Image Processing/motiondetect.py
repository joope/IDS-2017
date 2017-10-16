import cv2
import sys
import time
import numpy
import urllib.request
import requests

red = (100,0,0)
blur = 5
kernel = numpy.ones((5,5), numpy.uint8)

api = 'http://siika.es:1337'


sources = [
	'http://haba.tko-aly.fi/kuvat/webcam1.jpg',
	'http://haba.tko-aly.fi/kuvat/webcam2.jpg'
]

seatCoordinates = [
	(960, 400), 
	(800, 500), 
	(610, 595), 
	(415, 745), 
	(600, 915), 
	(750, 1060), 
	(1340, 1030), 
	(1565, 800), 
	(1735, 615)]
	
def sendData(data):
	r = requests.post(api, data=data, allow_redirects=True)
	print r.content

def getImageFromUrl(url):
	res = urllib.request.urlopen(url)
	img = numpy.asarray(bytearray(res.read()), dtype="uint8")
	img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)

	return img

def checkSofas(img):
	for i, c in enumerate(seatCoordinates):
		x,y = c
		size = 20
		roi = img[y-size:y+size, x-size:x+size]
		mean = roi.mean()
		print("%s: %s" % (i, mean > 100))
		cv2.rectangle(img, (x-size, y-size), (x+size, y+size), red)

def compareImages(img1, img2):
	#blur1 = cv2.blur(img1, (10,10))
	#blur2 = cv2.blur(img2, (10,10))
	#diff = cv2.absdiff(blur1, blur2)
	diff = cv2.absdiff(img1, img2)
	ret, thresh = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)
	#checkSofas(thresh)
	#dilated = cv2.dilate(thresh, kernel, iterations=2)

	max = diff.shape[0]*diff.shape[1]*255
	print(numpy.sum(diff)/max) # Skaala: 200 000 - 50 000 000
	cv2.imshow('image', diff)
	cv2.waitKey(0)
	
	sendData()
	#cv2.imshow('image', thresh)
	#cv2.waitKey(0)
	#showImage(blur)
	#cv2.imshow('image', thresh)
	#cv2.waitKey(0)

prev1 = getImageFromUrl(sources[1])
#prev1 = cv2.imread('imageset/room1_clear.jpg', 0)

for i in range(0,10):
	time.sleep(5)
	new1 = getImageFromUrl(sources[1])
	blur1 = cv2.blur(new1, (blur,blur))
	compareImages(blur1, prev1)
	prev1 = cv2.addWeighted(prev1, 0.5, blur1, 0.5, 0)
            
