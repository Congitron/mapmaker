#Terrain map generator
import Image    #PIL library stuff
import ImageDraw
import sys
import random
import math
import cPickle
#import convert  #a local module for converting image file types between libraries
import territory


FILE = open("height.map", 'r')
HM = cPickle.load(FILE)         #open the height map
FILE.close()

heightMap = Image.open(HM.getFile())     #open height map image
xSize = heightMap.size[0]
ySize = heightMap.size[1]
terrainMap = Image.new("RGB", (xSize,ySize))

#The terrrain mapper uses a heightmap with values from 0 to 255.  The following variables determine where sea level and the tree line occur within that scale.
seaLevel = 80
mountains = 245


draw = ImageDraw.Draw(terrainMap)

def makeTerrain():
    print "Mapping terrain..."
    for x in range(xSize):
        for y in range(ySize):
            r = "0"
            g = "0"
            b = "0"
            e = heightMap.getpixel((x,y))[0]  #e = elevation
	    #up to seaLevel is blue, above is green.  Above "mountains"(tree line) is grey to white.
            if (e >= seaLevel):
                g = str(e)
                if (e >= mountains):
                    r = str(e)
                    b = str(e)
            else:
                b = str(e)
            f = "rgb(" + r + "," + g + "," + b + ")"
            draw.point((x,y), fill=f)
    terrainMap.save("terrainmap.jpg")
    
def pickleMap():
    print "Storing map data..."
    #Make a Map() object and pickle it
    map = territory.TerrainMap()
    map.setName('Terrain Map')
    map.setFile('terrainmap.jpg')
    map.setXSize(xSize)
    map.setYSize(ySize)
    map.setSeaLevel(seaLevel)
    map.setMountains(mountains)
    
    mapFile = "terrain.map"
    file = open(mapFile, "w")
    cPickle.dump(map, file, 2)
    file.close()
    
    
makeTerrain()
pickleMap()
