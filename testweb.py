import httplib
from xml.dom import minidom
import utm

trainRoot = SceneNode.create('trains')
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