#!/usr/bin/env python
 
import pygame

pygame.init()

import gamedata


screen = pygame.display.set_mode((gamedata.width,gamedata.height))
pygame.display.set_caption("Strike the Colors!")
masterclock = pygame.time.Clock()

import sys
import getopt
import objects
from objects.PirateShip import PirateShipClass 
from objects.BigBoat import BigBoatClass
from objects.SmallBoat import SmallBoatClass
from objects.Background import BackgroundClass
from objects.Island import IslandClass
import objects.NormalScene
from objects.Scene import PausedScene
from objects.Scene import BackgroundScene
from objects.Scene import StartScene, BossScene, HelpScene, CreditsScene

moving = False

sceneStack = []

sceneStack.append(BackgroundScene(gamedata, sceneStack))
sceneStack.append(objects.NormalScene.NormalScene(gamedata, sceneStack))
#sceneStack.append(BossScene(gamedata, sceneStack))
#sceneStack[1].started = True
sceneStack.append(PausedScene(gamedata, sceneStack))
sceneStack.append(HelpScene(gamedata, sceneStack))

while True:
    masterclock.tick(gamedata.framerate)

    for event in pygame.event.get():
        sceneStack[-1].HandleEvent(event, len(sceneStack) - 1)

    #screen.fill((0,0,0))

    sceneStack[-1].Update(len(sceneStack) - 1)
    sceneStack[-1].render(screen, len(sceneStack) - 1)


    pygame.display.flip()


