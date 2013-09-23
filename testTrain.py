from math import *
from euclid import *
from omega import *
from cyclops import *
import sys
import datetime
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
trainNameList = {}
trainRoot = SceneNode.create("trainTracking")
all.addChild(trainRoot)
sceneLayer.update( {"trainTracking": trainRoot} )

updateTrainTime = 20
updateCrimeSimulationTime = 5
updateCrimeTime = 3

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

#crime data
communityCodeMap = {}
crimeList = {}

#communityCrimeRoot = []
yearCrimeRoot = {}
yearChecked = {}
#typeCrimeRoot = {}
crimeRoot = SceneNode.create("crime")
all.addChild(crimeRoot)
yearFilter = "year like 2000"

dataStream = {}

hostAdd = 'localhost'
#hostAdd = '131.193.79.42'

typeFilter = {"ROBBERY": False, "BURGLARY": False, "ASSAULT": False, "HOMICIDE": False}
typeGroup = {"ROBBERY": [], "BURGLARY": [], "ASSAULT": [], "HOMICIDE": []}
#typeFilter = None
crimeDataStr = None

realtimeCrimeList = {}
realtimeCrimeData = []
whitecolor = Color('white')
blackcolor = Color('black')
#######################################################################################
#
# Callback Func
#
#######################################################################################

def updateFunc(frame, time, dt):
	global updateTrainTime
	global updateCrimeTime
	global showTrainFlag
	global showCrimeFlag
	global CrimeSimulationFlag
	global updateCrimeSimulationTime
	if ( time > updateTrainTime and showTrainFlag ):
		updateTrain()
		print "updateTrain"
		updateTrainTime = time + 20
	if ( time >  updateCrimeTime and showCrimeFlag ):
		loadData()
		print "loadingCrime"
		updateCrimeTime = time+3
	if ( time > updateCrimeSimulationTime and CrimeSimulationFlag):
		realtimeUpdate()
		updateCrimeSimulationTime = time + 15

def onDraw(displaySize, tileSize, camera, painter):
	global CrimeSimulationFlag
	global realtimeCrimeData
	global whitecolor
	global blackcolor
	global communityCodeMap
	if (CrimeSimulationFlag == False or realtimeCrimeData == []):
		return 0
	# Get the default font
	font = painter.getDefaultFont()
	accPos = Vector2(10, 10)
	
	#print "oh"
	for q in realtimeCrimeData:
	# Set some text and compute its width and height in pixels (given the font we cant to use)
		comm = communityCodeMap.get(str(q['community']) )
		if (comm != None):
			text = "type " + (str(q['type'])) + " " + (str(q['id'])) + "  time: " + (str(q['time']) ) +"  "+ (str(comm))
		else:
			text = "type " + (str(q['type'])) + " " + (str(q['id'])) + "  time: " + (str(q['time']) ) + "  Community_Code" + (str(q['community']) )
		textSize = font.computeSize(text)
		# Draw a white box and put the text inside it
		painter.drawRect(accPos, textSize + Vector2(10, 10), whitecolor)
		painter.drawText(text, font, accPos + Vector2(5, 5 ), TextAlign.HALeft | TextAlign.VATop, blackcolor)
		accPos += Vector2(0, textSize.y+12)

