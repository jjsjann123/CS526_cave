import sys
sys.path.append('/home/evl/cs526/j_/libs')
import mysql.connector
#hostAdd = raw_input()


hostAdd = '131.193.79.42'
cnx = mysql.connector.connect(user='view', host = hostAdd, database='crime')

cursor = cnx.cursor()
query = ("select -20")
cursor.execute(query)
for name in cursor:
		
		if (isMaster()):
			broadcastCommand('''SphereShape.create(1,4).setPosition( Vector3(0, 0, ''' + str(name[0]) + '''));''')
		

print "finished"
cursor.close()
#q = threading.Timer(3.0, target = update, args = (cnx,))