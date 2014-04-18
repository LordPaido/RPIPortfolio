from Mob import MobClass
from CannonBall import SmallCannonBall, LargeCannonBall, FlamingCannonBall
from objects.Cannon import Cannon
from objects.Counter import Counter
import Bonuses
import pygame
import math



class PirateShipClass(MobClass):
    """Superclass of the player, BigBoat, and SmallBoat"""
    def __init__(self, passed_image, startpos, facing, islands):
        MobClass.__init__(self)
        self.image = pygame.transform.rotate(passed_image.convert_alpha(), -90)
        self.size = (47,32)
        self.direction = None
        self.startpos = startpos
        self.position = startpos
        self.maxlife = 100.0
        self.life = 100
        self.dead = False
        self.clock = pygame.time.Clock()
        self.timeSinceLastShot = 0
        self.forwardCannon = Cannon(5, 25, SmallCannonBall, Counter())
        self.leftCannon = Cannon(2.5, 50, LargeCannonBall, Counter())
        self.rightCannon = Cannon(2.5, 50, LargeCannonBall, Counter())
        self.flamingCannon = Cannon(0.5, 400, FlamingCannonBall, Counter())
        self.facing = facing
        self.invincible = False
        self.invincibletime = 0
        self.shouldrender = True
        self.speed = 2.0
        self.reload = 1.0
        self.islands = islands
        self.renderCounters = False
        self.bonusStrings = []
        self.renderedBonuses = []

    def render(self, screen):
        if self.shouldrender or self.invincible == False:
                MobClass.render(self, screen)
        if self.renderCounters: #render counters for the player
            self.forwardCannon.render(screen, (self.rect.center[0] + 35, self.rect.center[1]))
            self.leftCannon.render(screen, (self.rect.center[0], self.rect.center[1] - 25))
            self.rightCannon.render(screen, (self.rect.center[0], self.rect.center[1] + 25))
            self.flamingCannon.render(screen, (self.rect.center[0] - 35, self.rect.center[1]))

        startpos = (int(self.position[0]), int(self.position[1] + self.size[1]))
        length = int((self.life / self.maxlife) * self.size[1])

        for x in xrange(startpos[0], startpos[0] + length):
            screen.set_at((x, startpos[1]), (255,0,0))

        for str in self.bonusStrings:
            self.renderedBonuses.append(Bonuses.BonusText(self.position, str))

        for rendered in self.renderedBonuses:
            rendered.render(screen)

    def UpdatePosition(self, maxX, maxY):
        #Turn off invincibility from when the player respawns
        if not self.invincible and self.invincibletime == 180:
            self.invincibletime = 0

        if self.invincibletime != 180:
            self.invincibletime = self.invincibletime + 1
            if self.invincibletime % 8 == 0:
                self.shouldrender = not self.shouldrender
        else:
            self.invincible = False
            
        #self.invincible = True

        self.forwardCannon.Update()
        self.leftCannon.Update()
        self.rightCannon.Update()
        self.flamingCannon.Update()

        #Update speed
        newPos = self.position
        if self.direction == 1.5:
            newPos = (self.position[0] + self.speed/2, self.position[1] - self.speed/2)
        if self.direction == 3:
           newPos = (self.position[0] + self.speed, self.position[1])
        if self.direction == 4.5:
            newPos = (self.position[0] + self.speed/2, self.position[1] + self.speed/2)
        if self.direction == 6:
           newPos = (self.position[0], self.position[1] + self.speed)
        if self.direction == 7.5:
            newPos = (self.position[0] - self.speed/2, self.position[1] + self.speed/2)
        if self.direction == 9:
           newPos = (self.position[0] - self.speed, self.position[1])
        if self.direction == 10.5:
            newPos = (self.position[0] - self.speed/2, self.position[1] - self.speed/2)
        if self.direction == 12:
           newPos = (self.position[0], self.position[1] - self.speed)

        if maxX - self.size[0] < newPos[0]:
            newPos = (maxX - self.size[0], newPos[1])
        if newPos[0] < 0:
            newPos = (0, newPos[1])
        if maxY - self.size[1] < newPos[1]:
            newPos = (newPos[0], maxY - self.size[1])
        if newPos[1] < 0:
            newPos = (newPos[0], 0)
        
        self.position = newPos

        #Remove ship if it has passed off screen
        toRemove = []
        for rendered in self.renderedBonuses:
            if rendered.IsOnScreen(maxX, maxY):
                rendered.UpdatePosition(maxX, maxY)
            else:
                toRemove.append(rendered)
        
        for obj in toRemove:
            self.renderedBonuses.remove(obj)
            

    def computeAngle(self, coords):
        coords = (float((self.position[0] + self.size[0]/2) - coords[0]), float((self.position[1] + self.size[1]/2) - coords[1]))
        degrees = 0

        if coords[1] != 0:
            degrees = math.fabs(math.degrees(math.atan(coords[0]/coords[1])))
        

        if coords[0] < 0 and coords[1] <= 0:
            #lower right quadrant
            degrees = degrees + 270
        if coords[0] <= 0 and coords[1] >= 0:
            #upper right quadrant
            degrees = 90 - degrees
        if coords[0] > 0 and coords[1] <= 0:
            #lower left quadrant
            degrees = (90 - degrees) + 180
        if coords[0] > 0 and coords[1] >= 0:
            #upper left quandrant
            degrees = degrees + 90

        return degrees


    def fire(self, coords):
        """Fire a cannonball!"""
        #need to compute the vector the shot needs to go in
        degrees = self.computeAngle(coords)

        startingPos = (self.position[0] + self.size[0]/2, self.position[1] + self.size[1]/2)

        #EAST corresponds to only the player since no other ships face east
        if self.facing == "EAST":
            if degrees < 45 or degrees > 315:
                #firing small cannonball
                return self.forwardCannon.Fire(startingPos, degrees, self)
		
            #Deadzone Behind ship
            if degrees > 125 and degrees < 235:
                return None
		
            #fining Large Cannon
            if degrees < 180: #firing left cannons
                return self.leftCannon.Fire(startingPos, degrees, self)
            else:	#firing right cannons
                return self.rightCannon.Fire(startingPos, degrees, self)
	
        if self.facing == "WEST":
            if degrees < 225 and degrees > 135:
                #firing small cannonball
                return self.forwardCannon.Fire(startingPos, degrees, self)
		
            #Deadzone Behind ship
            if degrees > 315 or degrees < 45:
	    		return None
		
		    #fining Large Cannon
            if degrees > 180: #firing left cannons
                return self.leftCannon.Fire(startingPos, degrees, self)
            else:	#firing right cannons
                return self.rightCannon.Fire(startingPos, degrees, self)
	
        if self.facing == "NORTH":
            if degrees < 135 and degrees > 45:
                #firing small cannonball
                return self.forwardCannon.Fire(startingPos, degrees, self)

            #Deadzone Behind ship
            if degrees > 225 and degrees < 315:
                return None
		
            #fining Large Cannon
            if degrees < 270 and degrees > 90: #firing left cannons
                return self.leftCannon.Fire(startingPos, degrees, self)
            else:	#firing right cannons
                return self.rightCannon.Fire(startingPos, degrees, self)
    
        if self.facing == "SOUTH":
            if degrees < 315 and degrees > 225:
                #firing small cannonball
                return self.forwardCannon.Fire(startingPos, degrees, self)
		
            #Deadzone Behind ship
            if degrees > 45 and degrees < 135:
                return None
		
            #firing Large Cannon
            if degrees > 270 or degrees < 90: #firing left cannons
                return self.leftCannon.Fire(startingPos, degrees, self)
            else:	#firing right cannons
                return self.rightCannon.Fire(startingPos, degrees, self)
    
    def fireSpecial(self, coords):
        """Only the player can use the flaming cannonball"""
        degrees = self.computeAngle(coords)
        return self.flamingCannon.Fire((self.position[0] + self.size[0]/2, self.position[1] + self.size[1]/2), degrees, self)
	
    def hit(self, projectile):
        if not self.invincible:
            self.life = self.life - projectile.damage
            if self.life < 1:
	            self.dead = True
		
