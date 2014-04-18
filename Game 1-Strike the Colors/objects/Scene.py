from objects.PirateShip import PirateShipClass
from objects.BigBoat import BigBoatClass
from objects.SmallBoat import SmallBoatClass
from objects.Background import BackgroundClass
from objects.Island import IslandClass
from objects.Music import Music
from objects.Boss import BossClass
from objects.Gold import GoldCoin, TreasureChest
from objects.Credits import Credits
import pygame
import sys
import gamedata
from gameutility import MapGeneration, getDifficulty

Background = Music("sounds/GameBackground.wav")
DeathMusic = Music("sounds/Death.wav")
IslandCollide = Music("sounds/IslandCrash.wav")
BossMusic = Music("sounds/BossMusic.wav")
CreditMusic = Music("sounds/Credits.wav")

treasure = pygame.image.load("images/chest.png").convert_alpha()

def drawLines(screen, rect):
    """Developer function used for checking bounding boxes"""
    upleft = rect.topleft
    h = rect.height + upleft[1]
    while(upleft[1] < h):
        screen.set_at(upleft, (0,0,0))
        upleft = (upleft[0], upleft[1]+1)

    botleft = rect.bottomleft
    w = rect.width + botleft[0]
    while(botleft[0] < w):
        screen.set_at(botleft, (0,0,0))
        botleft = (botleft[0] + 1, botleft[1])

    topright = rect.topright
    h = rect.height + topright[1]
    while(topright[1] < h):
        screen.set_at(topright, (0,0,0))
        topright = (topright[0], topright[1] + 1)

    topleft = rect.topleft
    w = rect.width + topleft[0]
    while(topleft[0] < w):
        screen.set_at(topleft, (0,0,0))
        topleft = (topleft[0]+1, topleft[1])

def drawPoints(screen, points, font):
    topright = screen.get_rect().topright[0]
    strlen = font.size("%i" % points)[0]
    screen.blit(font.render("%i" % points, True, (0,0,0)), (topright - strlen - 15, 0))
    screen.blit(treasure, ((topright - strlen) - 35, 0))

def drawShips(screen, ships):
    for ship in ships:
        ship.render(screen)
        #drawLines(screen, ship.rect)

def drawProjectiles(screen, projectiles):
    for proj in projectiles:
        proj.render(screen)

def drawIslands(screen, islands):
    for island in islands:
        island.render(screen)
        #drawLines(screen,island.rect)

def drawLives(screen, lives, font,livesImage):
    loc1 = font.size("Lives: ")[0] + 2
    screen.blit(font.render("Lives: ", True, (0,0,0)), (2,12))
    onLife = 0
    while onLife < lives:
        screen.blit(livesImage, (loc1, 0))   
        onLife = onLife + 1
        loc1 = loc1 + 30

def drawGold(screen, golds):
    for gold in golds:
        gold.render(screen)

def getRects(objects):
        array = []
        for obj in objects:
            array.append(obj.rect)

        return array

class Scene:
    """Framework for controlling all game events"""
    def __init__(self, gamedata, stack):
        self.stack = stack
        self.gamedata = gamedata 

    def HandleEvent(self, event, index):
        return

    def render(self, screen, index):
        return

    def Update(self, index):
        return


class BackgroundScene(Scene):
    """Wrapper for BackgroundClass"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        self.background = BackgroundClass(pygame.image.load('images/water.png').convert(), self.gamedata.width, self.gamedata.height)
    
    def Update(self, index):
        self.background.UpdatePosition(self.gamedata.width, self.gamedata.height)

    def render(self, screen, index):
        self.background.render(screen)
            

class PausedScene(Scene):
    """Scene that is active when the game is paused"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        gamedata.beginpause = pygame.time.get_ticks()
        self.firstframe = False

    def HandleEvent(self, event, index):
        handled = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.gamedata.paused:
                sys.exit()
            elif event.key == pygame.K_SPACE and self.gamedata.lives != 0:
                self.gamedata.paused = not self.gamedata.paused
                self.firstframe = self.gamedata.paused
                if self.gamedata.paused == False:
                    gamedata.endpause = pygame.time.get_ticks()
                    gamedata.gametime += gamedata.endpause - gamedata.beginpause

        if not handled and (not self.gamedata.paused or event.type == pygame.KEYUP):
            self.stack[index-1].HandleEvent(event, index-1)

    def render(self, screen, index):
        self.stack[index-1].render(screen, index - 1)

        if self.gamedata.paused:
			font = self.gamedata.pauseFont
			screen.blit(font.render("Paused", True, (0,0,0)), (200,200))
			Background.pause()


    def Update(self, index):
        if self.firstframe == True:
            gamedata.beginpause = pygame.time.get_ticks()
            self.firstframe = False
        if not self.gamedata.paused:				
		    self.stack[index - 1].Update(index - 1)
		    Background.unpause()

