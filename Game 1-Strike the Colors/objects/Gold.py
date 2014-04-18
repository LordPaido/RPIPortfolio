import pygame
from Mob import MobClass

coin = pygame.image.load('images/goldcoin.png')\
                         .convert_alpha()
treasure = pygame.image.load('images/chest.png').convert_alpha()

class GoldClass(MobClass):
    """Defines gold items"""
    def __init__(self,position):
        MobClass.__init__(self)
        self.position = position

class GoldCoin(GoldClass):
    def __init__(self, position):
        GoldClass.__init__(self, position)
        self.image = coin
        self.size = (10,10)
        self.points = 50

class TreasureChest(GoldClass):
    def __init__(self, position):
        GoldClass.__init__(self, position)
        self.image = treasure
        self.size = (20,20)
        self.points = 100
