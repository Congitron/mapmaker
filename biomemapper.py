#Biome map generator
#This actually generates 3 maps:
#Precipitation map
#Temperature map
#Biome Map: based on the first 2

import Image            #PIL library stuff
import ImageDraw
import sys
import random
import math
import cPickle
import convert          #a local module for converting image file types between libraries
import territory


FILE = open("height.map", 'r')
HM = cPickle.load(FILE)         #open the height map
FILE.close()

FILE = open("terrain.map", 'r')
TM = cPickle.load(FILE)         #open the height map
FILE.close()

heightMap = Image.open(HM.getFile())

xSize = heightMap.size[0]
ySize = heightMap.size[1]

precipMap = Image.new("RGB", (xSize,ySize))
tempMap = Image.new("RGB", (xSize,ySize))
biomeMap = Image.new("RGB", (xSize,ySize))
biomeTable = Image.open('biome_table_3.jpg')


seaLevel = TM.getSeaLevel()
seaLevelTolerance = 0
mountains = TM.getMountains

temp = []                               #2D array of temperature values[x][y] -> map dimensions(512,256)
#manually intitialize 2D list so it works right:
for x in range(xSize):
    temp.append([])
    for y in range(ySize):
        temp[x].append(0.0)
rain = []                               #2D array of rain values[x][y] -> map dimensions(512,256)
for x in range(xSize):
    rain.append([])
    for y in range(ySize):
        rain[x].append(0.0)

        
equator = ySize / 2                     #map height / 2
degLat = ySize / 180                    #a degree of latitude in pixels
tropicN = equator - (25 * degLat)       #northern tropic is ~25 degrees N of equator
tropicS = equator + (25 * degLat)       #southern tropic is ~25 deg's S of equator
milesPerPixel = float(12500.0 / ySize)  #miles per pixel
#just for reference: there are ~69.44 miles / degree of lat
baseTemp = 90.0                         #degrees F at sea level in the tropics
#temp drops off at about 1 degree F per 50 miles beyond the tropics
milesPerDegree = 50
#temp drops off at ~1 degree F per 400 feet above sea level
#Mt Everest is about 29,000ft above sea level, so you need about 75 degrees of change (30000/400)
#taking sea level at 100 (on the 0-255 scale) that gives us 1 degree F change for every 2 points
#of elevation (on 0-255)
elevationPerDegree = 2

HadleyEffect = 40.0
baseRainfall = 170.0  #float/double
maxRainfall = 450.0   #float/double
cmPerElevation = float(baseRainfall / (255 - seaLevel))
cmTo255 = 255.0 / maxRainfall
deg30 = ySize / 6;    #this is the pixel equivalent of 30 degrees of latitude
deg15 = ySize / 12;   #15 degrees of latitude

tempToPixel = 81.0 / float(ySize)
rainToPixel = 450.0 / float(xSize)
cmFrom255 = float(maxRainfall) / 255.0;

drawPrecip = ImageDraw.Draw(precipMap)
drawTemp = ImageDraw.Draw(tempMap)
drawBiome = ImageDraw.Draw(biomeMap)


def makeTempMap():
    #generate the temperature map
    print "Generating temperature map..."
    for x in range(xSize):
        for y in range(ySize):
            elevation = heightMap.getpixel((x,y))[0]
            thisTemp = baseTemp
            if (y < tropicN):
                thisTemp -= ((tropicN - y) * milesPerPixel) / milesPerDegree
            if (y > tropicS):
                thisTemp -= ((y - tropicS) * milesPerPixel) / milesPerDegree
            if (elevation > (seaLevel + seaLevelTolerance)):
                thisTemp -= (elevation - (seaLevel + seaLevelTolerance)) / elevationPerDegree
            temp[x][y] = thisTemp
            val = str(int(thisTemp + 100))      #pad temps for pixel vals (0-255) so you don't get negatives
            f = "rgb(" + val + "," + val + "," + val + ")"
            drawTemp.point((x,y), fill=f)
    tempMap.save('temperaturemap.jpg')

