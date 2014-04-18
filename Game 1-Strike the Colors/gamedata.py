import pygame
import sys

#this file contains all the globals used by the game

framerate = 60 #we target 60 fps
paused  = False #the game starts unpaused
lives = 5 #you have 5 lives
width = 640
height = 480
pauseFont = pygame.font.Font(pygame.font.get_default_font(),18)
gametime = 0 #to keep track of time spent in-game
beginpause = 0 #instant that game is paused
endpause = 0 #instant that game is unpaused

bonusStrings = [] #strings used to give bonuses to the player

def extraLives(gamedata, old, new):
    """this is a callback executed when the score changes.  
        it awards the player extra lives for every 1000 points"""
    score = 1000
    if old % score > new % score:
        gamedata.lives += 1
        bonusStrings.append("+1 Life!")

class Points:
    """this class pretends to be an integer, so we can add points to it."""
    def __init__(self):
        self.__points = 0
        self.__events = []
        self.gamedata = sys.modules['gamedata']

    def getpoints(self):
        return self.__points

    def AddEvent(self, event):
        self.__events.append(event)

    def RemoveEvent(self, event):
        self.__events.remove(event)

    def __int__(self):
        return self.__points

    def __add__(self, other):
        oldval = self.__points
        self.__points+=other

        for event in self.__events: #fire our callbacks
            event(self.gamedata, oldval, self.__points)

        return self

points = Points()

points.AddEvent(extraLives)

#this text is displayed at the start of the game
helptext = [
                "Welcome to Strike the Colors!",
                "Sink enemy ships and collect gold",
                "as you navigate the sea!",
                "Press Space to begin                     D",
                "Controls:",
                "WASD - Move up/left/down/right",
                "Mouse-Aim and shoot cannonballs",
                "A                                                       D",
                "Cannonballs: Left-click to fire.",
                "Fire in front of the ship to fire small",
                "cannonballs, or to the side to fire a",
                "large, broadside cannonball!",
                "Right-click in any direction to fire",
                "a firey cannonball of destruction! ",
                "All cannonballs must recharge.",
                "A life is rewarded every 1000 gold"
               ]

#not using this for the time being
#class WindDirection(object):
#    UP = 0
#    DOWN = 1
#    LEFT = 2
#    RIGHT = 3
#windDirection = WindDirection.UP
