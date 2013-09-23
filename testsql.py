import sys
sys.path.append('/home/evl/cs526/j_/libs')
import mysql.connector
from mysql.connector import errorcode
import json
import utm
crimeList = {}
crimeRoot = SceneNode.create("crime")
for i in range(1, 12):
	crimeNode = SceneNode.create("crime" + str(i))
	crimeRoot.addChild( crimeNode )



setNearFarZ(1, 2 * 23227.75)
#deal with the camera
cam = getDefaultCamera()
cam.setPosition(Vector3(439418.67, 4631157.25, -752.96) + Vector3(7768.82, 2281.18, 2034.08))
#cam.setPosition(city1.getBoundCenter() )
cam.getController().setSpeed(2000)
cam.pitch(3.14159*0.45) #pitch up to start off flying over the city
#set up the scene

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