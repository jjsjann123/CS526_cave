from xml.dom import minidom

vector = "C:\\AJ\\omegalib\\apps\\data\\communities.xml"

xmldoc = minidom.parse(vector)
itemlist = xmldoc.getElementsByTagName('MultiGeometry') 

i = 0
for node in itemlist:
	print i
	i += 1
	



#q = itemlist[0].firstChild.nodeValue