from math import *
from euclid import *
from omega import *
from cyclops import *
import sys
sys.path.append('/home/evl/cs526/j_/libs')
import mysql.connector
from mysql.connector import errorcode
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

#skybox = Skybox()
#skybox.loadCubeMap("./Data/sky", "png")
#scene.setSkyBox(skybox)

sceneLayer ={}
sceneLayer.update( {'root': all} )

trainList = {}
trainRoot = SceneNode.create("trainTracking")
all.addChild(trainRoot)
sceneLayer.update( {"trainTracking": trainRoot} )

crimeList = {}
crimeRoot = SceneNode.create("crime")
for i in range(1, 12):
	crimeNode = SceneNode.create("crime" + str(i))
	crimeRoot.addChild( crimeNode )


updateTime = 20

showTrainFlag = False;
showCrimeFlag = False;
showCommunityFlag = True;
CrimeSimulationFlag = False;


appMenu = None;
communityRoot = SceneNode.create("communityRoot")
all.addChild(communityRoot)
communityList = []
activatedCommunity = -1
viewposition = []
mapList = {}

#######################################################################################
#
# Callback Func
#
#######################################################################################

def updateFunc(frame, time, dt):
	global updateTime
	if ( time > updateTime and showTrainFlag ):
		updateTrain()
		print "updateTrain"
		updateTime = time + 20

def onEvent():
	global appMenu
	e = getEvent()
	if(e.getServiceType() == ServiceType.Pointer or e.getServiceType() == ServiceType.Wand or e.getServiceType() == ServiceType.Keyboard):
		# Button mappings are different when using wand or mouse
		confirmButton = EventFlags.Button2
		quitButton = EventFlags.Button1
		if(e.getServiceType() == ServiceType.Wand): 
			confirmButton = EventFlags.Button5
			quitButton = EventFlags.Button3

		if(e.getServiceType() == ServiceType.Keyboard):
			print "key"
		
		# When the confirm button is pressed:
		if(e.isButtonDown(confirmButton)):
			print "confirm1"
			appMenu.getContainer().setPosition(e.getPosition())
			appMenu.show()
		if(e.isButtonDown(quitButton)):
			print "confirm2"
			appMenu.hide()
		
		
			
	
			
def toggleMap(map):
	global mapList
	global appMenu
	appMenu.hide()
	for node in mapList:
		if ( node == map ):
			mapList[node].setVisible(True)
		else:
			mapList[node].setVisible(False)

def switchCommunity(index):
	global viewposition
	global communityRoot
	global activatedCommunity
	global appMenu
	appMenu.hide()
	activatedCommunity = index
	if ( index >= 0 ):
		cam = getDefaultCamera()
		cam.setPosition( viewposition[index] + Vector3(0, 0, 6000) )
		cam.setPitchYawRoll (Vector3(0,0,0))
	else:
		cam = getDefaultCamera()
		cam.setPosition( Vector3(439418.67, 4631157.25, -752.96) + Vector3(0, 0, 40000) )
		cam.setPitchYawRoll (Vector3(0,0,0))		
	
def toggleTrain():
	global showTrainFlag
	global trainRoot
	global appMenu
	appMenu.hide()
	showTrainFlag = not showTrainFlag
	trainRoot.setChildrenVisible(showTrainFlag)

def toggleCrime():
	global showCrimeFlag
	global crimeRoot
	global appMenu
	appMenu.hide()
	showCrimeFlag = not showCrimeFlag
	crimeRoot.setChildrenVisible(showCrimeFlag)

def toggleCommunity():
	global communityRoot
	global showCommunityFlag
	global appMenu
	appMenu.hide()
	showCommunityFlag = not showCommunityFlag
	communityRoot.setChildrenVisible(showCommunityFlag)

#######################################################################################
#
# Set up the scene
#
# GUI shoul be put here too
#
# mapList == dic of available map handler
#
#######################################################################################
def initialize():
	global mapList
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
	light = Light.create()
	light.setColor(Color('white'))
	light.setEnabled(True)

	
