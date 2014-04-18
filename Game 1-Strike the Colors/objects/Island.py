from Mob import MobClass
import pygame

class IslandClass(MobClass):
    """Defines the islands that appear on the screen"""
    def __init__(self, startpos):
        self.image = pygame.image.load("images/island.png").convert_alpha()
        self.size = (100,100)
        self.direction = None
        self.startpos = startpos
        self.position = startpos
        self.clock = pygame.time.Clock()
        self.damage = 10000
