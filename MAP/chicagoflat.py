###############################################################
#
# Sample code for CS 526 Fall 2013
# Copyright 2013 by Andrew Johnson, evl, uic
#
# example code integrating osgearth and omegalib
# and overlaying data onto a flat map of the chicago area
#
###############################################################

from math import *
from euclid import *
from omega import *
from cyclops import *

# makes use of python utm converter from https://pypi.python.org/pypi/utm
import utm

# deal with audio
env = getSoundEnvironment()
s_sound = env.loadSoundFromFile("beep", "/menu_sounds/menu_select.wav")

scene = getSceneManager()

mi = ModelInfo()
mi.name = "defaultSphere"
mi.path = "sphere.obj"
scene.loadModel(mi)

# set background to black
scene.setBackgroundColor(Color(0, 0, 0, 1))

# Create a directional light                                                        
light1 = Light.create()
light1.setLightType(LightType.Directional)
light1.setLightDirection(Vector3(-1.0, -1.0, -1.0))
light1.setColor(Color(0.5, 0.5, 0.5, 1.0))
light1.setAmbient(Color(0.2, 0.2, 0.2, 1.0))

light1.setEnabled(True)
# Load a static osgearth 'model'
cityModel1 = ModelInfo()
cityModel1.name = "city1"
cityModel1.path = "chicago_yahoo.earth"
scene.loadModel(cityModel1)

# Create a scene object using the loaded model
city1 = StaticObject.create("city1")
city1.getMaterial().setLit(False)

setNearFarZ(1, 2 * city1.getBoundRadius())
#setNearFarZ(1, 0.2 * city1.getBoundRadius())

# add another version with a different type of map
cityModel2 = ModelInfo()
cityModel2.name = "city2"
cityModel2.path = "chicago_flat.map.earth"
#cityModel2.path = "chicago_yahoo.earth"
scene.loadModel(cityModel2)

# Create a scene object using the second loaded model
city2 = StaticObject.create("city2")
city2.getMaterial().setLit(False)

#deal with the camera
cam = getDefaultCamera()
cam.setPosition(city1.getBoundCenter() + Vector3(7768.82, 2281.18, 2034.08))
#cam.setPosition(city1.getBoundCenter() )
cam.getController().setSpeed(2000)
cam.pitch(3.14159*0.45) #pitch up to start off flying over the city

#set up the scene
all = SceneNode.create("everything")
all.addChild(city1)
all.addChild(city2)

#turn off one of the two maps
city1.setVisible(False)

#add some data in lat lon format onto the UTM based map
# chicago is in UTM Zone 16

# first the set of L stops

f = open('CTA_L_Stops')
ctastops = [line.rstrip('\n') for line in f]

for name in ctastops:
	#print name
	foo = name.strip(' ()"')
	bar = foo.partition(', ')
	print bar[0], bar[2]
	result = utm.from_latlon(float(bar[0]), float(bar[2]))
	model = StaticObject.create("defaultSphere")
	model.setScale(Vector3(100, 100, 100))                                                   
	model.setPosition(Vector3(float(result[0]), float(result[1]), 0))
	model.setEffect('colored -d red')  
	all.addChild(model)
f.close()

# and now one of the L segments

oldX = 0
oldY = 0
firstTime = 1
blueLine = LineSet.create()
blueLine.setEffect('colored -d blue')
f = open('LINE')
ctaline = [line.rstrip('\n') for line in f]
for row in ctaline:
	first = row.partition(',')
	second = first[2].partition(',') 
	result = utm.from_latlon(float(second[0]), float(first[0]))
	if firstTime == 1: 
		firstTime = 0
	else: 
		l = blueLine.addLine()
		l.setStart(Vector3(oldX, oldY, 10))
		l.setEnd(Vector3(float(result[0]), float(result[1]), 10))
		l.setThickness(20.0)
	oldX = float(result[0])
	oldY = float(result[1])
f.close
all.addChild(blueLine)

#handle events from the wand
# left and right buttons shift between the two maps

def handleEvent():
    global userScaleFactor

    e = getEvent()
    if(e.isButtonDown(EventFlags.ButtonLeft)):
        print("Left button pressed")
	city1.setVisible(False)
	city2.setVisible(True)

	#play button sound
	si_sound = SoundInstance(s_sound)
	si_sound.setPosition( e.getPosition() )
	si_sound.setVolume(1.0)
	si_sound.setWidth(20)
	si_sound.play()

    if(e.isButtonDown(EventFlags.ButtonRight)):
        print("Right button pressed")
	city2.setVisible(False)
	city1.setVisible(True)

	#play button sound
	si_sound = SoundInstance(s_sound)
	si_sound.setPosition( e.getPosition() )
	si_sound.setVolume(1.0)
	si_sound.setWidth(20)
	si_sound.play()

# by default user can use the joystick to spin the world and fly
# but a better flying model should be added in

# Draw the community boundaries
oldX = 0
oldY = 0
firstTime = True
districtBound = LineSet.create()
districtBound.setEffect('colored -d blue')

f = open('..\\data\\boundaries')
boundaries = [row.rstrip('\n') for row in f]
posArray = []
count = 10
for pos in boundaries:
	xy = pos.partition(',')
	result = utm.from_latlon(float(xy[2]), float(xy[0]))
	if firstTime == True:
		firstTime = False
		oldX = float(result[0])
		oldY = float(result[1])
#	elif count <= 2:
#		count = count + 1
	elif ( abs(Vector2(oldX, oldY) - Vector2( float(result[0]),float(result[1])) ) <= 20 ):
		print "no"
	else:
			l = districtBound.addLine()
			l.setStart(Vector3(oldX, oldY, 10))
			l.setEnd(Vector3(float(result[0]), float(result[1]), 10))
			l.setThickness(20.0)
			oldX = float(result[0])
			oldY = float(result[1])
	posArray.append(Vector2(oldX, oldY));

f.close()


