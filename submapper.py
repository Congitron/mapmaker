#!/usr/bin/env python
#The submapper is for generating heightmaps at levels 2, 3, and 4

import Image            #PIL library stuff
import ImageDraw
import sys
import random
import math
import cPickle
import os, os.path
import convert          #a local module for converting image file types between libraries
import territory        #this will change to wherever the lemon modules are

#We'll use a small map class to hold each map object
class Map():
    path = ''
    file = ''
    state = 0
    map = ''
    draw = ''
    xSize = 1
    ySize = 1
    e = None                  #2D array of elevation values[x][y]
    
#    def __init__(self):

    def initE(self):
        self.e = []
        for x in range(self.xSize):
            self.e.append([])
            for y in range(self.ySize):
                self.e[x].append(0)


#submapper takes command line arguments:
#0 submapper.py (default behavior for sys.arg, ignore this one)
#1 path to world folder (i.e. "world_2/")
#2 path to base map, not including world folder (map from which you choose a pixel to expand)
#3 level of base map (1 for world map, etc [1,2,3,4])
#4 x coordinate of pixel to map (from base map)
#5 y coordinate of pixel to map

basePath = ''
baseMap = ''
baseMapRoot = ''
baseMapLevel = 1
targetX = ''
targetY = ''
init = False
mapped = False

#check the command line arguments for correct number of items
if (len(sys.argv) > 1 and len(sys.argv) != 6):
    print "\nUsage:"
    print "submapper takes 5 arguments:"
    print "1. path to base map (folder)"
    print "2. base map file name"
    print "3. level of base map"
    print "4. x coordinate of pixel to map"
    print "5. y coordinate of pixel to map"
    print ""
    print "example: python submapper.py world_1/ heightmap.jpg 1 223 67"
    print ""
    sys.exit()
   
if (len(sys.argv) == 6):
    basePath = sys.argv[1]
    baseMap = sys.argv[2]
    baseMapLevel = int(sys.argv[3])
    targetX = sys.argv[4]
    targetY = sys.argv[5]
else:
    #warning: no system in place to check validity of user input!
    basePath = raw_input('Path to base map (folder): ')
    baseMap = raw_input('base map file name: ')
    baseMapLevel = int(raw_input('level of base map: '))
    targetX = raw_input('x coordinate of pixel to map: ')
    targetY = raw_input('y coordinate of pixel to map: ')

targetMapLevel = baseMapLevel + 1
targetPath = "x" + targetX + "y" + targetY

if (os.path.isdir(basePath + targetPath)):
    pass
else:
    os.system('mkdir ' + basePath + targetPath)
    
if (os.path.isfile(basePath + targetPath + "/heightmap.jpg")):
    mapped = True
    print "Heightmap already exists."
    sys.exit()
elif (os.path.isfile(basePath + targetPath + "/init.jpg")):
    init = True

xSize = 256
ySize = 256

if (targetMapLevel == 2):
    xSize = 256
    ySize = 256
if (targetMapLevel == 3):
    xSize = 32
    ySize = 32
if (targetMapLevel == 4):
    xSize = 16
    ySize = 16
    

#initialize a 2D array of map objects
maps = []
for x in range(3):
    maps.append([])
    for y in range(3):
        maps[x].append(Map())
        maps[x][y].xSize = xSize
        maps[x][y].ySize = ySize
        maps[x][y].initE()
targetMap = [1,1]       #the coordinates to the targetMap in maps[][]


e = []                               #2D array of elevation values[x][y]
for x in range(xSize):
    e.append([])
    for y in range(ySize):
        e[x].append(0)
        

heightMap = Image.new("RGB", (xSize, ySize))
#heightMap = Image.open('backup.jpg')
if (init == True):
    heightMap = Image.open(basePath + targetPath + "/init.jpg")
    for x in range(xSize):
        for y in range(ySize):
            e[x][y] = heightMap.getpixel((x,y))[0]


#Now that the target map is setup and ready to go, setup the neighboring map 
#directories and initialize any maps if need be
print "Initializing map area..."
for x in range(3):
    for y in range(3):
        if (x != 1 or y != 1):
            thisMap = maps[x][y]
            difX = x - 1
            difY = y - 1
            thisX = int(targetX) + difX
            thisY = int(targetY) + difY
            #check to see if the folder already exists for these coordinates
            thisMap.path = basePath + "x" + str(thisX) + "y" + str(thisY)
            path = thisMap.path
            if (os.path.isdir(path) == False):
                os.system('mkdir ' + path)
            
            #look for init.jpg or heightmap.jpg
            if (os.path.isfile(path + "/heightmap.jpg")):
                thisMap.map = Image.open(path + "/heightmap.jpg")
                #load the image into the 2D array
                for m in range(thisMap.xSize):
                    for n in range(thisMap.ySize):
                        thisMap.e[m][n] = thisMap.map.getpixel((m,n))[0]
                thisMap.state = 2
            elif (os.path.isfile(path + "/init.jpg")):
                thisMap.map = Image.open(path + "/init.jpg")
                thisMap.draw = ImageDraw.Draw(thisMap.map)
                #now load the pixels into map.e[][]
                for m in range(thisMap.xSize):
                    for n in range(thisMap.ySize):
                        thisMap.e[m][n] = thisMap.map.getpixel((m,n))[0]
                thisMap.state = 1
            else:
                #we need to make a new init.jpg map
                thisMap.map = Image.new("RGB", (xSize, ySize))
                thisMap.draw = ImageDraw.Draw(thisMap.map)
                for a in range(xSize):
                    for b in range(ySize):
                        value = random.randint(0,255)
                        thisMap.e[a][b] = value    
                thisMap.state = 1


