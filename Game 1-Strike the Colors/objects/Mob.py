import pygame

"""Mobile Object class that all displayed objects will inherit from"""
class MobClass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.__image = None
        self.__position = (0,0)
        self.__rect = None
        self.__size = (0,0)

    def render(self, screen):
        """base render function.  Simply blits the image"""
        screen.blit(self.image, self.position)

    def UpdatePosition(self, maxX, maxY):
        """any object that does not override this will move every frame, towards the left"""
        self.position = (self.position[0] - 0.5, self.position[1])

    def IsOffScreen(self, width, heigth):
        """for collection purposes, allows us to detect objects that we no longer care about"""
        if self.position[0] < (0 - self.size[0]) or self.position[0] > width:
            return True
        if self.position[1] < (0 - self.size[1]) or self.position[1] > heigth:
            return True
        return False

    def getposition(self):
        return self.__position

    def setposition(self, pos):
        self.__position = pos
        self.rect = pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def getrect(self):
        return self.__rect

    def setrect(self, rect):
        self.__rect = rect

    def getimage(self):
        return self.__image

    def setimage(self, image):
        self.__image = image

    def getsize(self):
        return self.__size
    
    def setsize(self, size):
        self.__size = size
    
    position = property(getposition, setposition)
    rect = property(getrect, setrect)
    image = property(getimage, setimage)
    size = property(getsize, setsize)

