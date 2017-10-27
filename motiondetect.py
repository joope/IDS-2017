import cv2
import sys
import time
import numpy
import urllib.request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from collections import deque



br = 5
imageSize = (640, 360)
folder = 'public/'
interval = 60

api = 'http://siika.es:1337/motion'
heatmap_api = 'http://siika.es:1337/heatmap'
prev = []
new = []
heatmap = deque()

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
    img = cv2.resize(img, imageSize)
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

    diff = cv2.absdiff(prev, new)
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
    if(relativeThresholdChange >= 0.90 or relativeThresholdChange < 0.001):
        return None

    data = {
        'abs_change': absolutePixelChange,
        'rel_change': relativePixelChange,
        'thresh_change': relativeThresholdChange
    }

    return data

def processImages(prev, new):
    return cv2.addWeighted(prev, 0.5, new, 0.5, 0)

def getDiff(prev, new):
    diff = cv2.absdiff(prev, new)
    ret, diff = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)
    return diff

def sendData(api, data, location):
    if(data):
        data['location'] = location
        request = Request(api, urlencode(data).encode())
        json = urlopen(request).read().decode()
        print(json)

def main(url, room_id, interval, maxIterations):
    prev = cv2.blur(getImageFromUrl(url), (br,br))

    i = 0
    while i != maxIterations:
        time.sleep(interval)
        new = cv2.blur(getImageFromUrl(url), (br,br))
        data = compareImages(prev, new)
        sendData(api, data, room_id)
        prev = processImages(prev, new)
        i += 1

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Missing parameters: url(address to fetch images) room_id(integer) interval(minutes) max_iterations(-1 for infinite)')
    else:
        url = sys.argv[1]
        room_id = sys.argv[2]
        interval = int(sys.argv[3])
        max_iterations = int(sys.argv[4])

        main(url, room_id, interval, max_iterations)
