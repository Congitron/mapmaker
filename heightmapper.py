#!/usr/bin/env python
#Command line based map generator for Citrus World Engine
#View the maps using the mapviewer tool

import Image            #PIL library stuff
import ImageDraw
import sys
import random
import math
import cPickle
#import convert          #a local module for converting image file types between libraries
import territory        #this will change to wherever the lemon modules are

#Generate a world, starting with the top level map.  From there you zoom in and draw
#all the sub-maps.

xSize = 1024
ySize = 512
heightMap = Image.new("RGB", (xSize, ySize))
#heightMap = Image.open('backup.jpg')
draw = ImageDraw.Draw(heightMap)

e = []                               #2D array of elevation values[x][y]
for x in range(xSize):
    e.append([])
    for y in range(ySize):
        e[x].append(0)


def randomMap(low=0, high=255):
    print "Generating random noise..."
    #generate random static
    for x in range(xSize):
        for y in range(ySize):
            value = random.randint(low, high)
            e[x][y] = value

def randomBlocks(size):
    print "Generating random " + str(size) + "x" + str(size) + " blocks..."
    #generate random static using blocks larger than single pixels
    for x in range(0, xSize, size):
        for y in range(0, ySize, size):
            value = random.randint(0,255)
            e[x][y] = value
            
def randomize(size=1):
    print "Randomizing map using " + str(size) + "x" + str(size) + " blocks..."
    #offset values of blocks (of size 'size') rather than pixels
    for x in range(0, xSize, size):
        for y in range(0, ySize, size):
            strength = random.randint(0,20)
            upDown = random.randint(0,1)
            for a in range(x,x+size):
                for b in range(y,y+size):
                    c = e[a][b]
                    if (upDown == 1): c += strength
                    else: c -= strength
                    e[a][b] = c
            
def circles(count):
    print "Drawing circles..."
    #draw n random circles
    for n in range(count):
        r = random.randint(10,100)          #radius of the circle
        upDown = random.randint(0,1)        #increase or decrease value
        strength = random.randint(1,20)     #how much to change the value by
    
        #where to put the circle
        centerX = random.randint(0, xSize)
        centerY = random.randint(0, ySize)
        loX = centerX - r
        hiX = centerX + r
        loY = centerY - r
        hiY = centerY + r
    
        #traverse the circle
        for thisX in range(loX, (hiX + 1)):
            for thisY in range(loY, (hiY + 1)):
                x = thisX
                y = thisY
                xDist = centerX - x
                yDist = centerY - y
                dist = math.sqrt((xDist * xDist) + (yDist * yDist))
                if (dist <= r):
                    #check if you're out of the map bounds and wrap around
                    if (y >= ySize):
                        x += (xSize / 2)
                        y = ySize - (y - (ySize - 1))
                    if (y < 0):
                        x += (xSize / 2)
                        y *= -1
                    if (x >= xSize): 
                        x -= xSize
                    if (x < 0): 
                        x = xSize + x

                    c = e[x][y]
                    if (upDown == 1): c += strength
                    else: c -= strength
                    e[x][y] = c
                    
def craters(count):
    print "Generating crater impacts..."
    #draw n random circles
    for n in range(count):
        r = random.randint(10,100)          #radius of the circle        
    
        #where to put the circle
        centerX = random.randint(0, xSize)
        centerY = random.randint(0, ySize)
        loX = centerX - r
        hiX = centerX + r
        loY = centerY - r
        hiY = centerY + r
    
        #traverse the circle
        for thisX in range(loX, (hiX + 1)):
            for thisY in range(loY, (hiY + 1)):
                x = thisX
                y = thisY
                xDist = centerX - x
                yDist = centerY - y
                dist = math.sqrt((xDist * xDist) + (yDist * yDist))
                if (dist <= r):
                    #check if you're out of the map bounds and wrap around
                    if (y >= ySize):
                        x += (xSize / 2)
                        y = ySize - (y - (ySize - 1))
                    if (y < 0):
                        x += (xSize / 2)
                        y *= -1
                    if (x >= xSize): 
                        x -= xSize
                    if (x < 0): 
                        x = xSize + x

                    #make an impact crater.  The impact is deepest at the center
                    #and gets shallower as it approaches the edge of the circle.
                    c = e[x][y] - (r - (dist-1))
                    e[x][y] = c
                    
       
