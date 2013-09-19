sphere = SphereShape.create(1,4)
sphere2 = SphereShape.create(1,4)
sphere2.setPosition(Vector3(5,0,0))

cam = getDefaultCamera()
cam.setPosition( Vector3(0, 0, 40))

root = SceneNode.create('train')