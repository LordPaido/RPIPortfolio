import direct.directbase.DirectStart
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import Filename
from pandac.PandaModules import PandaNode,NodePath,Camera,TextNode
from pandac.PandaModules import Vec3,Vec4,BitMask32
from pandac.PandaModules import PerspectiveLens
from pandac.PandaModules import AmbientLight,Spotlight
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.task.Task import Task
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from direct.showbase import Audio3DManager
import random, sys, os, math
from direct.gui.OnscreenImage import OnscreenImage


import Rocket, Explosion

SPEED = 0.5

audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0],camera)
RocketFire = loader.loadSfx("Assets/Sound/RocketFlying(Short).ogg")
BoomSound = loader.loadSfx("Assets/Sound/Explosion(Short).ogg")
Running = loader.loadSfx("Assets/Sound/CarIdling.ogg")
Idling = loader.loadSfx("Assets/Sound/CarRunning.ogg")
EnemyRunning = audio3d.loadSfx("Assets/Sound/EnemyCarIdling.ogg")
EnemyIdling = audio3d.loadSfx("Assets/Sound/EnemyCarRunning.ogg")
#Running.setVolume(0.5)
#Idling.setVolume(0.5)
EnemyRunning.setVolume(1)
EnemyRunning.setVolume(1)


# Figure out what directory this program is in.
MYDIR=os.path.abspath(sys.path[0])
MYDIR=Filename.fromOsSpecific(MYDIR).getFullpath()

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
            pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                    pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
            
def end_game(t):
    if t>=1:
        sys.exit(0)
        
def sign(x):
    return x/abs(x)


