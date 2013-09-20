from math import *
from euclid import *
from omega import *
from cyclops import *

from xml.dom import minidom
import utm
import re
import httplib
from random import randint

file1 = "./Data/communities.kml"
file2 = "./Data/CTARailLines.kml"
file3 = './Data/CTA_L_Stops'
trainRoot = SceneNode.create('trains')

scene = getSceneManager()
all = SceneNode.create("everything")
all.addChild(trainRoot)


########################################################################################
#
# Load the yahoo map
#
# viewposition		== list of center point of each node
# communityList 	== list of the name of each community
# mapList				== dic of available map handler
#
########################################################################################
mapList = {}

# Load satelite map
cityModel1 = ModelInfo()
cityModel1.name = "map"
cityModel1.path = "chicago_yahoo.earth"
scene.loadModel(cityModel1)
city1 = StaticObject.create("map")
city1.getMaterial().setLit(False)
mapList.update( { 'map' : city1 })
all.addChild(city1)

# Load road map
cityModel2 = ModelInfo()
cityModel2.name = "sat"
cityModel2.path = "chicago_yahoo_sat.earth"
scene.loadModel(cityModel2)
city2 = StaticObject.create("sat")
city2.getMaterial().setLit(False)
city2.setVisible(False)
mapList.update( { 'satellite' : city2 })
all.addChild(city2)

setNearFarZ(1, 2 * city1.getBoundRadius())
#deal with the camera
cam = getDefaultCamera()
cam.setPosition(city1.getBoundCenter() + Vector3(7768.82, 2281.18, 2034.08))
#cam.setPosition(city1.getBoundCenter() )
cam.getController().setSpeed(2000)
cam.pitch(3.14159*0.45) #pitch up to start off flying over the city
#set up the scene

########################################################################################
#
# Draw the district boundaries
#
# viewposition		== list of center point of each node
# communityList 	== list of the name of each community
#
########################################################################################

xmldoc = minidom.parse(file1)

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

viewposition = []
index = 0
itemlist = xmldoc.getElementsByTagName('MultiGeometry')
for node in itemlist:
	r = randint(0,255)
	g = randint(0,255)
	b = randint(0,255)
	color = Color(r/255.0, g/255.0, b/255.0, 1)
	coord = node.getElementsByTagName('coordinates')
	first = True
	for line in coord:
		str = line.firstChild.nodeValue.encode('ascii', 'ignore')
		if (first):
			first = False
			xy = str.partition(',')
			result = utm.from_latlon(float(xy[2]), float(xy[0]))
			viewposition.append(Vector3( float(result[0]),float(result[1]), 0 ) )
			t = Text3D.create('fonts/arial.ttf', 200, communityList[index])
			t.setPosition( viewposition[index] + Vector3(0,0,300))
			t.setColor( color )
			districtBound = LineSet.create()
			districtBound.setEffect('colored -e #' + hex(r)[2:] + hex(g)[2:] + hex(b)[2:] + 'dd -t')
			l = districtBound.addLine()
			l.setStart(viewposition[index])
			l.setEnd(viewposition[index] + Vector3(0,0,300))
			l.setThickness(30.0)
			#t.setFixedSize(True)
			#t.setFacingCamera(cam)
			index+=1
		else:
			firstTime = True
			pointArray = str.split(' ')
			for pos in pointArray:
				xy = pos.partition(',')
				result = utm.from_latlon(float(xy[2]), float(xy[0]))
				if firstTime == True:
					firstTime = False
					oldX = float(result[0])
					oldY = float(result[1])
				elif ( abs(Vector2(oldX, oldY) - Vector2( float(result[0]),float(result[1]))) > 30 ):
					l = districtBound.addLine()
					l.setStart(Vector3(oldX, oldY, 10))
					l.setEnd(Vector3(float(result[0]), float(result[1]), 10))
					l.setThickness(40.0)
					oldX = float(result[0])
					oldY = float(result[1])
			firstTime = True
	first = True


########################################################################################
#
# Draw the subway system
#
########################################################################################

# first the set of L stops
f = open(file3)
ctastops = [line.rstrip('\n') for line in f]

for name in ctastops:
	#print name
	foo = name.strip(' ()"')
	bar = foo.partition(', ')
	result = utm.from_latlon(float(bar[0]), float(bar[2]))
	sphere = SphereShape.create(60, 3)
	sphere.setEffect('colored -e #ff00cc')
	sphere.setPosition(Vector3(float(result[0]), float(result[1]), 5))
f.close()

# Draw TrainLines boundaries


xmldoc = minidom.parse(file2)

itemlist = xmldoc.getElementsByTagName('Placemark')
for node in itemlist:
	r = hex(randint(0,255))[2:]
	g = hex(randint(0,255))[2:]
	b = hex(randint(0,255))[2:]
	trainLine = node.getElementsByTagName('coordinates')
	str = trainLine[0].firstChild.data.encode('ascii', 'ignore')
	str = str.strip()
	coords = str.split(' ')
	firstTime = 1
	trainLine = LineSet.create()
	trainLine.setEffect('colored -e #3000a0aa -t')
	for row in coords:
		first = row.partition(',')
		second = first[2].partition(',')
		result = utm.from_latlon(float(second[0]), float(first[0]))
		if firstTime == 1:
			firstTime = 0
		else:
			l = trainLine.addLine()
			l.setStart(Vector3(oldX, oldY, 10))
			l.setEnd(Vector3(float(result[0]), float(result[1]), 5))
			l.setThickness(100.0)
		oldX = float(result[0])
		oldY = float(result[1])
def updateTrain():
	global trainRoot
	routeID = ['Red', 'Blue', 'Brn', 'G', 'Org', 'P', 'Pink', 'Y']
	trainRoot.setChildrenVisible(False)
	for route in routeID:
		conn = httplib.HTTPConnection('lapi.transitchicago.com')
		conn.request("GET", "/api/1.0/ttpositions.aspx?key=705484f6bc9545de936f7f01ce057123&rt=" + route)
		response = conn.getresponse()
		data = response.read()

		q = minidom.parseString(data)
		trains = q.getElementsByTagName('train')
		for train in trains:
			posX = float(train.getElementsByTagName('lat')[0].firstChild.data.encode('ascii','ignore'))
			posY = float(train.getElementsByTagName('lon')[0].firstChild.data.encode('ascii','ignore'))
			result = utm.from_latlon(posX, posY)
			t = SphereShape.create( 40, 4 )
			t.setPosition(Vector3(float(result[0]), float(result[1]), 0))
			t.setEffect('colored -d #aaaaaa')
			trainRoot.addChild(t)
