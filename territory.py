#this is a collection of classes being used by the mapping scripts.
#these need to go into the appropriate .py files in the lemon module
#once they're complete.  This is just a temperary way to make it easy
#to load all the right classes into the mapmaking scripts...

class Territory():
    pixels = []         #takes tuples of two (x,y)
    name = ''
    
    def __init__(self):
        pixels = []
    def getPixels(self):
        return self.pixels
    def setPixels(self, p):
        self.pixels = [p]
    def addPixel(self, p):
        self.pixels.append(p)
    def getName(self):
        return self.name
    def setName(self, n):
        self.name = n

class State():
    #colors on state map
    r = 0
    g = 0
    b = 0
    
    stateID = -1
    name = ''
    cities = []
    territory = ''
    size = 0
    
    def __init__(self):
        self.territory = Territory()
    def getPixels(self):
        return self.pixels
    def setPixels(self, p):
        self.pixels = p
    def addPixel(self, p):
        self.pixels.append(p)
    def getID(self):
        return self.stateID
    def setID(self, id):
        self.stateID = id
    def getName(self):
        return self.name
    def setName(self, n):
        self.name = n
    def getMapColor(self):
        return (self.r,self.g,self.b)
    def setMapColor(self, rgb):
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
    def getCities(self):
        return self.cities
    def setCities(self, c):
        self.cities = c
    def addCity(self, c):
        self.cities.append(c)
    def removeCity(self, c):
        z = self.cities.pop(c)
    def popCity(self, c):
        return self.cities.pop(c)
    def getTerritory(self):
        return self.territory
    def setTerritory(self, t):
        self.territory = t
    def getSize(self):
        return self.size
    def setSize(self, s):
        self.size = s

class City():
    #(x, y) coordinates on map
    x = 0
    y = 0
    
    def getPosition(self):
        return (self.x,self.y)
    def setPosition(self, p):
        self.x = p[0]
        self.y = p[1]
    
class Map():
    fileName = ''
    name = ''
    seaLevel = 0
    mountains = 0
    xSize = 1024
    ySize = 512
    level = 1
    
    def getFile(self):
        return self.fileName
    def setFile(self, f):
        self.fileName = f
    def getName(self):
        return self.name
    def setName(self, n):
        self.name = n
    def getSeaLevel(self):
        return self.seaLevel
    def setSeaLevel(self, s):
        self.seaLevel = s
    def getMountains(self):
        return self.mountains
    def setMountains(self, m):
        self.mountains = m
    def getXSize(self):
        return self.xSize
    def setXSize(self, x):
        self.xSize = x
    def getYSize(self):
        return self.ySize
    def setYSize(self, y):
        self.ySize = y
    def getLevel(self):
        return self.level
    def setLevel(self, l):
        self.level = l
        
class HeightMap(Map):
    #mapped = []
    pass

class TerrainMap(Map):
    pass

class BiomeMap(Map):
    tempMap = ''
    precipMap = ''
    
    def getTempMap(self):
        return self.tempMap
    def setTempMap(self, t):
        self.tempMap = t
    def getPrecipMap(self):
        return self.precipMap
    def setPrecipMap(self, p):
        self.precipMap = p

class PopulationMap(Map):
    pass

class CityMap(Map):
    population = 0
    
    def getPopulation(self):
        return self.population
    def setPopulation(self, p):
        self.population = p
    

    
