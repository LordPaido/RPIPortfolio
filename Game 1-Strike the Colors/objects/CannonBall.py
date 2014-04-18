from Mob import MobClass
import pygame
import math
pygame.init()

smallCannonBallImage = pygame.image.load('images/cannonball.png').convert_alpha()
largeCannonBallImage = pygame.image.load('images/largecannonball.png').convert_alpha()
flamingCannonBallImage = pygame.image.load("images/flamecannonball.png").convert_alpha()

class CannonBall(MobClass):
    """Defines the projectiles"""
    def __init__(self, startPosition, direction, creator):
        MobClass.__init__(self)
        self.position = startPosition
        self.direction = direction
        self.creator = creator

    def UpdatePosition(self, width, height):
        """Move and accelerate(turn) the ball"""
        MobClass.UpdatePosition(self, width, height)
        vert = math.fabs(self.speed * math.sin(math.radians(self.direction % 90)))
        hori = math.fabs(self.speed * math.cos(math.radians(self.direction % 90)))

        if self.direction > 270:
            direction = self.direction - 270
            vert = math.fabs(vert)
            hori = math.fabs(hori)
            self.position = (self.position[0] + vert, self.position[1] + hori)
        elif self.direction > 180:
            direction = self.direction - 180
            vert = math.fabs(vert)
            hori = -1 * math.fabs(hori)
            self.position = (self.position[0] + hori, self.position[1] +vert)
        elif self.direction > 90:
            direction = self.direction - 90
            vert = -1*vert
            hori = -1*hori
            self.position = (self.position[0] + vert, self.position[1] + hori)
        else:
            direction = self.direction
            vert = -1 * math.fabs(vert)
            hori = math.fabs(hori)
            self.position = (self.position[0] + hori, self.position[1] + vert)

    #we special case this function so we do not get removed before we enter the screen
    def IsOffScreen(self, width, height):
        if self.position[0] < (-100) or self.position[0] > width + 100:
            return True
        if self.position[1] < (-100) or self.position[1] > height + 100:
            return True
        return False
	

#subclasses
class SmallCannonBall(CannonBall):
    def __init__(self, startPosition, direction, creator):
        CannonBall.__init__(self, startPosition, direction, creator)
        self.damage = 25
        self.image = smallCannonBallImage
        self.speed = 5
        

class LargeCannonBall(CannonBall):
    def __init__(self, startPosition, direction, creator):
        CannonBall.__init__(self, startPosition, direction, creator)
        self.image = largeCannonBallImage
        self.speed = 2.5
        self.damage = 50

class FlamingCannonBall(CannonBall):
    def __init__(self, startPosition, direction, creator):
        CannonBall.__init__(self, startPosition, direction, creator)
        self.image = pygame.transform.rotate(flamingCannonBallImage, direction)
        self.speed = 6
        self.damage = 400

