from Mob import MobClass
from objects.Music import Music
from objects.Tentacle import TentacleClass
from gameutility import getRects
import pygame
import math
import gamedata
import random

class BossClass(MobClass):
        """Defines the final boss and manages all events relating to it"""
        def __init__(self,startpos):
            self.maxX = gamedata.width
            self.maxY = gamedata.height
            self.size=(60,40)
            self.image = pygame.transform.rotate(pygame.image.load("images/head.png").convert_alpha(),0)
            self.position = (self.maxX-100,self.maxY/2)
            self.tentacles = []
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*0/4), self.position[1] + 73*math.sin(math.pi*0/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*2/4), self.position[1] + 73*math.sin(math.pi*2/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*4/4), self.position[1] + 73*math.sin(math.pi*4/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*6/4), self.position[1] + 73*math.sin(math.pi*6/4))))
            self.mode = "Four" #the number of tentacles

    
            for tentacle in self.tentacles:
                tentacle.warmup = 0

            self.life = 2499 
            self.maxlife = 2500
            self.dead = False
            self.destination = (random.randint(320,550), random.randint(40, 440))
            self.speed = 2.5

        def getsize(self):
            return self.size
        
        def hit(self, projectile):
            print "boss hit!"
            self.life = self.life - projectile.damage
            if self.life < 1:
                self.dead = True
                print "dead"
            
        def fireAI(self,target):
            """choose an appropriate tentacle to fire at the player"""
            if random.randint(0, 75) != 0:
                return 
            closest = 9999
            attacker = self.tentacles[0]
            for tentacle in self.tentacles:
                if math.fabs(target[1]-tentacle.position[1]) < closest:
                    closest = math.fabs(target[1]-tentacle.position[1]) 
                    attacker = tentacle
            if attacker.isAttacking() == False:
                attacker.attack(target)

        def CollideWithPlayer(self,target):
            """Check if the player is colliding with the head or tentacles"""
            for tentacle in self.tentacles:
                if tentacle.dead or tentacle.warmup != 0:
                    continue


                index = target.collidelist([tentacle.rect])
                if index != -1:
                    return True
            index = target.collidelist([self.rect])
            if index != -1:
                return True
            return False

        def CollideWithProj(self,projectiles):
            """Check if the head or tentacles have hit any cannonballs"""
            toRemove = []
            hit = False
            for proj in projectiles:
                for tentacle in self.tentacles:
                    if tentacle.warmup != 0 or tentacle.dead:
                        continue

                    index = proj.rect.collidelist([tentacle.rect])
                    if index != -1:
                        #we've collided with a tentacle!
                        tentacle.hit(proj)
                        toRemove.append(proj)
                        hit = True
                
                if not hit:
                    index = proj.rect.collidelist([self.rect])
                    if index != -1:
                        self.hit(proj)
                        toRemove.append(proj)

            for x in toRemove:
                projectiles.remove(x)
                    

        def spawnTentacle(self): 
            i = 0
            if self.mode == "Four":
                for tentacle in self.tentacles:
                    if tentacle.IsOffScreen(self.maxX, self.maxY) or tentacle.dead:
                        self.tentacles[i] = TentacleClass((self.position[0] + 73*math.cos(math.pi*i*2/4), self.position[1] + 73*math.sin(math.pi*i*2/4)))
                        self.tentacles[i].warmup = 180
                    i = i + 1
                        
            elif self.mode == "Six":
                for tentacle in self.tentacles:
                    if tentacle.IsOffScreen(self.maxX, self.maxY) or tentacle.dead:
                        self.tentacles[i] = TentacleClass((self.position[0] + 73*math.cos(math.pi*i/3), self.position[1] + 73*math.sin(math.pi*i/3)))
                        self.tentacles[i].warmup = 180
                    i = i + 1
                
            else:
                for tentacle in self.tentacles:
                    if tentacle.IsOffScreen(self.maxX, self.maxY) or tentacle.dead:
                        self.tentacles[i] = TentacleClass((self.position[0] + 73*math.cos(math.pi*i/4), self.position[1] + 73*math.sin(math.pi*i/4)))
                        self.tentacles[i].warmup = 180
                    i = i + 1
                
                return
        
        def render(self, screen):
            if self.dead:
                return
            MobClass.render(self, screen)
            for tentacle in self.tentacles:
                tentacle.render(screen)
                
        #changes the boss's mode to six tenacles that are evenly spaced around it      
        def changeToSix(self):
            self.mode = "Six"
            #for tentacle in self.tentacles:
            #    tentacle.attack()
            self.tentacles =[]
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*0/3), self.position[1] + 73*math.sin(math.pi*0/3))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*1/3), self.position[1] + 73*math.sin(math.pi*1/3))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*2/3), self.position[1] + 73*math.sin(math.pi*2/3))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*3/3), self.position[1] + 73*math.sin(math.pi*3/3))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*4/3), self.position[1] + 73*math.sin(math.pi*4/3))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*5/3), self.position[1] + 73*math.sin(math.pi*5/3))))
            return
            
        #changes the boss's mode to eight tenacles that are evenly spaced around it    
        def changeToEight(self):
            self.mode = "Eight"
            #for tentacle in self.tentacles:
            #   tentacle.attack()
            self.tentacles =[]
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*0/4), self.position[1] + 73*math.sin(math.pi*0/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*1/4), self.position[1] + 73*math.sin(math.pi*1/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*2/4), self.position[1] + 73*math.sin(math.pi*2/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*3/4), self.position[1] + 73*math.sin(math.pi*3/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*4/4), self.position[1] + 73*math.sin(math.pi*4/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*5/4), self.position[1] + 73*math.sin(math.pi*5/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*6/4), self.position[1] + 73*math.sin(math.pi*6/4))))
            self.tentacles.append(TentacleClass((self.position[0] + 73*math.cos(math.pi*7/4), self.position[1] + 73*math.sin(math.pi*7/4))))
            return
            
            
        def UpdatePosition(self,maxX,maxY):
            i = 0
            #check to see if the boss is at its current targets
            if self.position[0] + self.speed >= self.destination[0] and self.position[0] - self.speed <= self.destination[0]:
                if self.position[1] + self.speed >= self.destination[1] and self.position[1] - self.speed <= self.destination[1]:
                    #get a new target 	
                    self.destination = (random.randint(320,550), random.randint(40, 440))

            #do math to figure out the X and Y distance that should be traveled each frame
            xPlusY = math.fabs(self.destination[0] -self.position[0])
            xPlusY = xPlusY + math.fabs(self.destination[1] -self.position[1])
            xDist = self.destination[0] - self.position[0]
            yDist = self.destination[1] - self.position[1]
            self.position = (self.position[0]+ self.speed*xDist/xPlusY,self.position[1]+ self.speed*yDist/xPlusY)
            
            #if we have more that 50% life	    
            if self.life > self.maxlife/2:
                for tentacle in self.tentacles:
                    #move all tenticals so they stay grouped wit the boss
                    tentacle.UpdatePosition(self.position[0] + 73*math.cos(math.pi*i*2/4), self.position[1] + 73*math.sin(math.pi*i*2/4))
                    i = i + 1
                #spawn any tentaclaes that need to be respawned    
                self.spawnTentacle()
            
            #if we have between that 25% and 50% life	 
            elif self.life > self.maxlife/4:
                #see if the boss has already changed form
                if self.mode != "Six":
                    #change form to six tenacles
                    self.changeToSix()
                else:
                    for tentacle in self.tentacles:
                        #move all tenticals so they stay grouped wit the boss
                        tentacle.UpdatePosition(self.position[0] + 73*math.cos(math.pi*i/3), self.position[1] + 73*math.sin(math.pi*i/3))
                        i = i + 1
                    #spawn any tentaclaes that need to be respawned        
                    self.spawnTentacle()
                    
            #if we have more that 50% life        
            else:
                #see if the boss has already changed form
                if self.mode != "Eight":
                    #change form to eight tenacles
                    self.changeToEight()
                else:
                    for tentacle in self.tentacles:
                         #move all tenticals so they stay grouped wit the boss
                        tentacle.UpdatePosition(self.position[0] + 73*math.cos(math.pi*i/4), self.position[1] + 73*math.sin(math.pi*i/4))
                        i = i + 1
                    #spawn any tentaclaes that need to be respawned   
                    self.spawnTentacle() 
    
