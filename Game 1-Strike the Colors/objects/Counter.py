import pygame
import Mob

pygame.init()

counterImage = pygame.image.load("images/health.png")

class Counter(pygame.sprite.Sprite):
    """Shows the status of a cannon in a pie-chart"""
    def __init__(self):
        self.percentage = 100
        self.size = (20,20)

    def render(self, screen, position):
        x = 100

        if self.percentage < 20:
            x = 100
        elif self.percentage < 40:
            x = 80
        elif self.percentage < 60:
            x = 60
        elif self.percentage < 80:
            x = 40
        elif self.percentage < 100:
            x = 20
        else:
            x = 0

        if self.percentage <= 100:
            screen.blit(counterImage, (position[0] - 10, position[1] - 10), pygame.Rect(x, 0, 20, 20))


