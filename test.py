from math import *

global left #= False

left = False

def toggleCamera():
	camera.setPosition(-5, 0, 0)
	#
	
scene = getSceneManager()

camera = getDefaultCamera()
print camera.getCameraId()

mm = MenuManager.createAndInitialize()
appMenu = mm.createMenu("contolPanel")

appMenu.addButton("toggle", "toggleCamera()")
appMenu.addButton("toggle2", "toggleCamera()")
appMenu.addButton("toggle3", "toggleCamera()")

#camera = getOrCreateCamera("top")
#camera.setPosition(Vector3(0, 20, 0))
#camera.setPitchYawRoll(Vector3(-3.14/180*90,0, 0))

sphere1 = SphereShape.create(1,4)
sphere1.setPosition ( Vector3( 5, 0, -20 ))
sphere1.setEffect("colored -d green")

sphere2 = SphereShape.create(1,4)
sphere2.setPosition ( Vector3( -5, 0, -20 ))
sphere2.setEffect("colored -d red")

light = Light.create()
light.setPosition( Vector3(0, 0, -20))
light.setEnabled( True)

# Animate the model
def onUpdate():
	e = getEvent()
	type = e.getServiceType()
	if ( type == ServiceType.Keyboard ):
		if ( e.isKeyDown(ord('x'))):
			camera.setPosition(-5, 0, 0)
		if ( e.isKeyDown(ord('z'))):
			camera.setPosition(5, 0, 0)
	if ( type == ServiceType.Pointer ):
		#if (e.getType() == EventFlags.Down)
		print "down"
		#print "Keyboard"
		#camera.setPosition( Vector3( -5, 0, 0))
		#camera.setPosition( Vector3( 5, 0, 0))
	#elif (e.isKeyDown('b')):
	#	print "b is pressed"
	
#--------------------------------------------------------------------------------------------------
def onEvent():
	e = getEvent()
	print e
	if(e.getServiceType() == ServiceType.Pointer or e.getServiceType() == ServiceType.Wand):
		# Button mappings are different when using wand or mouse
		print "button"
		confirmButton = EventFlags.Button2
		if(e.getServiceType() == ServiceType.Wand): confirmButton = EventFlags.Button5

		# When the confirm button is pressed:
		if(e.isButtonDown(confirmButton)):
			print "confirm1"
			camera.setPosition(-5, 0, 0)
			appMenu.getContainer().setPosition(e.getPosition())
			appMenu.show()
		if(e.isButtonDown(EventFlags.Button1)):
			print "confirm2"
			camera.setPosition(5, 0, 0)
		
	

setEventFunction(onEvent)