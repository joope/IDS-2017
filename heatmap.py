import cv2
import sys
import time
import numpy
import urllib.request
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import matplotlib as mpl
# Allows generating plots without display device
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from collections import deque

br = 5
imageSize = (640, 360)
folder = 'public/'
interval = 60

prev = []
new = []
heatmap = deque()

sources = [
    'http://haba.tko-aly.fi/kuvat/webcam1.jpg',
    'http://haba.tko-aly.fi/kuvat/webcam2.jpg'
]

# Read image from url as greyscale
def getImageFromUrl(url):
    res = urllib.request.urlopen(url)
    img = numpy.asarray(bytearray(res.read()), dtype="uint8")
    img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, imageSize)
    return img

def getDiff(prev, new):
    diff = cv2.absdiff(prev, new)
    ret, diff = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)
    diff = diff / 255
    return diff.astype(int)

def normalize(heatmap):
    maxp = numpy.amax(heatmap)
    return heatmap / maxp

def generateHeatmap(heatmap, room_id):
    plt.axis('off')
    plt.figure(figsize=(20,10))
    hmap = plt.imshow(normalize(heatmap))
    hmap.set_cmap('nipy_spectral')
    plt.axis('off')
    plt.savefig(folder + 'heatmap_' + room_id + '.png', bbox_inches='tight')
    plt.close()

def main(url, room_id, interval, maxIterations):
    prev1 = cv2.blur(getImageFromUrl(sources[0]), (br,br))
    prev2 = cv2.blur(getImageFromUrl(sources[1]), (br,br))
    heatmap1 = numpy.zeros((imageSize[1], imageSize[0]), numpy.uint16)
    heatmap2 = numpy.zeros((imageSize[1], imageSize[0]), numpy.uint16)

    i = 0
    while i != maxIterations:
        time.sleep(interval)
        new1 = cv2.blur(getImageFromUrl(sources[0]), (br,br))
        new2 = cv2.blur(getImageFromUrl(sources[1]), (br,br))
        heatmap1 = numpy.add(heatmap1, getDiff(prev1, new1))
        heatmap2 = numpy.add(heatmap2, getDiff(prev2, new2))
        generateHeatmap(heatmap1, '1')
        generateHeatmap(heatmap2, '2')
        prev1 = new1
        prev2 = new2

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
