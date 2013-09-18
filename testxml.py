from math import *
from euclid import *
from omega import *
from cyclops import *

from xml.dom import minidom
import utm
import re

scene = getSceneManager()

# Load a static osgearth 'model'
cityModel1 = ModelInfo()
cityModel1.name = "city1"
cityModel1.path = "chicago_yahoo.earth"
scene.loadModel(cityModel1)

city1 = StaticObject.create("city1")
city1.getMaterial().setLit(False)

setNearFarZ(1, 2 * city1.getBoundRadius())
#deal with the camera
cam = getDefaultCamera()
cam.setPosition(city1.getBoundCenter() + Vector3(7768.82, 2281.18, 2034.08))
#cam.setPosition(city1.getBoundCenter() )
cam.getController().setSpeed(2000)
cam.pitch(3.14159*0.45) #pitch up to start off flying over the city
#set up the scene
all = SceneNode.create("everything")
all.addChild(city1)
########################################################################################
#
# Draw the district boundaries
#
# viewposition		== list of center point of each node
# communityList 	== list of the name of each community
#
########################################################################################
vector = ".\\data\\communities.kml"

xmldoc = minidom.parse(vector)

communityList = []
itemlist = xmldoc.getElementsByTagName('description')
for node in itemlist:
	str = node.firstChild.data.encode('ascii', 'ignore')
	list = str.split('\n')
	for line in list:
		if ( re.search('COMMUNITY', line) != None ):
			xml = minidom.parseString(line)
			tag = xml.getElementsByTagName('span')
			communityList.append(tag[1].firstChild.data.encode('ascii', 'ignore'))
			break

#Add a random color for boundaries
#Add text for district view



viewposition = []
itemlist = xmldoc.getElementsByTagName('MultiGeometry') 
for node in itemlist:
	coord = node.getElementsByTagName('coordinates')
	first = True
	for line in coord:
		str = line.firstChild.nodeValue.encode('ascii', 'ignore')
		if (first):
			first = False
			xy = str.partition(',')
			result = utm.from_latlon(float(xy[2]), float(xy[0]))
			viewposition.append(Vector2( float(result[0]),float(result[1])))
		else:
			districtBound = LineSet.create()
			districtBound.setEffect('colored -d blue')
			firstTime = True
			pointArray = str.split(' ')
			for pos in pointArray:
				xy = pos.partition(',')
				result = utm.from_latlon(float(xy[2]), float(xy[0]))
				if firstTime == True:
					firstTime = False
					oldX = float(result[0])
					oldY = float(result[1])
				elif ( abs(Vector2(oldX, oldY) - Vector2( float(result[0]),float(result[1]))) > 20 ):
					l = districtBound.addLine()
					l.setStart(Vector3(oldX, oldY, 10))
					l.setEnd(Vector3(float(result[0]), float(result[1]), 10))
					l.setThickness(20.0)
					oldX = float(result[0])
					oldY = float(result[1])
			firstTime = True	
	first = True