def makePrecipMap():
    #generate the precipitation map
    print "Generating precipitation map..."
    for x in range(xSize):
        for y in range(ySize):
            #for every pixel, calculate cm of rainfall / year
            elevation = heightMap.getpixel((x,y))[0]
            thisRainfall = baseRainfall  #start w/ base rainfall @ sea level on  the ocean
            
            #modify rainfall by elevation
            if (elevation > (seaLevel + seaLevelTolerance)):
                thisRainfall -= float((elevation - (seaLevel + seaLevelTolerance)) * cmPerElevation)
                
            #modify rainfall by latitude
            if ((y > (equator + deg15) and y < (equator + deg30)) or (y < (equator - deg15) and y > (equator - deg30))):
                #this is a hot desert
                thisRainfall -= HadleyEffect
            
            if (y > (equator + (deg30*2)) or y < (equator - (deg30*2))):
                #this is a cold desert
                thisRainfall -= HadleyEffect
            
            #modify rainfall based on proximity to water (continental isolation deserts)
            lowX = x - deg15
            if (lowX < 0): lowX = 0
            lowY = y - deg15
            if (lowY < 0): lowY = 0
            hiX = x + deg15
            if (hiX >= xSize): hiX = xSize - 1
            hiY = y + deg15
            if (hiY >= ySize): hiY = ySize - 1
            
            foundWater = False
            
            for m in range(lowX,hiX+1):
                for n in range(lowY,hiY+1):
                    if (heightMap.getpixel((m,n))[0] <= seaLevel):
                        foundWater = True
                    if (foundWater): break
                if (foundWater): break
            if (foundWater == False): thisRainfall -= 50
            
            #eventually add rain shadows here..
            
            if (thisRainfall < 0): thisRainfall = 0
            rain[x][y] = thisRainfall
            
            #convert rainfall to pixel value for map image
            thisRainfall *= cmTo255
            val = str(int(thisRainfall))
            f = "rgb(" + val + "," + val + "," + val + ")"
            drawPrecip.point((x,y), fill=f)
            
    precipMap.save('precipitationmap.jpg')

def makeBiomeMap():
    #use the temperature and precipitation maps to make a biome map
    print "Generating biome map..."
    #precipMap = Image.open('precipitationmap.jpg')
    #tempMap = Image.open('temperaturemap.jpg')
    for x in range(xSize):
        for y in range(ySize):
            #if you've generated the precip and temp maps before calling 
            #makeBiomeMap() then you can just access rain[][] and temp[][]
            #but otherwise if you're loading previously generated temp and
            #precip maps you'll have to get the values from them and convert:
            #thisRain = float(precipMap.getpixel((x,y))[0] * cmFrom255) #rain[x][y]
            #thisTemp = float(tempMap.getpixel((x,y))[0] * cmFrom255) #temp[x][y]
            thisRain = rain[x][y]
            thisTemp = temp[x][y]
            if (thisTemp < 0.0): thisTemp = 0.0
            if (thisTemp > 80.0): thisTemp = 80.0
            xToUse = thisRain / rainToPixel
            yToUse = thisTemp / tempToPixel
            xToUse = int(xToUse)
            yToUse = int(yToUse)
            r = 0
            g = 0
            b = 0
            print str(thisRain) + " " + str(thisTemp)
            print str(xToUse) + " " + str(yToUse)
            if (heightMap.getpixel((x,y))[0] >= seaLevel):
                r = biomeTable.getpixel((xToUse,yToUse))[0]
                g = biomeTable.getpixel((xToUse,yToUse))[1]
                b = biomeTable.getpixel((xToUse,yToUse))[2]
            else:
                b = 128           
            f = "rgb(" + str(r) + "," + str(g) + "," + str(b) + ")"
            drawBiome.point((x,y), fill=f)            
    
    biomeMap.save('biomemap.jpg')
    
def pickleMap():
    print "Storing map data..."
    #Make a Map() object and pickle it
    map = territory.BiomeMap()
    map.setName('Biome Map')
    map.setFile('biomemap.jpg')
    map.setPrecipMap('precipitationmap.jpg')
    map.setTempMap('temperaturemap.jpg')
    map.setXSize(xSize)
    map.setYSize(ySize)
    map.setSeaLevel(seaLevel)
    map.setMountains(mountains)
    
    mapFile = "biome.map"
    file = open(mapFile, "w")
    cPickle.dump(map, file, 2)
    file.close()
    

makeTempMap()
makePrecipMap()
makeBiomeMap()
pickleMap()
