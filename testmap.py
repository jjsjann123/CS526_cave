#from xml.dom import minidom

#vector = "C:\\AJ\\omegalib\\apps\\data\\vectorQuery.xml"

#xmldoc = minidom.parse(vector)
#itemlist = xmldoc.getElementsByTagName('gml:coordinates') 
#q = itemlist[0].firstChild.nodeValue
from math import *
from euclid import *
from omega import *
from cyclops import *

from xml.dom import minidom
import utm
import re

file1 = ".\\data\\CTARailLines.kml"

# Draw TrainLines boundaries
xmldoc = minidom.parse(file1)

itemlist = xmldoc.getElementsByTagName('Placemark')
for node in itemlist:
	trainLine = node.getElementsByTagName('coordinates')
	str = trainLine[0].firstChild.data.encode('ascii', 'ignore')
	str = str.strip()
	coords = str.split(' ')
	firstTime = 1
	trainLine = LineSet.create()
	trainLine.setEffect('colored -e #44dd44')
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
			l.setThickness(50.0)
		oldX = float(result[0])
		oldY = float(result[1])		

#Add a random color for boundaries
#Add text for district view