class StartScene(Scene):
    """Scene for the start of the game"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        self.splash = pygame.image.load("images/splash.png").convert()

    def render(self, screen, index):
        self.stack[index - 1].render(screen, index - 1)
        screen.blit(self.splash, (160,120))

    def HandleEvent(self, event, index):
        if event.type == pygame.KEYDOWN:	
            Background.play(-1)
            self.stack.remove(self)
        return

class DeadScene(Scene):
    """Game Over screen"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        self.image = pygame.image.load("images/skull_and_crossbones.png")
        DeathMusic.play(0)

    def render(self, screen, index):
        screen.fill((0,0,0))
        Background.stop()
        screen.blit(self.image, (120, 40))
        screen.blit(self.gamedata.pauseFont.render("Press Q to quit.", True, (255,255,255)), (245, 410))

    def HandleEvent(self, event, index):
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_q:
                sys.exit()
        return

class BossScene(Scene):
    """Boss battle"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        self.font = pygame.font.Font(pygame.font.get_default_font(),18)
        self.livesImage = pygame.image.load('images/hat.png').convert_alpha()

        self.keys = { "left" : False, "right" : False, "up" : False, "down": False, "rmouse" : False, "lmouse" : False }
        self.boss = BossClass((300,300))

        #Adding the player
        self.projectiles = []
        self.player = PirateShipClass(pygame.image.load('images/pirateship.png'), (20, 200), "EAST", [])
        self.player.invincible = True
        self.player.renderCounters = True
        self.started = False
        self.mplay = False

    def HandleEvent(self, event, index):
        """Common tasks for each frame"""
        if not self.started:
            self.stack[index - 1].HandleEvent(event, index - 1)
            return
        if not self.mplay:
            Background.stop()
            BossMusic.play(-1)
            self.mplay = True
        
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            what = False
            if event.type == pygame.KEYDOWN:
                what = True
            elif event.type == pygame.KEYUP:
                what = False

            if event.key == pygame.K_a:
                self.keys["left"] = what
            elif event.key == pygame.K_s:
                self.keys["down"] = what
            elif event.key == pygame.K_d:
                self.keys["right"] = what
            elif event.key == pygame.K_w:
                self.keys["up"] = what

        if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            whatButtons = pygame.mouse.get_pressed()
            #we only care about left\right click
            self.keys["lmouse"] = whatButtons[0]
            self.keys["rmouse"] = whatButtons[2]


        #set the direction the ship is traveling based on what keys are currently down
        horizontalDirection = 0
        if self.keys["right"] and not self.keys["left"]:
            horizontalDirection = 3
        elif self.keys["left"] and not self.keys["right"]:
            horizontalDirection = 9

        verticalDirection = 0
        if self.keys["up"] and not self.keys["down"]:
            verticalDirection = 12
        elif self.keys["down"] and not self.keys["up"]:
            verticalDirection = 6

        #combine the two
        direction = 0
        if horizontalDirection == 3 and verticalDirection == 12:
            direction = 1.5
        elif horizontalDirection == 3 and verticalDirection == 6:
            direction = 4.5
        elif horizontalDirection == 9 and verticalDirection == 12:
            direction = 10.5
        elif horizontalDirection == 9 and verticalDirection == 6:
            direction = 7.5
        elif horizontalDirection == 0 and not verticalDirection == 0:
            direction = verticalDirection
        elif not horizontalDirection == 0 and verticalDirection == 0:
            direction = horizontalDirection

        self.player.direction = direction
                

    def ResetPlayer(self):
        """When the player dies"""
        if self.player.invincible:
            return

        oldplayer = self.player

        self.gamedata.lives = self.gamedata.lives - 1
        
        self.player = PirateShipClass(pygame.image.load('images/pirateship.png'), (20, 200), "EAST", [])
        self.player.invincible = True
        self.player.renderCounters = True
        
        if self.gamedata.lives == 0:
            self.stack.append(DeadScene(self.gamedata, self.stack))

        for proj in self.projectiles:
            if proj.creator == oldplayer:
                proj.creator = self.player

    def Update(self, index):
        self.stack[index - 1].Update(index - 1)

        if not self.started:
            return

        if self.boss.dead:
            return

        self.player.UpdatePosition(self.gamedata.width, self.gamedata.height)
        self.boss.UpdatePosition(self.gamedata.width, self.gamedata.height)

        toRemove = []
        for projectile in self.projectiles:
            projectile.UpdatePosition(self.gamedata.width, self.gamedata.height)
            if projectile.IsOffScreen(self.gamedata.width,self.gamedata.height):
                toRemove.append(projectile)
        for obj in toRemove:
            self.projectiles.remove(obj)

        #fire player's projectiles if we need to.
        if self.keys["lmouse"] == True:
            proj = self.player.fire(pygame.mouse.get_pos())
            if proj != None:
                self.projectiles.append(proj)
        if self.keys["rmouse"] == True:
            proj = self.player.fireSpecial(pygame.mouse.get_pos())
            if proj != None:
                self.projectiles.append(proj)
            
	    #Enemy Fires here
        self.boss.fireAI(self.player.position)

        #Check for player/boss collisions
        if self.boss.CollideWithPlayer(self.player.rect) == True:
            self.ResetPlayer()

        #Check for cannonball/boss collisions
        self.boss.CollideWithProj(self.projectiles)

        if self.boss.dead:
            self.stack.append(CreditsScene(self.gamedata, self.stack))
            
		
    def render(self, screen, index):
        self.stack[index - 1].render(screen, index - 1)

        if not self.started:
            return 

        drawShips(screen, [self.player])

        if self.boss.dead:
            return

        drawProjectiles(screen, self.projectiles)
        drawLives(screen, self.gamedata.lives, self.font, self.livesImage)
        drawPoints(screen, self.gamedata.points, self.font)
        self.boss.render(screen)

class CreditsScene(Scene):
    """Print the credits"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        self.credits = Credits()
        BossMusic.stop()
        CreditMusic.play(-1)

    def Update(self, index):
        self.stack[index - 1].Update(index - 1)
        self.credits.UpdatePosition(gamedata.width, gamedata.height)
        if self.credits.done:
            self.stack.remove(self)
    
    def render(self, screen, index):
        self.stack[index - 1].render(screen, index - 1)
        self.credits.render(screen)
    
    def HandleEvent(self, event, index):
        if event.type == pygame.KEYDOWN:
            if event.key in ( pygame.K_ESCAPE, pygame.K_q ):
                sys.exit()