class World(DirectObject):

    def __init__(self):
        
        self.keyMap = {"left":0, "right":0, "forward":0, "backward":0, "shoot":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        # Post the instructions
        self.inst6 = addInstructions(0.95, "Mad Max's Revenge!")
        self.inst1 = addInstructions(0.90, "[ESC]: Quit")
        self.inst2 = addInstructions(0.85, "[a]: Left Turn")
        self.inst3 = addInstructions(0.80, "[d]: Right Turn")
        self.inst4 = addInstructions(0.75, "[w]: Drive Forward")
        self.inst4 = addInstructions(0.70, "[s]: Reverse")
        self.inst5 = addInstructions(0.65, "[mouse]: Fire Rocket")
        
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.  

        self.environ = loader.loadModel("Assets/Models/env")    #models/environment  
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        self.sky = loader.loadModel("Assets/Models/sky")    #models/environment  
        self.sky.reparentTo(render)
        self.sky.setPos(0,0,0)
        
        # Create the main character, player

        playerStartPos = Point3(8,14,1) #self.environ.find("**/start_point").getPos()
        enemyStartPos = Point3(-7,-8,1) #self.environ.find("**/start_point").getPos()
        #~ print enemyStartPos
        enemyStartPos.addX(1.0)
        enemyStartPos.addY(1.0)
        #~ print enemyStartPos

        
        self.player = Actor("Assets/Models/player_model", {"drive":"Assets/Models/player_drive", "fire":"Assets/Models/player_turret", "drivefire":"Assets/Models/player_both"})
        self.player.reparentTo(render)
        self.player.setScale(0.1)
        self.player.setPos(playerStartPos)
        #~ self.playerdrive=self.player.actorInterval("drive")
        #~ self.playerfire=self.player.actoraaaaaaaInterval("fire")
        #~ self.playerdrivefire=self.player.actorInterval("drivefire")
        
        # Create the enemy, Enemy
        self.enemy = Actor("Assets/Models/enemy_model", {"drive":"Assets/Models/enemy_drive", "fire":"Assets/Models/enemy_turret", "drivefire":"Assets/Models/enemy_both"})
        self.enemy.reparentTo(render)
        self.enemy.setScale(0.1)
        tex = loader.loadTexture("Assets/Models/cartexture1.png")
        self.enemy.setTexture(tex, 1)
        self.enemy.setPos(enemyStartPos)
        self.enemyrockettiming = globalClock.getFrameTime()
        #print self.enemy.getCurrentAnim()

        #print self.enemy.getCurrentAnim()
        #~ self.enemydrive=self.enemy.actorInterval("drive")
        #~ self.enemyfire=self.enemy.actorInterval("fire")
        #~ self.enemydrivefire=self.enemy.actorInterval("drivefire")
        
        self.music = loader.loadMusic("Assets/Sound/music.mp3")
        SoundInterval(self.music).loop()

        audio3d.attachSoundToObject(EnemyRunning, self.enemy)
        audio3d.attachSoundToObject(EnemyIdling, self.enemy)

        backward = self.enemy.getNetTransform().getMat().getRow3(1)
        backward.setZ(0)
        backward.normalize()
        #self.enemy.setPos(self.enemy.getPos() - backward*(50))

        #Set up the lighting
        self.playerleftlight=self.player.attachNewNode(Spotlight("playerheadleft"))
        self.playerleftlight.node().setColor(Vec4(0.75, 0.75, 0.75, 1))
        self.playerleftlight.node().setLens( PerspectiveLens() )
        self.playerleftlight.node().getLens().setFov( 50, 50)
        self.playerleftlight.node().setAttenuation( Vec3( 0.1, 0.005, 0.0 ) )
        self.playerleftlight.node().setExponent( 60.0 )
        self.playerleftlight.setPos(-1, -0.1, 1.5)
        self.playerleftlight.setHpr(180, -10, 0)
        render.setLight(self.playerleftlight)
        
        self.playerrightlight=self.player.attachNewNode(Spotlight("playerheadright"))
        self.playerrightlight.node().setColor(Vec4(0.75, 0.75, 0.75, 1))
        self.playerrightlight.node().setLens( PerspectiveLens() )
        self.playerrightlight.node().getLens().setFov( 50, 50)
        self.playerrightlight.node().setAttenuation( Vec3( 0.1, 0.005, 0.0 ) )
        self.playerrightlight.node().setExponent( 60.0 )
        self.playerrightlight.setPos(1, -0.1, 1.5)
        self.playerrightlight.setHpr(180, -10, 0)
        render.setLight(self.playerrightlight)

        self.playerlightson=1

        self.enemyleftlight=self.enemy.attachNewNode(Spotlight("enemyheadleft"))
        self.enemyleftlight.node().setColor(Vec4(0.75, 0.75, 0.75, 1))
        self.enemyleftlight.node().setLens( PerspectiveLens() )
        self.enemyleftlight.node().getLens().setFov( 50, 50)
        self.enemyleftlight.node().setAttenuation( Vec3( 0.1, 0.005, 0.0 ) )
        self.enemyleftlight.node().setExponent( 60.0 )
        self.enemyleftlight.setPos(-1, -0.1, 1.5)
        self.enemyleftlight.setHpr(180, -10, 0)
        render.setLight(self.enemyleftlight)
        
        self.enemyrightlight=self.enemy.attachNewNode(Spotlight("enemyheadright"))
        self.enemyrightlight.node().setColor(Vec4(0.75, 0.75, 0.75, 1))
        self.enemyrightlight.node().setLens( PerspectiveLens() )
        self.enemyrightlight.node().getLens().setFov( 50, 50)
        self.enemyrightlight.node().setAttenuation( Vec3( 0.1, 0.005, 0.0 ) )
        self.enemyrightlight.node().setExponent( 60.0 )
        self.enemyrightlight.setPos(1, -0.1, 1.5)
        self.enemyrightlight.setHpr(180, -10, 0)
        render.setLight(self.enemyrightlight)
        
        self.enemylightson=1
        
        self.spotlight=camera.attachNewNode(PointLight("spotlight"))
        #self.spotlight.setPos(0, 3, 0.5)
        #self.spotlight.setHpr(0, 0, 0)
        self.spotlight.node().setColor(Vec4(1, 1, 1, 1))
        #self.spotlight.node().setLens( PerspectiveLens() )
        #self.spotlight.node().getLens().setFov( 180, 120)
        self.spotlight.node().setAttenuation( Vec3( 1, 0, 0.05 ))
        #self.spotlight.node().setExponent( 60.0 )
        render.setLight(self.spotlight)
        
        self.playerlight=self.player.attachNewNode(PointLight("spotlight"))
        self.playerlight.node().setColor(Vec4(1, 1, 1, 1))
        #self.spotlight.node().setLens( PerspectiveLens() )
        #self.spotlight.node().getLens().setFov( 180, 120)
        self.playerlight.node().setAttenuation( Vec3( 1, 0, 0.05 ))
        #self.spotlight.node().setExponent( 60.0 )
        render.setLight(self.playerlight)
        
        
        self.ambientlight=self.sky.attachNewNode(AmbientLight("ambientLight"))
        self.ambientlight.node().setColor(Vec4(1, 1, 1, 1))
        self.sky.setLight(self.ambientlight)

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation

        self.accept("escape", sys.exit)
        self.accept("a", self.setKey, ["left",1])
        self.accept("d", self.setKey, ["right",1])
        self.accept("w", self.setKey, ["forward",1])
        self.accept("s", self.setKey, ["backward",1])
        self.accept("a-up", self.setKey, ["left",0])
        self.accept("d-up", self.setKey, ["right",0])
        self.accept("w-up", self.setKey, ["forward",0])
        self.accept("s-up", self.setKey, ["backward",0])
        self.accept("l", self.playerLights,[])
        
        self.accept("mouse1", self.setKey, ["shoot", 1])
        self.accept("mouse1-up", self.setKey, ["shoot", 0]) #self.shootRocketshootRocket

        taskMgr.add(self.playerMove,"moveTask")
        taskMgr.add(self.enemyMove,"moveTask")
        taskMgr.add(self.shoot,"shootTask")
        taskMgr.add(self.rocketCollision,"rocketCollision")

        # Game state variables
        self.prevtime = 0
        self.isMoving = False
        self.prevShotTime = 0
        self.prevEnemyMoveTime = 0

        # Set up the camera
        
        base.disableMouse()
        base.camera.setPos(self.player.getX(),self.player.getY()+10,2)
        
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above player's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav = CollisionTraverser()

        self.playerGroundRay = CollisionRay()
        self.playerGroundRay.setOrigin(0,0,1000)
        self.playerGroundRay.setDirection(0,0,-1)
        self.playerGroundCol = CollisionNode('playerRay')
        self.playerGroundCol.addSolid(self.playerGroundRay)
        self.playerGroundCol.setFromCollideMask(BitMask32.bit(3))
        self.playerGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.playerGroundColNp = self.player.attachNewNode(self.playerGroundCol)
        self.playerGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.playerGroundColNp, self.playerGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(3))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # Uncomment this line to see the collision rays
        #self.playerGroundColNp.show()
        #self.camGroundColNp.show()
       
        #Uncomment this line to show a visual representation of the 
        #collisions occuring
        #self.cTrav.showCollisions(render)
        
        #Code for Enemy player
        self.enemyGroundRay = CollisionRay()
        self.enemyGroundRay.setOrigin(0,0,1000)
        self.enemyGroundRay.setDirection(0,0,-1)
        self.enemyGroundCol = CollisionNode('enemyRay')
        self.enemyGroundCol.addSolid(self.enemyGroundRay)
        self.enemyGroundCol.setFromCollideMask(BitMask32.bit(3))
        self.enemyGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.enemyGroundColNp = self.enemy.attachNewNode(self.enemyGroundCol)
        self.enemyGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.enemyGroundColNp, self.enemyGroundHandler)
        
        self.cRocketHandler = CollisionHandlerQueue()
        
        self.worldEdge = CollisionInvSphere(0, 0, 0, 50)
        
        cNode = CollisionNode("worldEdge")
        cNode.addSolid(self.worldEdge)
        cNode.setFromCollideMask(BitMask32.allOff())
        cNode.setIntoCollideMask(BitMask32.allOn())
        self.worldEdgeNp=self.environ.attachNewNode(cNode)
        #self.cTrav.addCollider(self.worldEdgeNp, self.cRocketHandler)
        #cNP = render.attachNewNode(cNode)
        
        cNode2 = CollisionNode("wall")
        cNode2.addSolid(CollisionPlane(Plane(Vec3(-1,0,0), Point3(22.5,0,0))))
        cNode2.addSolid(CollisionPlane(Plane(Vec3(1,0,0), Point3(-22.5,0,0))))
        cNode2.addSolid(CollisionPlane(Plane(Vec3(0,-1,0), Point3(0,22.5,0))))
        cNode2.addSolid(CollisionPlane(Plane(Vec3(0,1,0), Point3(0,-22.5,0))))
        cNode2.setFromCollideMask(BitMask32.allOff())
        cNode2.setIntoCollideMask(BitMask32.allOn())
        cNP2=self.environ.attachNewNode(cNode2)
        
        self.picker = CollisionTraverser()            #Make a traverser
        self.pq     = CollisionHandlerQueue()         #Make a handler
        #Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        #Attach that node to the camera since the ray will need to be positioned
        #relative to it
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        #Everything to be picked will use bit 1. This way if we were doing other
        #collision we could seperate it
        self.pickerNode.setFromCollideMask(BitMask32.allOn())
        self.pickerRay = CollisionRay()               #Make our ray
        self.pickerNode.addSolid(self.pickerRay)      #Add it to the collision node
        #Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.pq)
        
        self.playerrocket = None
        self.enemyrocket = None
        
        self.enemyTurn = 0
        self.enemyDestAng = 180

        
        self.enemyHp = 3
        self.playerHp = 3
        
        #Collisions
        self.setupCollisions()
        
        self.playermoving = False
        
        
        #setup hud
        self.drawHud()
        
    def drawHud(self):
        
        #Player
        OnscreenText(text="Player Health", style=1, fg=(1,1,1,1), pos=(0.85, 0.9), align=TextNode.ALeft, scale = .08)
        
        self.playerHealthImg = OnscreenImage(image = 'Assets/Images/healthFull.png', pos = (1.05, 0, .84), scale = .12)
        self.playerHealthImg.setTransparency(TransparencyAttrib.MAlpha)
        
        
        #Enemy
        OnscreenText(text="Enemy Health", style=1, fg=(1,1,1,1), pos=(0.85, 0.7), align=TextNode.ALeft, scale = .08)
        
        self.enemyHealthImg = OnscreenImage(image = 'Assets/Images/healthFull.png', pos = (1.05, 0, .64), scale = .12)
        self.enemyHealthImg.setTransparency(TransparencyAttrib.MAlpha)
        

    def updateGui(self):
    
        #player bar
        if self.playerHp == 2:
            self.playerHealthImg.setImage('Assets/Images/healthMedium.png')
            self.playerHealthImg.setTransparency(TransparencyAttrib.MAlpha)
        elif self.playerHp == 1:
            self.playerHealthImg.setImage('Assets/Images/healthLow.png')
            self.playerHealthImg.setTransparency(TransparencyAttrib.MAlpha)
        
        #enemy bar
        if self.enemyHp == 2:
            self.enemyHealthImg.setImage('Assets/Images/healthMedium.png')
            self.enemyHealthImg.setTransparency(TransparencyAttrib.MAlpha)
        elif self.enemyHp == 1:
            self.enemyHealthImg.setImage('Assets/Images/healthLow.png')
            self.enemyHealthImg.setTransparency(TransparencyAttrib.MAlpha)
        


    def setupCollisions(self):

        #player sphere
        cPlayerSphere = CollisionSphere(Point3(0, 0, .5), 10)
        cPlayerNode = CollisionNode("Player")
        cPlayerNode.addSolid(cPlayerSphere)
        
        cPlayerNode.setFromCollideMask(BitMask32.bit(4))
        cPlayerNode.setIntoCollideMask(BitMask32(20))
        
        cPlayerNP = self.player.attachNewNode(cPlayerNode)
        self.cTrav.addCollider(cPlayerNP, self.playerGroundHandler)
        #self.cTrav.addCollider(cPlayerNP, self.cRocketHandler)
        #cPlayerNP.show()
        
        
        #enemy sphere
        cEnemySphere = CollisionSphere(Point3(0, 0, .5), 10)
        cEnemyNode = CollisionNode("Enemy")
        cEnemyNode.addSolid(cEnemySphere)
        
        cEnemyNode.setFromCollideMask(BitMask32.bit(4))
        cEnemyNode.setIntoCollideMask(BitMask32(18))
        
        cEnemyNP = self.enemy.attachNewNode(cEnemyNode)
        self.cTrav.addCollider(cEnemyNP, self.enemyGroundHandler)
        #self.cTrav.addCollider(cEnemyNP, self.cRocketHandler)
        #cEnemyNP.show()
        

    def rocketCollision(self, task):
        """Check for rocket collisions with players and objects"""
        
        toRemove = []
        
        for i in range(self.cRocketHandler.getNumEntries()):
            entry = self.cRocketHandler.getEntry(i)
            #~ print entry		
            
            if entry.getFromNode().getName() == "PlayerRocket" and entry.getIntoNode().getName() == "Enemy":
                self.enemyHp -= 1
                self.updateGui()
                if self.enemyHp == 0:
                    print "Victory!"
                    OnscreenText(text="Victory!", style=2, fg=(0,1,0,1),
                    pos=(-0.6, 0), align=TextNode.ALeft, scale = .5, shadow=(0,0,0,0))
                    self.playerHp += 5
		    #LerpFunc(end_game, fromData = 0, toData = 1, duration = 3.0,
			#blendType = 'noBlend', extraArgs = [], name = None)
                    taskMgr.remove("moveTask")
                    taskMgr.remove("shootTask")
                    #print "GAME OVER, YOU WIN"
                    #sys.exit(0) 
            elif entry.getFromNode().getName() == "EnemyRocket" and entry.getIntoNode().getName() == "Player":
                self.playerHp -= 1
                self.updateGui()
                if self.playerHp == 0:
                    #~ print "GAME OVER, YOU LOSE"
                    OnscreenText(text="Failure!", style=2, fg=(1,0,0,1),
                    pos=(-0.6, 0), align=TextNode.ALeft, scale = .5, shadow=(0,0,0,0))
                    self.enemyHp += 5
                    taskMgr.remove("moveTask")
                    taskMgr.remove("shootTask")
            
            #Add to remove list
            if entry.getFromNodePath() not in toRemove:
                toRemove.append(entry.getFromNodePath())

        #remove
        for np in toRemove:
        
            if np.getNode(0).getName() == "PlayerRocket":
                if self.playerrocket:
                    self.playerrocket.kill_light()
                    #~ print "BOOM!, PLAYER ROCKET EXPLODED"
                    BoomSound.play()
                    RocketFire.stop()
                    Explosion.Explosion(self.playerrocket.rocket.getPos(), render)
                    self.playerrocket = None
                np.getParent().remove()
            
            else:
                if self.enemyrocket:
                    self.enemyrocket.kill_light()
                    #~ print "BOOM!, ENEMY ROCKET EXPLODED"
                    BoomSound.play()
                    RocketFire.stop()
                    Explosion.Explosion(self.enemyrocket.rocket.getPos(), render)
                    self.enemyrocket = None
                np.getParent().remove()
            
        self.cRocketHandler.clearEntries()
        
        return Task.cont
    
    def shootPlayerRocket(self):
        """Shoot a player rocket"""
        
        #Check to see if we can access the mouse. We need it to do anything else
        if base.mouseWatcherNode.hasMouse():
            #get the mouse position
            mpos = base.mouseWatcherNode.getMouse()
          
            #Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

            #Do the actual collision pass
            pickerpoint=Point3(0,0,0)
            self.picker.traverse(render)

            for i in range(self.pq.getNumEntries()):
                entry = self.pq.getEntry(i)
                if entry.getFromNode().getName() == "mouseRay" and entry.getIntoNode().getName()=="terrain":
                    pickerpoint=entry.getSurfacePoint(render)
            direction=pickerpoint-Point3(self.player.getX(), self.player.getY(), self.player.getZ()+0.5)
            #~ if self.playerrocket is None:
                #~ angle = math.radians(self.player.getH())
            playerpos=self.player.getPos()
            self.playerrocket = Rocket.Rocket(Point3(playerpos.getX(), playerpos.getY(), playerpos.getZ()+0.5), direction, "PlayerRocket", render)
            self.playerrocket.setupCollision(self.cTrav, self.cRocketHandler)
            RocketFire.play()
            
            if self.player.getCurrentAnim()=="drive":
                self.player.play("drivefire")
            else:
                self.player.play("fire")
            
    def shootEnemyRocket(self):
        """Shoot a enemy rocket"""
   
        if not (self.enemyrocket) and self.enemyrockettiming <= globalClock.getFrameTime() :
            #~ angle = math.radians(self.enemy.getH())
            #~ self.enemyrocket = Rocket.Rocket(self.enemy.getPos(), angle, "EnemyRocket", render)
            #~ self.enemyrocket.setupCollision(self.cTrav, self.cRocketHandler)
            direction = self.player.getPos() - self.enemy.getPos()
            enemyPos = self.enemy.getPos()
            self.enemyrocket = Rocket.Rocket(enemyPos + Point3(0,0,.5),direction,"EnemyRocket",render)
            self.enemyrocket.setupCollision(self.cTrav, self.cRocketHandler)
            RocketFire.play()
            self.enemy.play("drivefire")
            self.enemyrockettiming = globalClock.getFrameTime() + 2.0
        
    
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def shoot(self, task):
        elapsed = task.time - self.prevShotTime
        if(self.keyMap["shoot"]!=0 and elapsed > 1):
            self.shootPlayerRocket()
            self.prevShotTime = task.time
            
        return Task.cont
    
    def playerLights(self):
        if self.playerlightson:
            self.playerleftlight.node().setColor(Vec4(0,0,0,1))
            self.playerrightlight.node().setColor(Vec4(0,0,0,1))
            self.playerlightson=0
        else:
            self.playerleftlight.node().setColor(Vec4(0.75,0.75,0.75,1))
            self.playerrightlight.node().setColor(Vec4(0.75,0.75,0.75,1))
            self.playerlightson=1
    def enemyLights(self):
        if self.enemylightson:
            self.enemyleftlight.node().setColor(Vec4(0,0,0,1))
            self.enemyrightlight.node().setColor(Vec4(0,0,0,1))
            self.enemylightson=0
        else:
            self.enemyleftlight.node().setColor(Vec4(0.75,0.75,0.75,1))
            self.enemyrightlight.node().setColor(Vec4(0.75,0.75,0.75,1))
            self.enemylightson=1
        
    def enemyMove(self, task):
        elapsed = task.time - self.prevEnemyMoveTime

        startpos = self.enemy.getPos()
        
        #Calculate distance to the enemy
        distvec = self.player.getPos() - self.enemy.getPos()
        distvec.setZ(0)
        dist = distvec.length()
        
        backward = self.enemy.getNetTransform().getMat().getRow3(1)
        backward.setZ(0)
        backward.normalize()
        
        #Drive!
        if self.enemy.getCurrentAnim() is None:
            self.enemy.loop("drive")
            
        #Find the vector from the enemy to the player, then find the angle of that vector
        vec = self.enemy.getPos() - self.player.getPos()
        angle = math.degrees(math.atan2(vec.getX(), vec.getY()))

        #Find the angle left to turn according to the enemy's current angle
        angleToPlayer = (-self.enemy.getH() - angle) % 360
        
        #Fire rocket if within 60 degree arc of player
        #~ print angleToPlayer
        if angleToPlayer < 30 or angleToPlayer > 330:
            self.shootEnemyRocket()
        
        #AI control code starts here
        
        #enemyTurn is zero for heading straight, -1 to turn full left, +1 to turn full right
        #Turning rate is currently maxed at 100 degrees per second
        #drivedir is for forward (1) or backward (-1)
        #Wall avoidance stuff
        enemyTurn=0
        myh=self.player.getH()%360
        print myh
        if abs(self.enemy.getPos().getX())>19 or abs(self.enemy.getPos().getX())>19:
            drivedir=-1.0
        else:
            drivedir=1.0
        if self.playerrocket:
            playerpos=self.player.getPos()
            if playerpos.getX()>12.5 and (myh<90 or myh>270):
                self.enemyTurn = -(0.5+0.05*(self.enemy.getX()-12.5))*sign(myh-180)
                print 1
            elif playerpos.getX()<12.5 and not (myh<90 or myh>270):
                self.enemyTurn = -(0.5+0.05*(12.5-self.enemy.getX()))*sign(myh-180)
                print 2
            elif playerpos.getY()>12.5 and myh<180:
                self.enemyTurn = -(0.5+0.05*(self.enemy.getY()-12.5))*sign(myh-90)
                print 3
            elif playerpos.getY()<12.5 and myh>180:
                self.enemyTurn = -(0.5+0.05*(12.5-self.enemy.getY()))*sign(myh-270)
                print 4
        elif self.enemy.getPos().getX()>12.5 and (myh<90 or myh>270):
            self.enemyTurn = -(0.5+0.05*(self.enemy.getX()-12.5))*sign(myh-180)
            print 5
        elif self.enemy.getPos().getX()<-12.5 and not (myh<90 or myh>270):
            self.enemyTurn = -(0.5+0.05*(12.5-self.enemy.getX()))*sign(myh-180)
            print 6
        elif self.enemy.getPos().getY()>12.5 and myh<180:
            self.enemyTurn = -(0.5+0.05*(self.enemy.getY()-12.5))*sign(myh-90)
            print 7
        elif self.enemy.getPos().getY()<-12.5 and myh>180:
            self.enemyTurn = -(0.5+0.05*(12.5-self.enemy.getY()))*sign(myh-270)
            print 8
        elif not(math.fabs(self.enemyDestAng - angleToPlayer) > 3 and math.fabs(self.enemyDestAng - angleToPlayer) < 357):
            print 9
            self.enemyTurn = 0
        else:
            print 10
            if dist > 5:
                self.enemyDestAng = 0
                if angleToPlayer  > 1  and angleToPlayer <= 180:
                    #Turn left
                    self.enemyTurn = -0.5
                elif angleToPlayer > 180 and angleToPlayer < 359:
                    #Turn right
                    self.enemyTurn = 0.5
                
            elif dist < 5:
                self.enemyDestAng = 180
                if angleToPlayer  >= 0  and angleToPlayer < 179:
                    #Turn left
                    self.enemyTurn = 0.5
                elif angleToPlayer > 181 and angleToPlayer < 360:
                    #Turn right
                    self.enemyTurn = -0.5
        #Replace later
        #drivedir=1.0
        
        #End of AI code
        
        #Enemy always tries to move forward, regardless of where the player is
        self.enemy.setPos(self.enemy.getPos() - backward*(drivedir*elapsed*5))
        self.enemy.setH(self.enemy.getH() - elapsed *100.0*self.enemyTurn)
        EnemyRunning.play()
        
        
        self.cTrav.traverse(render)
        
        entries = []
        terrain = []
        for i in range(self.enemyGroundHandler.getNumEntries()):
            entry = self.enemyGroundHandler.getEntry(i)
            if entry.getFromNode().getName() == "enemyRay":
                terrain.append(entry)
            elif entry.getFromNode().getName() == "Enemy" and entry.getIntoNode().getName() != "terrain":
                entries.append(entry)
        terrain.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))

        if (len(entries)>0):
            self.enemy.setPos(startpos)
        if (len(terrain)>0) and (terrain[0].getIntoNode().getName() == "terrain"):
            self.enemy.setZ(terrain[0].getSurfacePoint(render).getZ()+.5)
        else:
            self.enemy.setPos(startpos)
            
        # Store the task time and continue.
        self.prevEnemyMoveTime = task.time
        return Task.cont

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def playerMove(self, task):
        
        elapsed = task.time - self.prevtime
        
        base.camera.lookAt(self.player)
        camright = base.camera.getNetTransform().getMat().getRow3(0)
        camright.normalize()
            

        # save player's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.player.getPos()
        
        
        # If a move-key is pressed, move player in the specified direction.

        if ((self.keyMap["left"]!=0) & (self.keyMap["forward"]!=0)):
            self.player.setH(self.player.getH() + elapsed*50)
            Idling.stop()
            Running.play()
            self.playermoving = True
        elif((self.keyMap["left"]!=0) & (self.keyMap["backward"]!=0)):
            self.player.setH(self.player.getH() - elapsed*50)
            Idling.stop()
            Running.play()
            self.playermoving = True
        if ((self.keyMap["right"]!=0) & (self.keyMap["forward"]!=0)):
            self.player.setH(self.player.getH() - elapsed*50)
            Idling.stop()
            Running.play()
            self.playermoving = True
        elif ((self.keyMap["right"]!=0) & (self.keyMap["backward"]!=0)):
            self.player.setH(self.player.getH() + elapsed*50)
            Idling.stop()
            Running.play()
            self.playermoving = True
        if (self.keyMap["forward"]!=0):
            backward = self.player.getNetTransform().getMat().getRow3(1)
            backward.setZ(0)
            backward.normalize()
            self.player.setPos(self.player.getPos() - backward*(elapsed*5))
            Running.play()
            Idling.stop()
            self.playermoving = True
        if (self.keyMap["backward"]!=0):
            backward = self.player.getNetTransform().getMat().getRow3(1)
            backward.setZ(0)
            backward.normalize()
            self.player.setPos(self.player.getPos() + backward*(elapsed*5))
            Idling.stop()
            Running.play()
            self.playermoving = True
        if (self.keyMap["backward"]==0 and self.keyMap["forward"]==0 and self.keyMap["left"]==0 and self.keyMap["right"]==0):
            Running.stop()
            Idling.play() 
            self.playermoving = False
            if self.player.getCurrentAnim()=="drive":
                self.player.stop()
                #print "STOP MOVING"
                
        
        #DRIVE!
        if self.player.getCurrentAnim() is None and self.playermoving:
            self.player.loop("drive")
            #print "DRIVE ON!"

            
        dist = 10.0
        angle = math.radians(self.player.getH()) + math.pi
        dx = dist * math.sin(angle)
        dy = dist * -math.cos(angle)
        dest = Point3(self.player.getX() + dx, self.player.getY() + dy, self.player.getZ()+1)
        base.camera.setPos(dest)

        # If player is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                #self.player.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                #self.player.stop()
                #self.player.pose("walk",5)
                self.isMoving = False

        # If the camera is too far from player, move it closer.
        # If the camera is too close to player, move it farther.
        
        camvec = self.player.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 20.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-20))
            camdist = 20.0
        if (camdist < 10.0):
            base.camera.setPos(base.camera.getPos() - camvec*(10-camdist))
            camdist = 10.0

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust player's Z coordinate.  If player's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.
        
        terrain = []
        entries = []
        for i in range(self.playerGroundHandler.getNumEntries()):
            entry = self.playerGroundHandler.getEntry(i)
            if entry.getFromNode().getName() == "playerRay":
                terrain.append(entry)
            elif entry.getFromNode().getName() == "Player" and entry.getIntoNode().getName() != "terrain":
                entries.append(entry)
        terrain.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))     
        
        if (len(entries)>0):
            self.player.setPos(startpos)
        elif (len(terrain)>0) and (terrain[0].getIntoNode().getName() == "terrain"):
            self.player.setZ(terrain[0].getSurfacePoint(render).getZ()+.5)
        else:
            self.player.setPos(startpos)
            
        # Keep the camera at one foot above the terrain,
        # or two feet above player, whichever is greater.
        
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+ 1.5)
        if (base.camera.getZ() < self.player.getZ() + 2.5):
            base.camera.setZ(self.player.getZ() + 2.5)
            
        # The camera should look in player's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above player's head.
        
        self.floater.setPos(self.player.getPos())
        self.floater.setZ(self.floater.getZ()+1)
        base.camera.lookAt(self.floater)

        # Store the task time and continue.
        self.prevtime = task.time
        
        return Task.cont


w = World()
run()