#CityMapper.  This script generates a city on the terrain in a 2D, tile-like format.
#The city map can then be used by CityBuilder to generate a 3D city in Panda3D.

import Image    #PIL library stuff
import ImageDraw
import sys
import random
import math
import cPickle
import convert  #a local module for converting image file types between libraries
import territory


#
#Initialization Stuff
#

FILE = open("height.map", 'r')
HM = cPickle.load(FILE)         #open the height map
FILE.close()

FILE = open("terrain.map", 'r')
TM = cPickle.load(FILE)         #open the terrain map
FILE.close()

heightMap = Image.open(HM.getFile())
xSize = heightMap.size[0]
ySize = heightMap.size[1]
cityMap = Image.open(TM.getFile())

seaLevel = TM.getSeaLevel()
mountains = TM.getMountains()

#Codes for mapping the city:
#0 - Nothing, unused
#1 - POI (point of interest)
#2 - Major Road (drawMajorRoads())
#3 - Street Grid - the grid zone (drawStreedGrid())
#4 - Street Grid - the actual street (drawStreetGrid())
city = []       
for x in range(xSize):
    city.append([])
    for y in range(ySize):
        city[x].append(0)
        

#the 2D streets[] array is used to keep track of which areas have been mapped with 
#street grids.  This is so to keep the grids themselves from overlapping.
gridCount = 0
streetGrids = []                       
for x in range(xSize):
    streetGrids.append([])
    for y in range(ySize):
        streetGrids[x].append(0)

draw = ImageDraw.Draw(cityMap)

#determine population and setup points of interest (POI's) for road mapping
population = random.randint(10000,1000000)
POI = []
numPOIs = population / 10000
POIs = []                       
for x in range(numPOIs):
    POIs.append([])
    for y in range(numPOIs):
        if (x == y): POIs[x].append(1)
        else: POIs[x].append(0)
num = numPOIs
while (num > 0):
    randX = random.randint(0,xSize-1)
    randY = random.randint(0,ySize-1)
    if (heightMap.getpixel((randX,randY))[0] > seaLevel):
        POI.append([randX,randY])
        city[randX][randY] = 1
        f = "rgb(255,255,255)"
        draw.point((randX,randY), fill=f)
        num -= 1
        

#
#Function Definitions
#

def makeLine2(a, b):
    #takes two points, a and b, and returns the line that connects them
    difX = b[0] - a[0]
    difY = b[1] - a[1]
    points = []
    
    if (difX != 0 and difY != 0):
        slope1 = float(b[1] - a[1]) / float(b[0] - a[0]) #real slope
        slope2 = (b[1] - a[1]) / (b[0] - a[0])           #rounded down (int)
        if (slope1 < 0): slope1 *= -1
        if (slope2 < 0): slope2 *= -1
        r = slope1 - slope2
        xP = False
        yP = False
        if (b[0] > a[0]): xP = True
        if (b[1] > a[1]): yP = True
    
        x = a[0]
        y = a[1]
    
        extra = 0
        #print "a is " + str(a) + " and b is " + str(b)
        go = True
        while (go):
            #print str(x) + "," + str(y)
            points.append([x,y])
            addY = slope2
            if (extra > 1):
                addY += 1
                extra -= 1
            if (yP): y += addY
            else: y -= addY
            if (xP): x += 1
            else: x -= 1
            extra += r
            
            if (yP == True and y > b[1]): go = False
            if (yP == False and y < b[1]): go = False
            if (xP == True and x > b[0]): go = False
            if (xP == False and x < b[0]): go = False
        
    else:
        if (difX == 0):
            #vertical line that causes divide by 0 problem
            #both points have same x, so...
            x = a[0]
            y1 = a[1]
            y2 = b[1]
            if (y1 > y2):
                y1 = b[1]
                y2 = a[1]
            for y in range(y1,y2):
                #print "vert: " + str(x) + ", " + str(y)
                points.append((x,y))
        if (difY == 0):
            #horizontal line: both points have same y, so...
            y = a[1]
            x1 = a[0]
            x2 = b[0]
            if (x1 > x2):
                x1 = b[0]
                x2 = a[0]
            for x in range(x1,x2):
                #print "hor: " + str(x) + ", " + str(y)
                points.append((x,y))

    return points