def smooth():
    print "Smoothing..."
    #Run the smoothing algorithm
    for allX in range(xSize):
        for allY in range(ySize):
            value = 0
            pixels = 0
            for thisX in range((allX-1), (allX+2)):
                for thisY in range((allY-1), (allY+2)):
                    x = thisX
                    y = thisY
                    
                    #wrap around the image
                    if (y >= ySize):
                        x += (xSize / 2)
                        y = ySize - (y - (ySize - 1))
                    if (y < 0):
                        x += (xSize / 2)
                        y *= -1
                    if (x >= xSize): 
                        x -= xSize
                    if (x < 0): 
                        x = xSize + x

                    value += e[x][y]
            value /= 9
            e[allX][allY] = value
        
def exaggerate():
    print "Exaggerating..."
    #Draws evevation values toward extremes; good for making continents, etc
    for x in range(xSize):
        for y in range(ySize):
            val = e[x][y]
            val *= val
            val /= 128
            e[x][y] = val
  
def squareVals():
    print "Squaring values..."
    #squares values
    for x in range(xSize):
        for y in range(ySize):
            val = e[x][y]
            val *= val
            e[x][y] = val

def rescale():
    print "Rescaling..."
    #Takes the range of elevations and remaps it to [0,255]
    low = 255
    high = 0
    for x in range(xSize):
        for y in range(ySize):
            if (e[x][y] < low): low = e[x][y]
            if (e[x][y] > high): high = e[x][y]
    eRange = high - low
    mult = 255.0 / float(eRange)
    for x in range(xSize):
        for y in range(ySize):
            val = e[x][y] - low
            val = int(val * mult)
            e[x][y] = val
    newLow = 255
    newHigh = 0
    for x in range(xSize):
        for y in range(ySize):
            val = e[x][y]
            if (val < newLow): newLow = val
            if (val > newHigh): newHigh = val
    if (newLow < 0 or newHigh > 255): 
        print "Warning: values out of color range: "
        print "low: " + str(newLow) + ", high: " + str(newHigh)

def writeImage():
    print "Writing image to file..."
    #Writes the map to the image file
    for x in range(xSize):
        for y in range(ySize):
            value = e[x][y]
            value = str(value)
            f = "rgb(" + value + "," + value + "," + value + ")"
            draw.point((x,y), fill=f)
    heightMap.save('heightmap.jpg')
    
def pickleMap():
    print "Storing map data..."
    #Make a Map() object and pickle it
    map = territory.HeightMap()
    map.setName('Height Map')
    map.setFile('heightmap.jpg')
    map.setXSize(xSize)
    map.setYSize(ySize)
    
    mapFile = "height.map"
    file = open(mapFile, "w")
    cPickle.dump(map, file, 2)
    file.close()
    
#Run the Heightmap generation sequence

#hmm...weird..the circles() algorithm is like craters from the earth getting pelted by meteors
#for millions of years.  The smoothing is like erosion..  Weird that it happens to work out 
#that way.  I didn't even think of that when I wrote the algorithms..


#Regular mapping sequence
randomMap()
circles(600)
smooth()
smooth()
smooth()
#seems to work pretty good with either exaggerate() or squareVals()
#exaggerate()
squareVals()
smooth()
smooth()
smooth()
rescale()
writeImage()
pickleMap()

'''
#attempt at craters and erosion..so far the regular version looks way cooler.
#this one actually has a really soft look.  It doesn't look very stylized.
randomMap(200,255)
craters(600)
smooth()
smooth()
smooth()
#squareVals()
#smooth()
#smooth()
#smooth()
rescale()
writeImage()
pickleMap()
'''

print "All done!"

