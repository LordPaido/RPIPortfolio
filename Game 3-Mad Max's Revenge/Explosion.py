from pandac.PandaModules import *
from direct.task.Task import Task
from pandac.PandaModules import PointLight, AmbientLight



expTexs = [loader.loadTexture(("Assets/Images/explosion/explosion%0"+str(4)+"d.png") % i) for i in range(51)]

class Explosion():
    
    def __init__(self, pos, render):

        #load plane
        self.expPlane = loader.loadModelCopy('Assets/Models/plane')  #load the object
        self.expPlane.reparentTo(render)                      #reparent to render
        self.expPlane.setPos(pos)                             #set the position, relative to render
        self.expPlane.setTransparency(1)                      #enable transparency
        
        #Add task to increment
        self.expTask = taskMgr.add(self.playSprite, "explosionTask")
        self.expTask.fps = 30                                 #set framerate
        self.expTask.obj = self.expPlane                      #set object
        self.expTask.textures = expTexs                  #set texture list
        
        self.expPlane.node().setEffect(BillboardEffect.makePointEye())
        
        
        #Setup light
        self.redPointLight = self.expPlane.attachNewNode( AmbientLight( "flame" ) )
        self.redPointLight.setPos(3,3,3)
        self.redPointLight.node().setColor( Vec4( 1.0, 1.0, 1.0, 0 ) )
        #self.redPointLight.node().setAttenuation( Vec3( .1, 0.1, 0.0 ) ) 
        self.expPlane.setLight(self.redPointLight)
        
   
        
    def playSprite(self, task):
        """Play the sprite movie"""
    
        currentFrame = int(task.time * task.fps)
        task.obj.setTexture(task.textures[currentFrame % len(task.textures)], 1)
        
        #end sprite
        if currentFrame >= 50:
            self.kill_sprite()
            self.expPlane.removeNode()
            return Task.done
        
        return Task.cont
        
        
    def kill_sprite(self):
        """turn off light"""
        
        self.expPlane.clearLight(self.redPointLight)
        self.redPointLight.remove()
        return