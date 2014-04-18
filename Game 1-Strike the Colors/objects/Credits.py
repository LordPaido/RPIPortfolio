import pygame
import Mob

font = pygame.font.Font(pygame.font.get_default_font(),18)

creditText = """
CONGRATULATIONS!  YOU'VE WON!



Credits

Art
Joe Miller

Programming
Jean-Paul Mayer
Michael Gram
Roger Swingle

Music and Sound
Stephen Kohler
"""


class Credits(Mob.MobClass):
    """Display the credits"""
    def __init__(self):
        Mob.MobClass.__init__(self)
        self.done = False
        self.creditLines = []

        lastY = 480
        for line in creditText.split("\n"):
            surface = font.render(line, True, (0,0,0))

            width = surface.get_size()[0]

            self.creditLines.append(CreditLine(surface, ((640/2)-width/2, lastY)))

            lastY += surface.get_size()[1] + 10


    def UpdatePosition(self, maxX, maxY):
        for line in self.creditLines:
            line.UpdatePosition(maxX, maxY)

    def render(self, screen):
        for line in self.creditLines:
            line.render(screen)


class CreditLine(Mob.MobClass):
    def __init__(self, text, position):
        Mob.MobClass.__init__(self)
        self.image = text
        self.position = position

    def UpdatePosition(self, maxX, maxY):
        self.position = (self.position[0], self.position[1] - 1.0)