def onEvent():
	global appMenu
	cam = getDefaultCamera()
	e = getEvent()
	type = e.getServiceType()
	if(type == ServiceType.Pointer or type == ServiceType.Wand or type == ServiceType.Keyboard):
		# Button mappings are different when using wand or mouse
		confirmButton = EventFlags.Button2
		quitButton = EventFlags.Button1

		lowHigh = 0
		leftRight = 0
		if(type == ServiceType.Keyboard):
			forward = ord('w')
			down = ord('s')
			left = ord ('a')
			right = ord('d')
			low = ord('i')
			high = ord('k')
			turnleft = ord('j')
			turnright = ord('l')
			climb = ord('r')
			descend = ord('f')
			if(e.isKeyDown( low)):
				lowHigh = 0.5
			if(e.isKeyDown( high )):
				lowHigh = -0.5
			if(e.isKeyDown( turnleft)):
				leftRight = 0.5
			if(e.isKeyDown( turnright )):
				leftRight = -0.5				
			if(e.isKeyDown( forward)):
				cam.translate(0, 0, -500, Space.Local )
			if(e.isKeyDown( down )):
				cam.translate(0, 0, 500, Space.Local )
			if(e.isKeyDown( left)):
				cam.translate(-500, 0, 0, Space.Local )
			if(e.isKeyDown( right )):
				cam.translate(500, 0, 0, Space.Local )
			if(e.isKeyDown( climb)):
				cam.translate(0, 500, 0, Space.Local )
			if(e.isKeyDown( descend )):
				cam.translate(0, -500, 0, Space.Local )
		
		if(type == ServiceType.Wand): 
			confirmButton = EventFlags.Button5
			quitButton = EventFlags.Button3
			forward = EventFlags.ButtonUp
			down = EventFlags.ButtonDown
			left = EventFlags.ButtonLeft
			right = EventFlags.ButtonRight
			climb = EventFlags.Button5
			descend = EventFlags.Button7
			lowHigh = e.getAxis(0)
			leftRight = e.getAxis(1)
			if(e.isButtonDown( forward)):
				cam.translate(0, 0, -500, Space.Local )
			if(e.isButtonDown( down )):
				cam.translate(0, 0, 500, Space.Local )
			if(e.isButtonDown( left)):
				cam.translate(-500, 0, 0, Space.Local )
			if(e.isButtonDown( right )):
				cam.translate(500, 0, 0, Space.Local )
			if(e.isButtonDown( climb)):
				cam.translate(0, 500, 0, Space.Local )
			if(e.isButtonDown( descend )):
				cam.translate(0, -500, 0, Space.Local )
	
		cam.rotate(Vector3(1,0,0), -lowHigh, Space.Local)
		cam.rotate(Vector3(0,0,1), leftRight, Space.Local)
				
		# When the confirm button is pressed:
		if(e.isButtonDown(confirmButton)):
			appMenu.getContainer().setPosition(e.getPosition())
			appMenu.show()
		if(e.isButtonDown(quitButton)):
			appMenu.hide()
		e.setProcessed()

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

def toggleUpdateCrime():
	global showCrimeFlag
	global crimeRoot
	global appMenu
	appMenu.hide()
	showCrimeFlag = not showCrimeFlag

def toggleShowCrime(year):
	global yearCrimeRoot
	global yearChecked
	global yearFilter
	yearCrimeRoot[year].setChildrenVisible(yearChecked[year])
	yearChecked[year] = not yearChecked[year]
	yearFilter = yearFilter.replace(' or year like '+ str(year),'')
	if (yearChecked[year] == True):
		yearFilter += ' or year like '
		yearFilter += str(year)

def toggleShowCrimeType(type):
	global typeFilter
	global typeGroup
	typeFilter[type] = not typeFilter[type]
	for item in typeGroup[type]:
		item.setVisibility = typeFilter[type]
		

def toggleCommunity():
	global communityRoot
	global showCommunityFlag
	global appMenu
	appMenu.hide()
	showCommunityFlag = not showCommunityFlag
	communityRoot.setChildrenVisible(showCommunityFlag)

