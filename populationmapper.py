#Terrain map generator
import Image    #PIL library stuff
import ImageDraw
import sys
import random
import math
import cPickle
import convert  #a local module for converting image file types between libraries
import territory


FILE = open("height.map", 'r')
HM = cPickle.load(FILE)         #open the height map
FILE.close()

FILE = open("terrain.map", 'r')
TM = cPickle.load(FILE)         #open the height map
FILE.close()

heightMap = Image.open(HM.getFile())    #load the heightmap
stateMap = Image.open(TM.getFile())     #use the terrainmap as a basis for the pop. map
draw = ImageDraw.Draw(stateMap)

states = []             #list of territory objects (state boundaries)
cities = []             #list of city objects

xSize = heightMap.size[0]
ySize = heightMap.size[1]

#2D array of int's representing all pixels on map
#a value of -1 indicates an unclaimed pixel
#any other value is the state ID of the owner
claimed = []
for x in range(xSize):
    claimed.append([])
    for y in range(ySize):
        claimed[x].append(-1)

seaLevel = TM.getSeaLevel()             #get the sea level from the terrain map
mountains = TM.getMountains()           #get the mountain level from terrain map
aveSize = 5
stateCount = 195
pixelCount = xSize * ySize

#find all the water pixels, remove them from the pixel count, and color them blue
#also claim them: -2 = water
print "Mapping water..."
for x in range(xSize):
    for y in range(ySize):
        e = heightMap.getpixel((x,y))[0]
        if (e < seaLevel): 
            pixelCount -= 1
            draw.point((x,y), "rgb(0,0,255)")
            claimed[x][y] = -2

threshold = pixelCount / 10     #When only X% of the pixels are left unused, resort to method 2(faster)
freeLand = pixelCount / 20      #Leave X% of land unclaimed so human players can claim it
pixelCount -= freeLand

def makeStates():
    print "Generating states and capitols..."
    for newState in range(stateCount):
        state = territory.State()
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = 0 #random.randint(0,255)
        state.setMapColor((r,g,b))
        state.setName("State " + str(newState))
        state.setID(newState)
        stateSize = random.randint(1,(aveSize * 2))
        stateSize *= stateSize
        stateSize /= aveSize
        state.setSize(stateSize)
        
        #make a capitol city for the state and
        #make sure the city is above sea level
        capitol = territory.City()
        foundLocation = False
        x = 0
        y = 0
        while (foundLocation == False):
            x = random.randint(0,(xSize-1))
            y = random.randint(0,(ySize-1))
            e = heightMap.getpixel((x,y))[0]
            if (e >= seaLevel and e < mountains):
                foundLocation = True
        capitol.setPosition((x,y))
        claimed[x][y] = newState
        draw.point((x,y), "rgb(255,255,255)")
        state.addCity(capitol)
        state.getTerritory().setPixels((x,y))
        states.append(state)
        cities.append(capitol)
        foundLocation = True
        state.getTerritory().setName(state.getName())
        
def drawStates1():
    print "Mapping states..."
    global pixelCount
    while (pixelCount > threshold):
        print str(pixelCount)
        #pick a random state
        randState = random.randint(0,(stateCount-1))
        state = states[randState]
        stateSize = state.getSize()
        for num in range(stateSize):
            #expand from borders or randomly
            odds = random.randint(1,100000)
            if (odds <= 100000):
                #expand from border
                #randomly get a territory pixel
                pixels = state.getTerritory().getPixels()
                rand = random.randint(0,len(pixels)-1)
                pixel = pixels[rand]
                thisX = pixel[0]
                thisY = pixel[1]
                #change x val?
                if (random.randint(0,1)):
                    #up or down?
                    if (random.randint(0,1)): thisX += 1
                    else: thisX -= 1
                #change y val?
                if (random.randint(0,1)):
                    #up or down?
                    if (random.randint(0,1)): thisY += 1
                    else: thisY -= 1
                #wrap around the map (the world is round)
                if (thisY >= ySize):
                    thisX += (xSize / 2)
                    thisY = ySize - (thisY - (ySize - 1))
                if (thisY < 0):
                    thisX += (xSize / 2)
                    thisY *= -1
                if (thisX >= xSize): 
                    thisX -= xSize
                if (thisX < 0): 
                    thisX = xSize + thisX
                if ((claimed[thisX][thisY] == -1) and (heightMap.getpixel((thisX,thisY))[0] >= seaLevel)):
                    claimed[thisX][thisY] = state.getID()
                    pixels.append((thisX,thisY))
                    rgb = state.getMapColor()
                    r = str(rgb[0])
                    g = str(rgb[1])
                    b = str(rgb[2])
                    f = "rgb(" + r + "," + g + "," + b + ")"
                    draw.point((thisX,thisY), fill=f)
                    pixelCount -= 1
            else:
                #expand to a non-bordering region (establish colonies)
                thisX = random.randint(0,xSize-1)
                thisY = random.randint(0,ySize-1)
                if ((claimed[thisX][thisY] == -1) and (heightMap.getpixel((thisX,thisY))[0] >= seaLevel)):
                    claimed[thisX][thisY] = state.getID()
                    pixels.append((thisX,thisY))
                    rgb = state.getMapColor()
                    r = str(rgb[0])
                    g = str(rgb[1])
                    b = str(rgb[2])
                    f = "rgb(" + r + "," + g + "," + b + ")"
                    draw.point((thisX,thisY), fill=f)
                    pixelCount -= 1
                    
def drawStates2():
    global pixelCount
    #After the threshold is reached, resort to this method
    #make a list of unclaimed pixels
    unclaimed = []
    for x in range(xSize):
        for y in range(ySize):
            if (claimed[x][y] == -1):
                unclaimed.append((x,y))
    while (pixelCount > 0):
        print str(pixelCount)
        rand = random.randint(0,len(unclaimed)-1)
        pixel = unclaimed.pop(rand)
        pX = pixel[0]
        pY = pixel[1]
        foundState = False
        radius = 1
        while (foundState == False):
            for x in range(pX-radius,pX+radius+1):
                for y in range(pY-radius,pY+radius+1):
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
                    if (foundState == False):
                        if (claimed[x][y] > -1):
                            ID = claimed[x][y]
                            claimed[pX][pY] = ID
                            states[ID].getTerritory().getPixels().append((pX,pY))
                            rgb = states[ID].getMapColor()
                            r = str(rgb[0])
                            g = str(rgb[1])
                            b = str(rgb[2])
                            f = "rgb(" + r + "," + g + "," + b + ")"
                            draw.point((pX,pY), fill=f)
                            pixelCount -= 1
                            foundState = True
            if (foundState == False): radius += 1
        
def pickleMap():
    print "Storing map data..."
    #Make a Map() object and pickle it
    map = territory.PopulationMap()
    map.setName('Population Map')
    map.setFile('populationmap.jpg')
    map.setXSize(xSize)
    map.setYSize(ySize)
    map.setSeaLevel(seaLevel)
    map.setMountains(mountains)
    
    mapFile = "population.map"
    file = open(mapFile, "w")
    cPickle.dump(map, file, 2)
    file.close()


makeStates()
drawStates1()
stateMap.save("statemap.jpg")
pickleMap()