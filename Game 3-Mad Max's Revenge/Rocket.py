from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import PointLight
import math

#Only fire one rocket at a time!
class Rocket():
    def __init__(self, pos, direction, source, render):
        direction.normalize()
        self.source = source
    
        #Calculate direction
        dist = 200
        dx = dist * direction.getX()
        dy = dist * direction.getY()
        dz = dist * direction.getZ()
        dest = Point3(pos.getX() + dx, pos.getY() + dy, pos.getZ()+dz)
    
        # load the ball model
        if source is "PlayerRocket":
            self.rocket = loader.loadModel("Assets/Models/player_rocket.egg")
        else:
            self.rocket = loader.loadModel("Assets/Models/enemy_rocket.egg")
            
        self.rocket.setScale(.2)
        self.rocket.lookAt(-dest)
        self.rocket.reparentTo(render)
        
        #movement calculations
        start = Point3(pos.getX(), pos.getY(), pos.getZ())
        self.rocket.setPos(start)
        
        # setup the projectile interval
        self.bulletInterval = LerpPosInterval(self.rocket, 5, dest)
        self.bulletInterval.start()
    
        #Give it a light
        self.redPointLight = self.rocket.attachNewNode( PointLight( "exhaust" ) )
        self.redPointLight.setPos(0.0, 2, 0.0)
        self.redPointLight.node().setColor( Vec4( 1.0, 0, 0, 1 ) )
        self.redPointLight.node().setAttenuation( Vec3( .1, 0.1, 0.0 ) ) 
        render.setLight(self.redPointLight)
            
        print "FIRE"
        
        
    def setupCollision(self, cTrav, cRocketHandler):
    
        #collision sphere
        cSphere = CollisionSphere(Point3(0, 0, 0), 1)
        cNode = CollisionNode(self.source) #Name the rocket "PlayerRocket" or "EnemyRocket"
        cNode.addSolid(cSphere)
        
        if self.source == "PlayerRocket":
            cNode.setFromCollideMask(BitMask32.bit(1))
        else:
            cNode.setFromCollideMask(BitMask32.bit(2))
            
        cNode.setIntoCollideMask(BitMask32.allOff())
        
        cNP = self.rocket.attachNewNode(cNode)
        #cNP.show()
        cTrav.addCollider(cNP, cRocketHandler)
    
    def kill_light(self):
        render.clearLight(self.redPointLight)
        self.redPointLight.remove()
        return
        
        