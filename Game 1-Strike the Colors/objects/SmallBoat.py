from Mob import MobClass
from CannonBall import SmallCannonBall, LargeCannonBall
from PirateShip import PirateShipClass
import pygame
import math
import random


class SmallBoatClass(PirateShipClass):
    """Defines the SmallBoat enemy"""
    def __init__(self, passed_image, startpos, facing, islands):
        PirateShipClass.__init__(self, passed_image, startpos, facing, islands)
        self.speed = random.random()+.75
        self.life = self.life*.5
        self.image = passed_image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (20,32))
        self.damage = 10000
        self.stopped = False

        self.leftCannon = self.forwardCannon
        self.rightCannon = self.forwardCannon

        if facing == "NORTH":
            self.image = self.image.convert_alpha()
            self.size =(20,32)
        if facing == "EAST":
            self.image = pygame.transform.rotate(self.image, -90)
            self.size = (32,20)
        if facing == "SOUTH":
            self.image = pygame.transform.rotate(self.image, 180)
            self.size = (20,32)
        if facing == "WEST":
            self.image = pygame.transform.rotate(self.image, 90)
            self.size = (32,20)
	    
    def fireAI(self, player):
        """shoot at the player"""
        self.timeSinceLastShot = self.timeSinceLastShot +self.clock.tick()

        if self.timeSinceLastShot > 1250:
            res = self.fire(player.position)

            if res != None:
                self.timeSinceLastShot = 0

            return res

        else:
            #print self.timeSinceLastShot
            return None
	
    def UpdatePosition(self, maxX, maxY):
        #ships move in a straight line in the direction that they were spawned
        #stopping to aviod a collision with an island
        MobClass.UpdatePosition(self, maxX, maxY)

        self.forwardCannon.Update()
        #self.leftCannon.Update()
        #self.rightCannon.Update()

        if self.stopped:
            return

        newPos = self.position
        if self.facing == "EAST":
            newPos = (self.position[0]+self.speed, self.position[1])
        if self.facing == "WEST":
           newPos = (self.position[0]-self.speed, self.position[1])
        if self.facing == "SOUTH":
            newPos = (self.position[0], self.position[1]+self.speed)
        if self.facing == "NORTH":
           newPos = (self.position[0], self.position[1]-self.speed)


        newRect = pygame.Rect((newPos[0], newPos[1]), self.size)

        if newRect.collidelist(self.islands) != -1:
            self.stopped = True
        else:
            self.position = newPos


