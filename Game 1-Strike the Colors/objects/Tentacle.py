from Mob import MobClass
from CannonBall import SmallCannonBall, LargeCannonBall, FlamingCannonBall
from objects.Music import Music
import pygame
import math
from random import randint

class TentacleClass(MobClass):
    """Defines the Boss' tentacle projectile"""
    def __init__(self,startpos):#,direction):
        if randint(0,1)==0:
            tmp="images/tentaclea.png"
        else:
            tmp="images/tentacleb.png"
        self.image = pygame.image.load(tmp).convert_alpha()
        self.size = (70,20)
        self.startpos = startpos
        self.position = startpos
        self.life = 75
        #self.direction = direction
        self.clock = pygame.time.Clock()
        self.speed = 4.0
        self.attacktime = 0
        self.destination = startpos
        self.xMove = 0
        self.yMove = 0
        self.moving = False
        self.dead = False
        self.warmup = 0 #hides the tentacle for a set number of frames.

    def render(self, screen):
        if self.warmup != 0 or self.dead:
            return
        
        MobClass.render(self, screen)

    def hit(self, obj):
        if self.warmup != 0:
            return
        self.life -= obj.damage
        if self.life < 1:
            self.dead = True

    def isAttacking(self):
        if self.attacktime != 0 or self.warmup != 0:
            return True
        else:
            return False

    def attack(self, target):
        self.attacktime = pygame.time.get_ticks()
        self.destination = target

    def UpdatePosition(self,newX,newY):
        if self.warmup != 0:
            self.warmup -= 1
        #if a tenacle is not attacking    
        if self.attacktime==0:
            #move it to the position that the boss says
            self.position = (newX,newY)
            return
            
        #if a tentacle is attacking do match to figure ou the X and Y distances that should be moved each frame
        xPlusY = math.fabs(self.destination[0] -self.position[0])
        xPlusY = xPlusY + math.fabs(self.position[1] - self.destination[1])
        xDist = self.destination[0] - self.position[0]
        yDist = self.destination[1] - self.position[1]

        seconds = (pygame.time.get_ticks()-self.attacktime)/1000.0
        
        #warning animation makes the tentacle wiggle
        if seconds < 0.1875:
            self.position = (self.position[0], self.position[1] - 0.5)
        elif seconds < 0.5625:
            self.position = (self.position[0], self.position[1] + 0.5)
        elif seconds < 0.75:
            self.position = (self.position[0], self.position[1] - 0.5)
        #tentalce starts moving towards its target    
        else:
            #if the tentacle isnt already moving towards its target lock its X and Y movement speeds so that it will pass through its targer
            #and if it has no collisions keep moving till it moves off screen
            if self.moving == False:
                self.xMove = self.speed*xDist/xPlusY
                self.yMove = self.speed*yDist/xPlusY
                self.moving = True
            #move the tenacle the specified X and Y
            self.position = (self.position[0]+ self.xMove, self.position[1]+ self.yMove)

