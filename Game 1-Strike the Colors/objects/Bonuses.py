import pygame
import Mob

font = pygame.font.Font(pygame.font.get_default_font(),18)

class BonusText(Mob.MobClass):
    """Generate bonus messages"""
    def __init__(self, position, text):
        Mob.MobClass.__init__(self)

        #render the text at the given position
        self.position = position
        self.image = font.render(text, True, (0,0,0))
        self.speed = 5

    def UpdatePosition(self, maxX, maxY):
        """Change the acceleration of the text"""
        self.position = (self.position[0], self.position[1] - self.speed)
        self.speed *=0.9

    def IsOnScreen(self, maxX, maxY):
        if self.speed < .01:
            return False
        return True