def makeLine(a,b):
    x0 = a[0]
    y0 = a[1]
    x1 = b[0]
    y1 = b[1]
    
    dx = x1 - x0
    dy = y1 - y0
        
    points = []
    points.append((x0,y0))
    
    if (abs(dx) > abs(dy)):     #slope < 1
        m = float(dy) / float(dx)
        b = float(y0 - (m * x0))
        if (dx < 0): dx = -1
        else: dx = 1
        while (x0 != x1):
            x0 += dx
            points.append((x0,(int((m * x0) + b))))
    else:       #slope > 1
        if (dy != 0):
            m = float(dx) / float(dy)
            b = float(x0 - (m * y0))
            if (dy < 0): dy = -1
            else: dy = 1
            while (y0 != y1):
                y0 += dy
                points.append((int((m * y0) + b),y0))
    return points

def drawMajorRoads():
    print "Building major roads..."
    for p1 in range(numPOIs):
        for p2 in range(numPOIs):
            rN = random.randint(0,1)
            if (POIs[p1][p2] == 0 and rN == 1):
                #there is no road connecting the POI's, so make one
                #only do this about half the time (if rN==1) because
                #by mapping each POI to only a few other POI's you will
                #connect the entire system.
                done = False
                here = POI[p1]
                there = POI[p2]
                while (done == False):
                    #first we need to look for possible routes
                    route = []
                    for x in range(3):
                        route.append([])
                        for y in range(3):
                            route[x].append(0)
                    newX = here[0]
                    newY = here[1]
                    difX = here[0] - there[0]
                    difY = here[1] - there[1]
                    #8 possible paths
                    if (difX > 0 and difY > 0):
                        #go NW
                        route[0][1] = 1
                        route[0][0] = 1
                        route[1][0] = 1
                    elif (difX > 0 and difY == 0):
                        #go W
                        route[0][0] = 1
                        route[0][1] = 1
                        route[0][2] = 1
                    elif (difX > 0 and difY < 0):
                        #go SW
                        route[0][1] = 1
                        route[0][2] = 1
                        route[1][2] = 1
                    elif (difX < 0 and difY > 0):
                        #go NE
                        route[1][0] = 1
                        route[2][0] = 1
                        route[2][1] = 1
                    elif (difX < 0 and difY == 0):
                        #go E
                        route[2][0] = 1
                        route[2][1] = 1
                        route[2][2] = 1
                    elif (difX < 0 and difY < 0):
                        #go SE
                        route[2][1] = 1
                        route[2][2] = 1
                        route[1][2] = 1
                    elif (difX == 0 and difY > 0):
                        #go N
                        route[0][0] = 1
                        route[1][0] = 1
                        route[2][0] = 1
                    elif (difX == 0 and difY == 0):
                        #shouldn't happen, you're there already
                        pass
                    elif (difX == 0 and difY < 0):
                        #go S
                        route[0][2] = 1
                        route[1][2] = 1
                        route[2][2] = 1
                    
                    hereE = heightMap.getpixel((here[0],here[1]))[0] #elevation at here[][]
                    newX = 0
                    newY = 0
                    lowestDifE = 1000
                    for x in range(3):
                        for y in range(3):
                            if (route[x][y] == 1):
                                thisXY = [1,1]
                                routeX = here[0] + (x-1)
                                routeY = here[1] + (y-1)
                                thisE = heightMap.getpixel((routeX,routeY))[0]
                                difE = thisE - hereE
                                if (difE < 0): difE *= -1
                                if (difE < lowestDifE):
                                    lowestDifE = difE
                                    newX = routeX
                                    newY = routeY          
                    
                    #calculate newX and newY by the time you get here
                    if (newX == there[0] and newY == there[1]):
                        #you've reached 'there'
                        POIs[p1][p2] = 1
                        done = True
                    elif (heightMap.getpixel((newX,newY))[0] < seaLevel):
                        #you've hit water
                        done = True
                    elif (city[newX][newY] == 2):
                        #you hit another road so just let them connect and stop
                        done = True
                    else:
                        #you haven't reached your target, hit water or a road, so build more road
                        city[newX][newY] = 2
                        f = "rgb(100,100,100)"
                        draw.point((newX,newY), fill=f)
                        here[0] = newX
                        here[1] = newY
                                                
