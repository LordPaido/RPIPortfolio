import pygame
import sys
import gamedata
import objects
from random import randint
from objects.PirateShip import PirateShipClass
from objects.BigBoat import BigBoatClass
from objects.SmallBoat import SmallBoatClass
from objects.Island import IslandClass
 
def getRects(objects):
        array = []
        for obj in objects:
            array.append(obj.rect)

        return array

def MapGeneration(maxIslands, maxEnemies, islands, enemies):
    """Generate new obstacles on the fly"""
    while len(islands) < maxIslands and randint(0,60) == 0:
        newIsland = IslandClass((gamedata.width,randint(0,gamedata.height)))
        if newIsland.rect.collidelist(getRects(islands)) != -1 \
           and randint(0,1)==1:
                break
        else:
            islands.append(newIsland)

    while len(enemies) < maxEnemies and randint(0,60) == 0:
        newEnemy = randint(1,6)
        if newEnemy==1:
            newEnemy = SmallBoatClass(\
            pygame.image.load('images/pirateship.png'),\
            (randint(gamedata.width/4,gamedata.width), gamedata.height),\
            "NORTH", islands)
        elif newEnemy==2:
            newEnemy = SmallBoatClass(\
            pygame.image.load('images/pirateship.png'),\
            (randint(gamedata.width/4,gamedata.width), -50), "SOUTH", islands)
        elif newEnemy==3:
            newEnemy = SmallBoatClass(\
            pygame.image.load('images/pirateship.png'),\
            (gamedata.width,randint(0,gamedata.height)), "WEST", islands)
        elif newEnemy==4:
            newEnemy = BigBoatClass(\
            pygame.image.load('images/shiplarge.png'),\
            (randint(gamedata.width/4,gamedata.width), gamedata.height),\
            "NORTH", islands)
        elif newEnemy==5:
            newEnemy = BigBoatClass(\
            pygame.image.load('images/shiplarge.png'),\
            (randint(gamedata.width/4,gamedata.width), -50), "SOUTH", islands)
        else:
            newEnemy = BigBoatClass(\
            pygame.image.load('images/shiplarge.png'),\
            (gamedata.width,randint(0,gamedata.height)), "WEST", islands)
        
        if newEnemy.rect.collidelist(getRects(islands)) != -1 or \
           newEnemy.rect.collidelist(getRects(enemies)) != -1:
            return
        else:
            enemies.append(newEnemy)

    return

def getDifficulty(gametime):
    """Given how long the player has been in gameplay, adjust the difficulty"""
    #convert milliseconds to seconds
    seconds = (pygame.time.get_ticks()-gametime)/1000.0
    #print seconds

    if seconds < 30:
        return (0,1)
    elif seconds < 60:
        return (1,1)
    elif seconds < 90:
        return (2,2)
    elif seconds < 120:
        return (2,3)
    elif seconds < 180:
        return (3,4)
    elif seconds < 210:
        return (4,4)
    else:
        return (0,0)