def buildGUI():
	global mapList
	global appMenu
	mm = MenuManager.createAndInitialize()
	appMenu = mm.createMenu("contolPanel")
	
	appMenu.addButton("OverView", "switchCommunity(-1)")

	# map toggle
	subMenu = appMenu.addSubMenu('Map')
	first = True
	for map in mapList:
		button = subMenu.addButton(map,"toggleMap('" + map + "')").getButton()
		button.setRadio(True)
		button.setCheckable(True)
		button.setChecked(first)
		first = False
	button = subMenu.addButton('None', "toggleMap('')").getButton()
	button.setRadio(True)
	button.setCheckable(True)
	button.setChecked(False)
	
	# community information
	subMenu = appMenu.addSubMenu('Community')
	col = 6
	containerList = []
	cc = subMenu.getContainer()
	cc.setLayout(ContainerLayout.LayoutHorizontal)
	for i in range(0,col):
		containerList.append(Container.create(ContainerLayout.LayoutVertical,cc))
	index = 0
	prevButton = None
	for com in communityList:
		button = Button.create(containerList[index%6])
		button.setText(com)
		button.setUIEventCommand('switchCommunity(' + str(index) + ')' )
		#button.setCommand('print "' + com + '"')
		#button.setRadio(True)
		#button.setCheckable(True)
		#button.setChecked(True)
		if (index % 6 != 0):
			prevButton.setHorizontalNextWidget(button)
			button.setHorizontalPrevWidget(prevButton)
		prevButton = button
		index+=1
		
	# option
	subMenu = appMenu.addSubMenu("options")
	button1 = subMenu.addButton("updateTrain", "toggleTrain()").getButton()
	button1.setCheckable(True)
	button1.setChecked(False)
	button2 = subMenu.addButton("updateCrime", "toggleCrime()").getButton()
	button2.setCheckable(True)
	button2.setChecked(False)
	button3 = subMenu.addButton("showCommunity", "toggleCommunity()").getButton()
	button3.setCheckable(True)
	button3.setChecked(True)
	
	
	
########################################################################################
#
# Draw the district boundaries
#
# viewposition		== list of center point of each node
# communityList 	== list of the name of each community
#
########################################################################################
def buildCommunity():
	global communityList
	global viewposition
	global communityRoot
	vector = "Data/communities.kml"

	xmldoc = minidom.parse(vector)

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
	index = 0
	itemlist = xmldoc.getElementsByTagName('MultiGeometry') 
	for node in itemlist:
		#r = randint(0,255)
		#g = randint(0,255)
		#b = randint(0,255)
		r = 180
		g = 180
		b = 180
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
				communityRoot.addChild(districtBound)
				communityRoot.addChild(t)
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
	vector = "Data/CTARailLines.kml"
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
def updateCrimeScene(recordList):
	global crimeRoot
	count = 2000
	for record in recordList:
		id = record['id']
		item = crimeList.get(id)
		if (item == None):
			posX = record['x']
			poxY = record['y']
			typ = record['type']
			year = record['year']
			result = utm.from_latlon(posX, poxY)
			cube = BoxShape.create(50,50,20)
			cube.setEffect('colored -d red')
			pos = Vector3(float(result[0]), float(result[1]), 0)
			cube.setPosition(pos)
			crimeRoot.getChildByIndex(year-2001).addChild(cube)
			crimeList.update( {id: cube} )
			count-=1
			if (count == 0) : break
		else:
			item.setVisible(True);

def updateCrimeByYear(year= None):
	if (isMaster()):
		hostAdd = 'localhost'
		#hostAdd = '131.193.79.42'
		try:
			cnx = mysql.connector.connect(user='view', host = hostAdd, database='crime')
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exists")
			else:
				print(err)
		else:
			dataList = []
			cursor = cnx.cursor()
			query = "select latitude, longitude, type, year, id from crimerecord where year = " + str(year)
			cursor.execute(query)
			rows = cursor.fetchall()
			for (x, y, type, year, id) in rows:
				#dataList.append( { 'x': float(x), 'y': float(y), 'type': str(type), 'date': str(date), 'time': str(time), 'id': int(id)} )
				dataList.append( { 'x': float(x), 'y': float(y), 'type': str(type), 'year': int(year), 'id': int(id)} )
			dataStr = json.dumps(dataList)
			broadcastCommand('''updateCrimeScene(''' + dataStr + ''');''')
			cursor.close()
#######################################################################################
#
# Entry Point
#
#######################################################################################
			
if ( __name__ == "__main__"):
	initialize()
	buildCommunity()			
	getStation()
	getRoute()
	buildGUI()
	#updateTrain()
	
	setUpdateFunction(updateFunc)
	setEventFunction(onEvent)
	#print "yes"


	