def drawStreetGrid():
    print "Building street grid..."
    numGrids = numPOIs * 10
    for p1 in range(numGrids):
        #done = False
        randX = random.randint(0,xSize-1)
        randY = random.randint(0,ySize-1)
        #here = POI[p1]
        here = [randX,randY]
        gridType = random.randint(0,1) #0 N-S/E-W, 1 for diagonal
        blockSize = 10
        radius = random.randint(1,10) #blocks of grid in each direction
        global gridCount
        thisGrid = gridCount
        gridCount += 1
        if (gridType == 0):
            startX = here[0] - (radius * blockSize)
            startY = here[1] - (radius * blockSize)
            stopX = here[0] + (radius * blockSize)
            stopY = here[1] + (radius * blockSize)
            while (startX < 0):
                startX += blockSize
            while (stopX >= xSize):
               stopX -= blockSize
            while (startY < 0):
                startY += blockSize
            while (stopY >= ySize):
                stopY -= blockSize
            if (startX > stopX or startY > stopY):
                print "WHAT THE FUCK!!!!????!?!?!"
            for x in range(startX, stopX+1): #draw the horizontal roads
                go = True
                for y in range(startY, stopY+1):
                    if ((heightMap.getpixel((x,y))[0] > seaLevel) and (city[x][y] != 2) and (go)):
                        if ((city[x][y] == 3) and (streetGrids[x][y] != thisGrid)):
                            #this is a street on a grid, but it's not THIS grid so stop
                            go = False
                            
                        else:
                            #it's not a street on a grid so keep building the street
                            streetGrids[x][y] = thisGrid
                            city[x][y] = 3
                            if ((x == startX) or (((x-startX) % blockSize) == 0)):
                                city[x][y] = 4
                                f = "rgb(100,100,100)"
                                draw.point((x,y), fill=f)
                    else: 
                        go = False
                        
                    if (go == False): break
            for y in range(startY, stopY+1): #draw the vertical roads
                go = True
                for x in range(startX, stopX+1):
                    if ((heightMap.getpixel((x,y))[0] > seaLevel) and (city[x][y] != 2) and (go)):
                        if ((city[x][y] == 3) and (streetGrids[x][y] != thisGrid)):
                            #you hit another street grid so stop!
                            go = False
                            
                        else:
                            #keep going!
                            streetGrids[x][y] = thisGrid
                            city[x][y] = 3
                            if ((y == startY) or (((y-startY) % blockSize) == 0)):
                                city[x][y] = 4
                                f = "rgb(100,100,100)"
                                draw.point((x,y), fill=f)
                    else: 

                        go = False
                        
                    if (go == False): break
                    
            #set the whole region to this zone
            for a in range(startX, stopX):
                for b in range(startY, stopY):
                    streetGrids[a][b] = thisGrid
                    #v = str(thisGrid * 2)
                    #f = "rgb(" + v + "," + v + "," + v + ")"
                    #draw.point((a,b), fill=f)
                        

