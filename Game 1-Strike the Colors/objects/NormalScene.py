import pygame
import Scene
import PirateShip
import Gold
import Music
import random
import Health
import SmallBoat
import BigBoat
from gameutility import MapGeneration, getDifficulty

IslandCollide = Music.Music("sounds/IslandCrash.wav")

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

def getPowerup(position):
    """Chooses an item to spawn when the player kills an enemy"""
    num =random.randint(0,4)

    if num == 0:
        return Health.HealthCross(position)
    elif num == 1:
        return Gold.TreasureChest(position)
    else:
        return Gold.GoldCoin(position)
    

class NormalScene(Scene.Scene):
    """Controls the main gameplay experience"""
    def __init__(self, gamedata, stack):
        Scene.Scene.__init__(self, gamedata, stack)

        self.font = pygame.font.Font(pygame.font.get_default_font(),18)
        self.livesImage = pygame.image.load('images/hat.png').convert_alpha()

        self.keys = { "left" : False, "right" : False, "up" : False, "down": False, "rmouse" : False, "lmouse" : False }

        self.bossScene = None
        
        #Initialize arrays and the player object
        self.ships = []
        self.projectiles = []
        self.islands = []
        self.powerups = []
        self.player = PirateShip.PirateShipClass(pygame.image.load('images/pirateship.png'), (20, 200), "EAST", self.islands)
        self.player.invincible = True
        self.player.renderCounters = True

    def HandleEvent(self, event, index):
            """Respond to player input"""
            #Handle input from WASD
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
            
            #Handle mouse clicks
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

            #combine the two for diagonal motion
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
        """Tasks for when the player dies"""
        if self.player.invincible:
            return

        oldplayer = self.player

        self.gamedata.lives = self.gamedata.lives - 1
        if self.player.life < 1:
            self.player = PirateShip.PirateShipClass(pygame.image.load('images/pirateship.png'), (20, 200), "EAST", self.islands)
            self.player.invincible = True
            self.player.renderCounters = True
        if self.gamedata.lives == 0:
            self.stack.append(Scene.DeadScene(self.gamedata, self.stack))

        for proj in self.projectiles:
            if proj.creator == oldplayer:
                self.creator = self.player

    def Update(self, index):
        """Common tasks for each frame"""
        self.stack[index - 1].Update(index - 1)

        self.player.UpdatePosition(self.gamedata.width, self.gamedata.height)

        #Obtain the current difficulty
        maxIslands, maxEnemies = getDifficulty(self.gamedata.gametime)
        #Generate new islands and enemies if needed
        MapGeneration(maxIslands, maxEnemies, self.islands, self.ships)

        #Start the BossScene after 3 minutes
        if pygame.time.get_ticks() - self.gamedata.gametime > 3*60*1000: # ~3 minutes
            if self.bossScene == None:
                self.bossScene = Scene.BossScene(self.gamedata, self.stack)
                self.stack.insert(index, self.bossScene)
            
            self.bossScene.player = self.player
            
            if len(self.ships) == 0 and len(self.islands) == 0:
                self.bossScene.started = True
                self.stack.remove(self)


        def removeFunc(objects):
            """Remove objects that are off-screen"""
            toRemove = []
            for obj in objects:
                obj.UpdatePosition(self.gamedata.width, self.gamedata.height)
                if obj.IsOffScreen(self.gamedata.width, self.gamedata.height):
                    toRemove.append(obj)
            for obj in toRemove:
                objects.remove(obj)

        removeFunc(self.ships)
        removeFunc(self.projectiles)
        removeFunc(self.islands)
        removeFunc(self.powerups)

        #Check for Ship to Ship Collisions
        shipIndex = self.player.rect.collidelist(getRects(self.ships))
        if shipIndex != -1:
            print "Collision with enemy ship!"
            self.player.hit(self.ships[shipIndex])
            self.ships.remove(self.ships[shipIndex])
            self.ResetPlayer()
    
        #Check for Ship to Island collisions
        islandIndex = self.player.rect.collidelist(getRects(self.islands))
        if islandIndex != -1:
            print "Collision with island!"
            IslandCollide.play(0)
            self.player.hit(self.islands[islandIndex])
            self.ResetPlayer()

        #Check for Cannon Ball to Enemy Ship Collisions
        for ship in self.ships:
            index = ship.rect.collidelist(getRects(self.projectiles))
            if index != -1:
                if self.projectiles[index].creator != ship:
                    ship.hit(self.projectiles[index])
                    if ship.dead:
                        if self.projectiles[index].creator == self.player:
                            if type(ship) == SmallBoat.SmallBoatClass:
                                self.gamedata.points+=100
                                self.gamedata.bonusStrings.append("+100 Gold")
                                self.powerups.append(getPowerup(ship.position))
                            elif type(ship) == BigBoat.BigBoatClass:
                                self.gamedata.points+=50
                                self.gamedata.bonusStrings.append("+50 Gold")
                                self.powerups.append(getPowerup(ship.position))
                        self.ships.remove(ship)
			
                    self.projectiles.remove(self.projectiles[index])
                
        #Check for Player to Cannonball Collisions
        index = self.player.rect.collidelist(getRects(self.projectiles))
        if index != -1 and self.projectiles[index].creator != self.player:
            self.player.hit(self.projectiles[index])
            self.projectiles.remove(self.projectiles[index])
            if self.player.dead == True:
                self.ResetPlayer()

        #Check for Player to powerups Collisions
        index = self.player.rect.collidelist(getRects(self.powerups))
        if index != -1:
            powerup = self.powerups[index]

            if type(powerup) in (Gold.GoldCoin, Gold.TreasureChest):
                self.gamedata.points += self.powerups[index].points
                self.gamedata.bonusStrings.append("+%i Gold" % self.powerups[index].points)
            elif type(powerup) == Health.HealthCross:
                self.player.life = 100

                self.gamedata.bonusStrings.append("Full Life!")
            self.powerups.remove(self.powerups[index])


        #fire projectiles if we need to.
        if self.keys["lmouse"] == True:
            proj = self.player.fire(pygame.mouse.get_pos())
            if proj != None:
                self.projectiles.append(proj)
        if self.keys["rmouse"] == True:
            proj = self.player.fireSpecial(pygame.mouse.get_pos())
            if proj != None:
                self.projectiles.append(proj)
            
	    #Enemy Fires here
    	for ship in self.ships:
            proj = ship.fireAI(self.player)
            if proj != None:
                self.projectiles.append(proj)
		
    def render(self, screen, index):
        self.player.bonusStrings = self.gamedata.bonusStrings
        self.gamedata.bonusStrings = []
        self.stack[index - 1].render(screen, index - 1)
        self.renderEach(screen, self.islands)
        self.renderEach(screen, self.ships)
        self.renderEach(screen, [self.player])
        self.renderEach(screen, self.projectiles)
        drawLives(screen, self.gamedata.lives, self.font, self.livesImage)
        drawPoints(screen, self.gamedata.points, self.font)
        self.renderEach(screen, self.powerups)

    def renderEach(self, screen, objects):
        for obj in objects:
            obj.render(screen)


def getRects(objects):
    array = []
    for obj in objects:
        array.append(obj.rect)
    return array

def drawLives(screen, lives, font,livesImage):
    loc1 = font.size("Lives: ")[0] + 2
    screen.blit(font.render("Lives: ", True, (0,0,0)), (2,12))
    onLife = 0
    while onLife < lives:
        screen.blit(livesImage, (loc1, 0))   
        onLife = onLife + 1
        loc1 = loc1 + 30


treasure = pygame.image.load("images/chest.png").convert_alpha()

def drawPoints(screen, points, font):
    topright = screen.get_rect().topright[0]
    strlen = font.size("%i" % points)[0]
    screen.blit(font.render("%i" % points, True, (0,0,0)), (topright - strlen - 15, 0))
    screen.blit(treasure, ((topright - strlen) - 35, 0))
