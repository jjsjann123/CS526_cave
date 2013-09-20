import sys
sys.path.append('/home/evl/cs526/j_/libs')
import mysql.connector
from mysql.connector import errorcode
#hostAdd = raw_input()

if (isMaster()):
	hostAdd = 'localhost'
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
		cursor = cnx.cursor()
		query = ("select -20")
		cursor.execute(query)
		for name in cursor:
				
				if (isMaster()):
					broadcastCommand('''SphereShape.create(1,4).setPosition( Vector3(0, 0, ''' + str(name[0]) + '''));''')
			

		print "finished"
		cursor.close()
	#q = threading.Timer(3.0, target = update, args = (cnx,))