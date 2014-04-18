import pygame
import Mob

healthImage = pygame.image.load("images/healthcross.png").convert_alpha()

class HealthCross(Mob.MobClass):
    """Defines the health crate item"""
    def __init__(self, position):
        Mob.MobClass.__init__(self)
        self.image = healthImage
        self.position = position
        self.size = self.image.get_size()
