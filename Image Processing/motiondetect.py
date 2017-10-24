import cv2
import sys
import time
import numpy
import urllib.request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

br = 5
interval = 60

api = 'http://siika.es:1337/motion'
heatmap_api = 'http://siika.es:1337/heatmap'
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
    processed = []
    for i, img in enumerate(new):
        processed.append(cv2.addWeighted(prev[i], 0.5, new[i], 0.5, 0))

    return processed

def getDiff(prev, new):
    diff = cv2.absdiff(prev, new)
    ret, thresh = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)
    return thresh / 255

def updateHeatmap(heatmap, diff):
    return numpy.add(heatmap, diff)

def normalize(heatmap):
    maxp = numpy.amax(heatmap)
    normalized = heatmap / maxp

    return normalized

def sendData(api, data, location):
    if(data):
        data['location'] = location
        request = Request(api, urlencode(data).encode())
        json = urlopen(request).read().decode()
        print(json)

def saveHeatmaps(heatmap1, heatmap2):
    plt.axis('off')
    plt.figure(figsize=(20,10))
    hmap = plt.imshow(normalize(heatmap1))
    hmap.set_cmap('nipy_spectral')
    plt.savefig('heatmap1.png', bbox_inches='tight')

    hmap2 = plt.imshow(normalize(heatmap2))
    hmap2.set_cmap('nipy_spectral')
    plt.savefig('heatmap2.png', bbox_inches='tight')
    plt.close()

def fetchImages():
    images = []
    for cam in sources:
        blurred = cv2.blur(getImageFromUrl(cam), (br,br))
        images.append(blurred)
        
    return images


def main(interval, maxIterations=2880):     # 2880 minutes = 48 hours
    prev = fetchImages()
    heatmap1 = numpy.zeros((1080, 1920), numpy.uint32)
    heatmap2 = numpy.zeros((1080, 1920), numpy.uint32)

    i = 0
    while i < maxIterations:
        time.sleep(interval)
        new = fetchImages()
        data1 = compareImages(prev[0], new[0])
        data2 = compareImages(prev[1], new[1])
        heatmap1 = updateHeatmap(heatmap1, getDiff(prev[0], new[0]))
        heatmap2 = updateHeatmap(heatmap2, getDiff(prev[1], new[1]))
        saveHeatmaps(heatmap1, heatmap2)

        sendData(api, data1, 0)
        sendData(api, data2, 1)
        prev = new
        
        i += 1
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main(interval)

            
