#!/usr/bin/env python
#Command line based map generator for Citrus World Engine
#View the maps using the mapviewer tool

import Image    #PIL library stuff
import ImageDraw
import sys
import random
import math
import convert  #a local module for converting image file types between libraries

#Generate a world, starting with the top level map.  From there you zoom in and draw
#all the sub-maps.

xSize = 1024
ySize = 512
heightMap = Image.new("RGB", (xSize, ySize))
#heightMap = Image.open('backup.jpg')
draw = ImageDraw.Draw(heightMap)
    
def randomMap():
    print "Generating random noise..."
    #generate random static
    for x in range(xSize):
        for y in range(ySize):
            value = str(random.randint(0, 255))
            f = "rgb(" + value + "," + value + "," + value + ")"
            draw.point((x,y), fill=f)

def randomBlocks(size):
    print "Generating random " + str(size) + "x" + str(size) + " blocks..."
    #generate random static using blocks larger than single pixels
    for x in range(0, xSize, size):
        for y in range(0, ySize, size):
            value = str(random.randint(0,255))
            f = "rgb(" + value + "," + value + "," + value + ")"
            draw.rectangle([x,y,(x+size),(y+size)],fill=f)
            
def randomize(size=1):
    print "Randomizing map using " + str(size) + "x" + str(size) + " blocks..."
    #offset values of blocks (of size 'size') rather than pixels
    for x in range(0, xSize, size):
        for y in range(0, ySize, size):
            strength = random.randint(0,20)
            upDown = random.randint(0,1)
            for a in range(x,x+size):
                for b in range(y,y+size):
                    c = heightMap.getpixel((a,b))[0]
                    if (upDown == 1):
                        c += strength
                        if (c > 255): c = 255
                    else:
                        c -= strength
                        if (c < 0): c = 0
                    c = str(c)
                    f = "rgb(" + c + "," + c + "," + c + ")"
                    draw.point((a,b), fill=f)
            
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

                    c = heightMap.getpixel((x,y))[0]
                    if (upDown == 1):
                        c += strength
                        if (c > 255): c = 255
                    else:
                        c -= strength
                        if (c < 0): c = 0
                    c = str(c)
                    f = "rgb(" + c + "," + c + "," + c + ")"
                    draw.point((x,y), fill=f)
                    
       
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

                    value += heightMap.getpixel((x,y))[0]
            value /= 9
            c = str(value)
            f = "rgb(" + c + "," + c + "," + c + ")"
            draw.point((allX, allY), fill=f)
        
def exaggerate():
    print "Exaggerating..."
    for x in range(xSize):
        for y in range(ySize):
            val = heightMap.getpixel((x, y))[0]
            val *= val
            val /= 128
            if (val > 255): val = 255
            val = str(val)
            f = "rgb(" + val + "," + val + "," + val + ")"
            draw.point((x, y), fill=f)
  


#Run the Heightmap generation sequence


randomMap()
circles(600)
smooth()
smooth()
smooth()
exaggerate()
smooth()
smooth()
smooth()
exaggerate()

#-----------------down to here is good--------------------------

print "Saving image..."
heightMap.save("heightmap.jpg")
print "All done!"

