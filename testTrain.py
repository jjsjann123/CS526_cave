from math import *
from euclid import *
from omega import *
from cyclops import *

from xml.dom import minidom
import utm
import re
import httplib
import json
from random import randint

#######################################################################################
#
# Global variables
#
#######################################################################################

scene = getSceneManager()
all = SceneNode.create("everything")

sceneLayer ={}
sceneLayer.update( {'root': all} )

trainList = {}
trainRoot = SceneNode.create("trainTracking")
all.addChild(trainRoot)
sceneLayer.update( {"trainTracking": trainRoot} )

updateTime = 20

showTrainFlag = True;
showRouteFlag = True;
showStationFlag = True;
showMapFlag = 0;
showCrimeFlag = True;
CrimeSimulationFlag = False;

#######################################################################################
#
# Callback Func
#
#######################################################################################

def updateFunc(frame, time, dt):
	global updateTime
	if ( time > updateTime ):
		updateTrain()
		print "updateTrain"
		updateTime = time + 20
		
#######################################################################################
#
# Set up the scene
#
# GUI shoul be put here too
#
#######################################################################################
def initialize():
	setNearFarZ(1, 2 * 23227.75)
	#deal with the camera
	cam = getDefaultCamera()
	cam.setPosition(Vector3(439418.67, 4631157.25, -752.96) + Vector3(7768.82, 2281.18, 2034.08))
	#cam.setPosition(city1.getBoundCenter() )
	cam.getController().setSpeed(2000)
	cam.pitch(3.14159*0.45) #pitch up to start off flying over the city
	#set up the scene

	light = Light.create()
	light.setColor(Color('white'))
	light.setEnabled(True)

########################################################################################
#
# Draw the district boundaries
#
# viewposition		== list of center point of each node
# communityList 	== list of the name of each community
#
########################################################################################
def buildCommunity():
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
def getStation():
	f = open('Data/CTA_Stops.csv')
	ctastops = [line.rstrip('\n') for line in f]
	stationRoot = SceneNode.create("TrainStation")
	stationLabel = SceneNode.create('TrainStationLabel')
	all.addChild(stationRoot)
	stationRoot.addChild(stationLabel)
	sceneLayer.update({ 'stationRoot' : stationRoot, 'stationLabel' : stationLabel })
	for name in ctastops:
		#print name
		if (name == ''): continue
		bar = name.split(',')
		result = utm.from_latlon(float(bar[1]), float(bar[2]))
		cube = BoxShape.create(50,50,20)
		cube.setEffect('colored -d #ff00cc')
		pos = Vector3(float(result[0]), float(result[1]), 0)
		cube.setPosition(pos)
		t = Text3D.create('fonts/arial.ttf', 100, bar[0])
		t.setPosition( Vector3(0,0,100) + pos)
		t.setColor(Color('#dd0033'))
		stationRoot.addChild(cube)
		stationLabel.addChild(t)
	f.close()

def getRoute():
	# Draw TrainLines
	vector = ".\\data\\CTARailLines.kml"
	#	colorMap{ 'Brown' : Color(139/255.0, 69/255.0, 19/255.0), 'Red' : Color('red'), 'Purple' : Color('purple'), 'Blue' : Color('blue'), 'Green': Color('green'), 'Orange': Color('orange') }

	xmldoc = minidom.parse(vector)

	itemlist = xmldoc.getElementsByTagName('Placemark')
	for node in itemlist:
		trainLine = node.getElementsByTagName('coordinates')
		str = trainLine[0].firstChild.data.encode('ascii', 'ignore')
		str = str.strip()
		coords = str.split(' ')
		firstTime = 1
		route = node.getElementsByTagName('name')
		route = route[0].firstChild.data.encode('ascii','ignore').partition(',')[0].partition(' ')[0].lower()
		if (route == 'pink'): route = '#ff1493'
		if (route == 'brown'): route = '#8b4513'
		trainLine = LineSet.create()
		trainLine.setEffect('colored -d ' + route)
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
				l.setThickness(20.0)
			oldX = float(result[0])
			oldY = float(result[1])

def updateTrain():
	if (isMaster()):
		routeID = ['Red', 'Blue', 'Brn', 'G', 'Org', 'P', 'Pink', 'Y']
		trainColor = { 'Red': 'red', 'Blue': 'blue', 'Brn': '#8b4513', 'G': 'green', 'Org': 'orange', 'P': '#ff1493', 'Pink': '#ff1493', 'Y': 'yellow' }
		data = []
		for route in routeID:
			conn = httplib.HTTPConnection('lapi.transitchicago.com')
			conn.request("GET", "/api/1.0/ttpositions.aspx?key=705484f6bc9545de936f7f01ce057123&rt=" + route)
			response = conn.getresponse()
			xml = response.read()

			q = minidom.parseString(xml)
			trains = q.getElementsByTagName('train')
			
			for train in trains:
				posX = float(train.getElementsByTagName('lat')[0].firstChild.data.encode('ascii','ignore'))
				posY = float(train.getElementsByTagName('lon')[0].firstChild.data.encode('ascii','ignore'))
				rn = float(train.getElementsByTagName('rn')[0].firstChild.data.encode('ascii','ignore'))
				result = utm.from_latlon(posX, posY)
				data.append({ 'id': rn, 'x': float(result[0]), 'y': float(result[1]), 'z': 0.0, 'color': trainColor[route]})
		data_str = json.dumps(data)
		broadcastCommand( 'moveTrain(' + data_str + ')')
def moveTrain(json_str):
	global trainRoot
	global trainList
	trainRoot.setChildrenVisible(False)
	for record in json_str:
		train = trainList.get(record['id'])
		if ( train == None):
			sphere = SphereShape.create(30, 4)
			sphere.setPosition(record['x'], record['y'], record['z'])
			sphere.setEffect("colored -d " + record['color'])
			trainList.update({ record['id']: sphere })
			trainRoot.addChild(sphere)
		else:
			train.setPosition(record['x'], record['y'], record['z'])
			train.setVisible(True)
			
			
#######################################################################################
#
# Crime
#
#######################################################################################

#######################################################################################
#
# Entry Point
#
#######################################################################################
			
if (__	name__ == "__main__"):
	initialize()
	buildCommunity()			
	getStation()
	getRoute()
	updateTrain()
	setUpdateFunction(updateFunc)