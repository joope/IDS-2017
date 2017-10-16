import cv2
import sys
import time
import numpy
import urllib.request
from urllib.parse import urlencode
from urllib.request import Request, urlopen

br = 5
kernel = numpy.ones((5,5), numpy.uint8)
interval = 10

api = 'http://siika.es:1337/motion'
prev = []
new = []

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

# Read image from url as greyscale
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

def showImageAndWait(img):
    cv2.imshow('image', img)
    cv2.waitKey(0)

def compareImages(prev, new):

    img1 = prev
    img2 = cv2.blur(new, (br,br))
        
    diff = cv2.absdiff(img1, img2)
    ret, thresh = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)

    # Absolute change in pixel values
    # Usually between 200 000 - 50 000 000
    absolutePixelChange = numpy.sum(diff)

    # Calculate maximum pixel values from image size
    maxPixelValue = diff.shape[0]*diff.shape[1]*255

    # Percentage of change relative to maximum change in pixels
    # If all pixels change from 0 -> 255, the value is 1,0
    relativePixelChange = absolutePixelChange / maxPixelValue

    # Percentage of change in thresholded image
    thresholdChange = numpy.sum(thresh)
    relativeThresholdChange = thresholdChange / maxPixelValue

    # Uncomment to view the images:
    # showImageAndWait(diff)
    # showImageAndWait(thresh)

    # Discard data if change is too much (i.e light switched off)
    if(relativeThresholdChange >= 0.80):
        return None

    data = {
        'abs_change': absolutePixelChange,
        'rel_change': relativePixelChange,
        'thresh_change': relativeThresholdChange
    }

    return data

def processImages(prev, new):
    processed = []
    for i, img in enumerate(new):
        blurred = cv2.blur(img, (br,br))
        processed.append(cv2.addWeighted(prev[i], 0.5, blurred, 0.5, 0))

    return processed

def sendData(data, location):
    if(data):
        data['location'] = location
        request = Request(api, urlencode(data).encode())
        json = urlopen(request).read().decode()
        print(json)

def fetchImages():
    images = []
    for cam in sources:
        images.append(getImageFromUrl(cam))
        
    return images


def mainLoop(interval, maxIterations=1000):
    prev = fetchImages()
    i = 0
    while i < maxIterations:
        time.sleep(interval)
        new = fetchImages()
        data1 = compareImages(prev[0], new[0])
        data2 = compareImages(prev[1], new[1])
        sendData(data1, 0)
        sendData(data2, 1)
        prev = processImages(prev, new)
              
        i += 1

mainLoop(60)


            