class HelpScene(Scene):
    """Show help text"""
    def __init__(self, gamedata, stack):
        Scene.__init__(self, gamedata, stack)
        self.pagenum = 0
        self.strings = gamedata.helptext
        self.time = pygame.time.get_ticks()
        self.font = gamedata.pauseFont
        self.rightArrow = pygame.image.load("images/arrow.png").convert()
        self.leftArrow = pygame.transform.rotate(pygame.image.load("images/arrow.png").convert(), 180)
        self.splash = pygame.image.load("images/splash.png").convert()

    def HandleEvent(self, event, index):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if self.pagenum >= 4:
                    self.pagenum -= 4
            elif event.key == pygame.K_d:
                if self.pagenum < len(self.strings) - 4:
                    self.pagenum += 4
            elif event.key in (pygame.K_SPACE, pygame.K_ESCAPE):
                self.stack.remove(self)
                Background.play(-1)
            
            print self.pagenum

    def render(self, screen, index):
        self.stack[index-1].render(screen, index - 1)
        screen.blit(self.splash, (160,120))
        if self.pagenum >= 0 and self.pagenum < len(self.strings):
            screen.blit(self.font.render(self.strings[self.pagenum], True, (0,0,0)), (160 + 5,120 + 25))
            screen.blit(self.font.render(self.strings[self.pagenum+1], True, (0,0,0)), (160 + 5,120 + 60 + 25))
            screen.blit(self.font.render(self.strings[self.pagenum+2], True, (0,0,0)), (160 + 5,120 +120 + 25))
            screen.blit(self.font.render(self.strings[self.pagenum+3], True, (0,0,0)), (160 + 5,120 +180+ 25))

            if self.pagenum > 0:
                screen.blit(self.leftArrow, (160 - self.leftArrow.get_size()[0], 320))
            if self.pagenum < len(self.strings) - 4:
                screen.blit(self.rightArrow, (160 + 320, 320))
