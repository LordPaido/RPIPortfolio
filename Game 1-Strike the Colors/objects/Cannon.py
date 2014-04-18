import pygame
from objects.Music import Music
CFire = Music("sounds/CFire.wav")

class Cannon(object):
    """Defines the cannons associated with the PirateShip class"""
    def __init__(self, recharge, damage, type, counter):
        self.rechargeRate = recharge
        self.damage = damage
        self.type = type
        self.counter = counter

    def Update(self):
        if self.counter.percentage < 100:
            self.counter.percentage = self.counter.percentage + self.rechargeRate

    def Fire(self, position, degrees, owner):
        """Fire a cannonball if the cannon is charged"""
        if self.counter.percentage >= 100:
            self.counter.percentage = 0
            CFire.play(0)
            return self.type(position, degrees, owner)

        return None

    def render(self, screen, position):
        """Display a counter if the cannon is not charged"""
        if self.counter.percentage < 100:
            self.counter.render(screen, position)

