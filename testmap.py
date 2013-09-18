#from xml.dom import minidom

#vector = "C:\\AJ\\omegalib\\apps\\data\\vectorQuery.xml"

#xmldoc = minidom.parse(vector)
#itemlist = xmldoc.getElementsByTagName('gml:coordinates') 
#q = itemlist[0].firstChild.nodeValue
from math import *
from euclid import *
from omega import *
from cyclops import *

# Draw the community boundaries
oldX = 0
oldY = 0
firstTime = True
districtBound = LineSet.create()
districtBound.setEffect('colored -d blue')

f = open('..\\data\\boundaries')
boundaries = [row.rstrip('\n') for row in f]
count = 10
for pos in boundaries:
	xy = pos.partition(',')
	result = utm.from_latlon(float(xy[2]), float(xy[0]))
	if firstTime == True:
		firstTime = False
		oldX = float(result[0])
		oldY = float(result[1])
	elif ( abs(Vector2(oldX, oldY) - Vector2( float(result[0]),float(result[1])) ) <= 20 ):
		print "no"
	else:
			l = districtBound.addLine()
			l.setStart(Vector3(oldX, oldY, 10))
			l.setEnd(Vector3(float(result[0]), float(result[1]), 10))
			l.setThickness(20.0)
			oldX = float(result[0])
			oldY = float(result[1])
#firstTime = 1
#districtBound = LineSet.create()
#districtBound.setEffect('colored -d blue')
#f = open('..\\data\\boundaries')
#boundaries = [row.rstrip('\n') for row in f]
#posArray = []
#for pos in boundaries:
#	xy = pos.partition(',')
#	result = utm.from_latlon(float(xy[2]), float(xy[0]))
#	if firstTime == 1:
#		firstTime = 0
#	else:
#		l = districtBound.addLine()
#		l.setStart(Vector3(oldX, oldY, 10))
#		l.setEnd(Vector3(float(result[0]), float(result[1]), 10))
#		l.setThickness(80.0)
#	oldX = float(result[0])
#	oldY = float(result[1])

#f.close()
#all.addChild(boundaries)
