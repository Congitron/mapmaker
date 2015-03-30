#A map-making script that will run all the scripts for a world map (no level 2, 3, or 4)
import heightmapper
import terrainmapper
import biomemapper
import populationmapper
import os

#All this does is run all the mapping scripts in sequence
print "Launching world mapping sequence.  This may take a while."
os.system('python heightmapper.py')
os.system('python terrainmapper.py')
os.system('python biomemapper.py')
os.system('python populationmapper.py')