def realTimeCrime():
	global showCrimeFlag
	global CrimeSimulationFlag
	global crimeList
	CrimeSimulationFlag = not CrimeSimulationFlag
	if (CrimeSimulationFlag):
		for key in crimeList:
			crimeList[key].setVisible(False)
		showCrimeFlag = False

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
	global yearCrimeRoot
	global yearChecked
	global typeCrimeRoot
	global crimeRoot
	global dataStream
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
	cam.setControllerEnabled(False)
	#set up the scene
	light = Light.create()
	light.setColor(Color('white'))
	light.setLightType(LightType.Directional)
	light.setLightDirection(Vector3(0,0, 20))
	light.setEnabled(True)
	
	#load community code => name
	for i in range(1, 13):
		yearCrimeRoot[2000+i] = SceneNode.create("crime20" + str(i))
		crimeRoot.addChild( yearCrimeRoot[2000+i] )
		yearChecked[2000+i] = False
		dataStream.update({ (2000+i): None})
	#for q in ('ROBBERY', 'BURGLARY', 'ASSAULT', 'HOMICIDE'):
	#	typeCrimeRoot[q] = SceneNode.create(q+"Root")
	#	crimeRoot.addChild( typeCrimeRoot[q] )
	
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
	button2 = subMenu.addButton("updateCrime", "toggleUpdateCrime()").getButton()
	button2.setCheckable(True)
	button2.setChecked(False)
	button3 = subMenu.addButton("showCommunity", "toggleCommunity()").getButton()
	button3.setCheckable(True)
	button3.setChecked(True)

	subMenu = appMenu.addSubMenu("filterCrime")
	for integer in range (2001,2012):
		button = subMenu.addButton("Filter Crime Year " + str(integer), "toggleShowCrime(" + str(integer) + ")").getButton()
		button.setCheckable(True)
		button.setChecked(False)
	
	for type in ( 'ROBBERY', 'BURGLARY', 'ASSAULT', 'HOMICIDE'):
		button = subMenu.addButton("Filter Crime Type" + str(type), "toggleShowCrimeType('" + str(type) + "')").getButton()
		button.setCheckable(True)
		button.setChecked(False)
	
	button = subMenu.addButton("reset Crime Update", 'updateCrime()')
	
	#button = appMenu.addButton("real-time Hero play", 'realTimeCrime(); button2.setChecked(False);').getButton()
	button = appMenu.addButton("real-time Hero play", 'realTimeCrime()').getButton()
	button.setCheckable(True)
	button.setChecked(False)
	button.setChecked(False)
	
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
	global communityCodeMap
	vector = "Data/crime/communityCode.csv"
	f = open(vector)
	comMap = [line.rstrip('\n') for line in f]

	for line in comMap:
		bar = line.split(',')
		p1 = bar[0].strip(' ')
		p2 = bar[1].strip(' ')
		communityCodeMap.update({p1 : p2})
	f.close()
	
	
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
		cube = BoxShape.create(80,80,40)
		cube.setEffect('colored -d #e67e22')
		pos = Vector3(float(result[0]), float(result[1]), 0)
		cube.setPosition(pos)
		t = Text3D.create('fonts/arial.ttf', 100, bar[0])
		t.setPosition( Vector3(0,0,100) + pos)
		t.setColor(Color('#e74c3c'))
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
		trainName = trainNameList.get(record['id'])
		if ( train == None):
			sphere = SphereShape.create(30, 4)
			sphere.setPosition(record['x'], record['y'], record['z'])
			sphere.setEffect("colored -d " + record['color'])
			t = Text3D.create('fonts/arial.ttf', 100, str(int(record['id'])))
			t.setPosition(record['x'], record['y'], record['z']+50)
			t.setColor(Color(record['color']))
			trainList.update({ record['id']: sphere })
			trainNameList.update({ record['id']: t })
			trainRoot.addChild(sphere)
			trainRoot.addChild(t)
		else:
			train.setPosition(record['x'], record['y'], record['z'])
			trainName.setPosition(record['x'], record['y'], record['z']+50)
			train.setVisible(True)
			trainName.setVisible(True)
			
			
#######################################################################################
#
# Crime
#
#######################################################################################
def updateCrimeScene(recordList, para):
	global crimeDataStr
	global dataStream
	crimeDataStr += recordList
	for i in range (2001, 2013):
		if str(i) in para: 
			if (dataStream[i] == None or len(dataStream[i] > len(recordList))):
				dataStream[i] = recordList
	
def loadData():
	global crimeDataStr
	global crimeList
	global typeFilter
	global typeGroup
	if (crimeDataStr == None):
		return 0
	#global crimeRoot
	global yearCrimeRoot
	#global typeCrimeRoot
	count = 300
	for record in crimeDataStr:
		id = record['id']
		item = crimeList.get(id)
		type = record['type']
		if (item == None):
			posX = record['x']
			poxY = record['y']
			year = record['year']
			result = utm.from_latlon(posX, poxY)
			cube = PlaneShape.create(50,50)
			if ( type == "ROBBERY"):
				cube.setEffect('colored -d green')
			if ( type == "BURGLARY"):
				cube.setEffect('colored -d yellow')
			if ( type == "ASSAULT"):
				cube.setEffect('colored -d blue')
			if ( type == "HOMICIDE"):
				cube.setEffect('colored -d red')
			pos = Vector3(float(result[0]), float(result[1]), 1)
			cube.setPosition(pos)
			yearCrimeRoot[year].addChild(cube)
			#typeCrimeRoot[type].addChild(cube)
			crimeList.update( {id: cube} )
			typeGroup[type].append(cube)
			count-=1
			if (count == 0) : break
			item = cube
		item.setVisible(typeFilter[type]);
		
			