def drawStreetGrid2():
    print "Building street grid..."
    numGrids = numPOIs * 10
    for p1 in range(numGrids):
        print str(p1) + " of " + str(numGrids)
        #The following generation of randX and randY doesn't check to be sure that 
        #this point itself is a valid place to map.  Later this point will be used
        #in checking the line from makeLine() and thus if the center point isn't 
        #valid, none of the points in the grid are valid.  So it wastes a lot of time
        #if it picks a non-valid center point.  It'd be faster to check it here when
        #you get around to doing that..
        randX = random.randint(0,xSize-1)
        randY = random.randint(0,ySize-1)
        here = [randX,randY]
        gridType = random.randint(0,1) #0 N-S/E-W, 1 for diagonal
        blockSize = 10
        radius = random.randint(1,10) #blocks of grid in each direction
        global gridCount
        thisGrid = gridCount
        gridCount += 1
        if (gridType == 0):
            #make a square that represents the potential street grid
            startX = here[0] - (radius * blockSize)
            startY = here[1] - (radius * blockSize)
            stopX = here[0] + (radius * blockSize)
            stopY = here[1] + (radius * blockSize)
            while (startX < 0):
                startX += blockSize
            while (stopX >= xSize):
               stopX -= blockSize
            while (startY < 0):
                startY += blockSize
            while (stopY >= ySize):
                stopY -= blockSize
            if (startX > stopX or startY > stopY):
                print "WHAT THE FUCK!!!!????!?!?!"
            
            #Make a 2D array that sets all pixels in the grid to be non-valid for drawing on by default
            pG = []       #pG = potentialGrid
            for x in range(xSize):
                pG.append([])
                for y in range(ySize):
                    pG[x].append(False)
            
            #Check all the pixels in the potential grid to see if they should be included
            for x in range(startX, stopX+1):
                for y in range(startY, stopY+1):
                    a = (randX,randY)
                    b = (x,y)
                    line = makeLine(a,b)
                    use = True
                    for point in line:
                        thisX = point[0]
                        thisY = point[1]
                        #draw.point((thisX,thisY), fill="rgb(0,0,0)")
                        if ((heightMap.getpixel((thisX,thisY))[0] < seaLevel) or (city[thisX][thisY] != 0)):
                            use = False
                            #draw.point((thisX,thisY), fill="rgb(0,0,255)")
                    if (use == True):
                        pG[x][y] = True
                        #draw.point((x,y), fill="rgb(255,255,255)")
                        
            for x in range(startX, stopX+1): #draw the horizontal roads
                for y in range(startY, stopY+1):
                    if (pG[x][y] == True):
                        #build the street grid
                        streetGrids[x][y] = thisGrid
                        city[x][y] = 3
                        if ((x == startX) or (((x-startX) % blockSize) == 0)):
                            city[x][y] = 4
                            draw.point((x,y), fill="rgb(100,100,100)")                        
            for y in range(startY, stopY+1): #draw the vertical roads
                for x in range(startX, stopX+1):
                    if (pG[x][y] == True):
                            #build street grid
                            streetGrids[x][y] = thisGrid
                            city[x][y] = 3
                            if ((y == startY) or (((y-startY) % blockSize) == 0)):
                                city[x][y] = 4
                                f = "rgb(100,100,100)"
                                draw.point((x,y), fill=f)
    
            '''   #Shouldn't be needed now     
            #set the whole region to this zone
            for a in range(startX, stopX):
                for b in range(startY, stopY):
                    streetGrids[a][b] = thisGrid
                    #v = str(thisGrid * 2)
                    #f = "rgb(" + v + "," + v + "," + v + ")"
                    #draw.point((a,b), fill=f)
            '''
                        
        else:
            #draw a diagonal grid
            pass
        
                        
def pickleMap():
    print "Storing map data..."
    #Make a Map() object and pickle it
    map = territory.CityMap()
    map.setName('City Map')
    map.setFile('citymap.jpg')
    map.setXSize(xSize)
    map.setYSize(ySize)
    map.setSeaLevel(seaLevel)
    map.setMountains(mountains)
    map.setPopulation(population)
    
    mapFile = "city.map"
    file = open(mapFile, "w")
    cPickle.dump(map, file, 2)
    file.close()


#
#Run the functions
#

drawMajorRoads()
drawStreetGrid2()
cityMap.save('citymap.jpg')
#pickleMap()