draw = ImageDraw.Draw(heightMap)



def randomMap():
    print "Generating random noise..."
    #generate random static
    for x in range(xSize):
        for y in range(ySize):
            value = random.randint(0, 255)
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
                targetMap = [1,1]
                x = thisX
                y = thisY
                xDist = centerX - x
                yDist = centerY - y
                dist = math.sqrt((xDist * xDist) + (yDist * yDist))
                if (dist <= r):
                    #check if you're out of the map bounds and wrap around
                    if (y >= ySize):
                        y -= ySize
                        targetMap[1] = 2
                    if (y < 0):
                        y = ySize + y
                        targetMap[1] = 0
                    if (x >= xSize): 
                        x -= xSize
                        targetMap[0] = 2
                    if (x < 0): 
                        x = xSize + x
                        targetMap[0] = 0
                    
                    #if we didn't wander on to a neighboring map..
                    if (targetMap == [1,1]):
                        c = e[x][y]
                        if (upDown == 1): c += strength
                        else: c -= strength
                        e[x][y] = c
                    #if we need to write onto a neighboring map
                    #first, check if it's mapped yet.  Only map if in state 1
                    else:
                        nMap = maps[targetMap[0]][targetMap[1]]     #nMap = neighbor map
                        if (nMap.state == 1):
                            c = nMap.e[x][y]
                            if (upDown == 1): c += strength
                            else: c -= strength
                            nMap.e[x][y] = c
    '''
    #now we need to make sure we save all the changes to the neighbor maps
    for x in range(3):
        for y in range(3):
            #skip coordinate (1,1), that's the main target map, not a neighbor
            if (x != 1 or y != 1):
                path = maps[x][y].path
                maps[x][y].map.save(path + "/init.jpg")
    '''
                    
       
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
                    targetMap = [1,1]
                    #wrap around the image
                    if (y >= ySize):
                        y -= ySize
                        targetMap[1] = 2
                    if (y < 0):
                        y = ySize + y
                        targetMap[1] = 0
                    if (x >= xSize): 
                        x -= xSize
                        targetMap[0] = 2
                    if (x < 0): 
                        x = xSize + x
                        targetMap[0] = 0
            
                    if (targetMap == [1,1]):
                        value += e[x][y]
                    else:
                        nMap = maps[targetMap[0]][targetMap[1]]
                        value += nMap.e[x][y]
            value /= 9
            e[allX][allY] = value
        
def exaggerate():
    print "Exaggerating..."
    #Draws elevation values toward extremes; good for making continents, etc
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

def rescaleNMaps():
    print "Rescaling surrounding maps..."
    #Takes the range of elevations and remaps it to [0,255]
    for a in range(3):
        for b in range(3):
            if ((a != 1 or b != 1) and (maps[a][b].state == 1)):
                low = 255
                high = 0
                nMap = maps[a][b]
                for x in range(xSize):
                    for y in range(ySize):
                        if (nMap.e[x][y] < low): low = nMap.e[x][y]
                        if (nMap.e[x][y] > high): high = nMap.e[x][y]
                eRange = high - low
                mult = 255.0 / float(eRange)
                for x in range(xSize):
                    for y in range(ySize):
                        val = nMap.e[x][y] - low
                        val = int(val * mult)
                        nMap.e[x][y] = val
                newLow = 255
                newHigh = 0
                for x in range(xSize):
                    for y in range(ySize):
                        val = nMap.e[x][y]
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
    heightMap.save(basePath + targetPath + "/heightmap.jpg")
    
def writeNMaps():
    print "Writing neighboring map images to files..."
    #write the neighboring map images to files
    for x in range(3):
        for y in range(3):
            if ((x != 1 or y != 1) and (maps[x][y].state == 1)):
                nMap = maps[x][y]
                for a in range(nMap.xSize):
                    for b in range(nMap.ySize):
                        value = str(nMap.e[a][b])
                        f = "rgb(" + value + "," + value + "," + value + ")"
                        nMap.draw.point((a,b), fill=f)
                nMap.map.save(nMap.path + "/init.jpg")

def correctAverage():
    print "Correcting target heightmap to match base map..."
    #load the base map and check the value of the pixel that was mapped
    complete = False
    while (complete == False):
        complete = True
        global targetX
        global targetY
        targetX = int(targetX)
        targetY = int(targetY)
        baseAvg = Image.open(basePath + baseMap).getpixel((targetX,targetY))[0]
        targetAvg = 0
        for x in range(xSize):
            for y in range(ySize):
                targetAvg += e[x][y]
        targetAvg /= (x * y)
        dif = baseAvg - targetAvg
        for x in range(xSize):
            for y in range(ySize):
                e[x][y] += dif
                if (e[x][y] < 0):
                    e[x][y] = 0
                    complete = False
                if (e[x][y] > 255):
                    e[x][y] = 255
                    complete = False
            

pauseCount = 0
            
#Run the Heightmap generation sequence

if (init == False):
    #there's no init.jpg file to load
    randomMap()
    
circleCount = (xSize * ySize) / 800  #divide by less for more circles
circles(circleCount)

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
correctAverage()
writeImage()

rescaleNMaps()
writeNMaps()

if (init == True): os.system("rm " + basePath + targetPath + "/init.jpg")   #delete the init file now that it's mapped

print "All done!"

