from Mob import MobClass
from CannonBall import SmallCannonBall, LargeCannonBall
from PirateShip import PirateShipClass
import pygame
import math
import random


class BigBoatClass(PirateShipClass):
    """Defines the BigBoat enemy"""
    def __init__(self, passed_image, startpos, facing, islands):
        PirateShipClass.__init__(self, passed_image, startpos, facing, islands)
        self.speed = random.random()
        self.life = self.life*.75
        self.image = passed_image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (38,56))
        self.damage = 10000
        self.stopped = False
        self.ssize = 2
        if facing == "NORTH":
            self.image = self.image.convert_alpha()
            self.size = (38,56)
        if facing == "EAST":
            self.image = pygame.transform.rotate(self.image, -90)
            self.size = (56,38)
        if facing == "SOUTH":
            self.image = pygame.transform.rotate(self.image, 180)
            self.size = (38,56)
        if facing == "WEST":
            self.image = pygame.transform.rotate(self.image, 90)
            self.size = (56,38)
	
    def fireAI(self, player):
        """Shoot at the player"""
        self.timeSinceLastShot = self.timeSinceLastShot + self.clock.tick()
        if self.timeSinceLastShot > 1500:
            res = self.fire(player.position)

            if res != None:
                self.timeSinceLastShot = 0

            return res
        else:
            return None
	
    def UpdatePosition(self, maxX, maxY):
        #ships move in a straight line in the direction that they were spawned
        #stopping to aviod a collision with an island
        MobClass.UpdatePosition(self, maxX, maxY)

        self.forwardCannon.Update()
        self.leftCannon.Update()
        self.rightCannon.Update()

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
            #stop the ship.
            self.stopped = True
        else:
            self.position = newPos 
