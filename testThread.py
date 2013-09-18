import mysql.connector
import threading
import time

cnx = mysql.connector.connect(user='viewer', database='topgun_report')

def update(cnx):
	while (True):
		cursor = cnx.cursor()
		query = ("select name from capsulorrhexis")
		cursor.execute(query)
		for name in cursor:
			print name

		print "finished"
		cursor.close()
		time.sleep(1)
#q = threading.Timer(3.0, target = update, args = (cnx,))
q = threading.Timer(3.0, update, args = (cnx,))
q.start()

def onUpdate(frame, time, dt):
	x = frame
	print x
	
setUpdateFunction(onUpdate)