def updateCrime(year= None, type= None, community= None):
	if (isMaster()):
		global crimeDataStr
		global yearFilter
		crimeDataStr = []
		global hostAdd
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
			if (year== None): searchYear = yearFilter
			if (type== None): type = '%'
			if (community== None): community = '%'
			for i in range (2001, 2013):
				if (dataStream[i] != None):
					searchYear = searchYear.replace (' or year like '+ str(i),'')
					crimeDataStr += dataStream[i]
			#query = "select latitude, longitude, type, year, id from crimerecord where year like " + str(year) + " AND type like '" + str(type) + "' AND community like '" +str(community) + "';"
			query = "select latitude, longitude, type, year, id from crimerecord where " + str(searchYear) + " AND type like '" + str(type) + "' AND community like '" +str(community) + "';"
			print query
			cursor.execute(query)
			rows = cursor.fetchall()
			for (x, y, type, year, id) in rows:
				#dataList.append( { 'x': float(x), 'y': float(y), 'type': str(type), 'date': str(date), 'time': str(time), 'id': int(id)} )
				dataList.append( { 'x': float(x), 'y': float(y), 'type': str(type), 'year': int(year), 'id': int(id)} )
			dataStr = json.dumps(dataList)
			broadcastCommand('updateCrimeScene(' + dataStr + ',"' + str(searchYear) + '",);')
			cursor.close()

def realtimeUpdate ( ):
	if (isMaster()):
		global hostAdd
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
			date = str( datetime.datetime.now().date() )
			date = list(date)
			date[3] = '%'
			date = ''.join(date)
			
			time = datetime.datetime.now()
			starttime = (str((time - datetime.timedelta(seconds=900)).time()))[:8]
			time = (str(time.time()))[:8]
			
			query = ("select latitude, longitude, type, year, time, id, community from crimerecord where " 
			"date like '" + date + "' and time between '"+ starttime +"' and '"+ time +"'")
			print query
			cursor.execute(query)
			rows = cursor.fetchall()
			for (x, y, type, year, time, id, community) in rows:
				#dataList.append( { 'x': float(x), 'y': float(y), 'type': str(type), 'date': str(date), 'time': str(time), 'id': int(id)} )
				dataList.append( { 'x': float(x), 'y': float(y), 'type': str(type), 'year': int(year), 'id': int(id), 'time': str(time), 'community': str(community)} )
			dataStr = json.dumps(dataList)
			broadcastCommand('realTime(' + dataStr + ')')
			cursor.close()
			
def realTime(str):
	global crimeList
	global realtimeCrimeList
	global typeGroup
	global yearCrimeRoot
	global realtimeCrimeData
	#global typeFilter
	if (str == []):
		return 0
	for record in realtimeCrimeList:
		realtimeCrimeList[record].setVisible(False)
	realtimeCrimeData = []
	realtimeCrimeList = {}
	for record in str:
		id = record['id']
		item = crimeList.get(id)
		type = record['type']
		realtimeCrimeData.append(record)
		if (item == None):
			posX = record['x']
			poxY = record['y']
			year = record['year']
			result = utm.from_latlon(posX, poxY)
			cube = PlaneShape.create(50,50)
			if ( type == "ROBBERY"):
				cube.setEffect('colored -d green')
			if ( type == "BURGLARY"):
				cube.setEffect('colored -d yellow')
			if ( type == "ASSAULT"):
				cube.setEffect('colored -d blue')
			if ( type == "HOMICIDE"):
				cube.setEffect('colored -d red')
			pos = Vector3(float(result[0]), float(result[1]), 1)
			cube.setPosition(pos)
			yearCrimeRoot[year].addChild(cube)
			#typeCrimeRoot[type].addChild(cube)
			crimeList.update( {id: cube} )
			realtimeCrimeList.update( {id: cube} )
			typeGroup[type].append(cube)
			item = cube
		#item.setVisible(typeFilter[type])
		item.setVisible(True)
	
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
	setDrawFunction(onDraw)
	#print "yes"


	