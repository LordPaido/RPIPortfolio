import pygame
import math
from Mob import MobClass

class BackgroundClass(MobClass):
    """Displays and scrolls the background image"""
    class Inner(MobClass):
        def __init__(self, image, position):
            MobClass.__init__(self)
            self.image = image
            self.position = position

    def __init__(self, image, width, height):
        MobClass.__init__(self)
        self.image = image
        curx = 0
        self.screenWidth = width
        self.screenHeight = height

        self.array = []

        while curx < width:
            self.array.append(self.CreateColumn(curx))
            curx = curx + self.image.get_size()[1]

        self.maxColumns = len(self.array) + 1

    def CreateColumn(self, x):
        """Organize the background into tiled columns"""
        current = []
        cury = 0
        while cury < self.screenHeight:
            current.append(BackgroundClass.Inner(self.image, (x, cury)))
            cury = cury + self.image.get_size()[1]

        return current


    def UpdatePosition(self, maxX, maxY):
        MobClass.UpdatePosition(self, maxX, maxY)

        for y in self.array:
            for x in y:
                x.UpdatePosition(maxX, maxY)

    def render(self, screen):
        """
        this function keeps track of the background, making sure to remove
        it when it goes offscreen
        """
        if self.position[0] < -(self.image.get_size()[1]):
            del self.array[0]
            self.position = self.array[0][0].position

        if len(self.array) != self.maxColumns:
            self.array.append(self.CreateColumn(self.array[-1][0].position[0] + self.image.get_size()[1]))

        for y in self.array:
            for x in y:
                x.render(screen)

        def getimage(self):
            return self.__image

        def setimage(self, image):
            self.__image = image
            self.maxColumns = (640 / self.image.get_size()[1]) + 3

        image = property(getimage,setimage)
