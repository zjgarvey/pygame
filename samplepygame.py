import pygame
import random
import sys
import time
from pygame.locals import *

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()
 
# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 125, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#font creation
font = pygame.font.SysFont('calibri', 14)
font1 = pygame.font.SysFont('calibri', 40)
 
# Screen information
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(GREEN)
pygame.display.set_caption("Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self,v = [0,5]):
        super().__init__() 
        self.vel = v
        self.image = pygame.image.load("mario2.png")
        self.rect = self.image.get_rect()
        if self.vel[0] == 0:
            self.rect.center = (random.randint(self.rect.width//2,SCREEN_WIDTH-self.rect.width//2),-self.rect.height//2) 
        else:
            self.rect.center = (-self.rect.width//2,random.randint(self.rect.height//2,SCREEN_HEIGHT-self.rect.height//2))

    def accelerate(self,v):
        self.vel=[self.vel[i]+v[i] for i in range(2)]
 
    def move(self):
        self.rect.move_ip(self.vel[0],self.vel[1])
        if self.vel[0] == 0:
            if (self.rect.bottom > SCREEN_HEIGHT + self.rect.height):
                self.rect.top = 0
                self.rect.center = (random.randint(self.rect.width//2,SCREEN_WIDTH-self.rect.width//2),-self.rect.height//2)
                self.accelerate([0,random.uniform(-0.5,1)])
        else:
            if (self.rect.right > SCREEN_WIDTH + self.rect.width):
                self.rect.left = 0
                self.rect.center = (-self.rect.width//2,random.randint(self.rect.height//2,SCREEN_HEIGHT-self.rect.height//2))
                self.accelerate([random.uniform(-0.5,1),0])
 
    def draw(self, surface):
        surface.blit(self.image, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("mario2.png")
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH//2, 3*SCREEN_HEIGHT//4)
        self.health=100
        self.speed = 5
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.top > 0:
            if pressed_keys[K_w]:
                self.rect.move_ip(0, -self.speed)
        if self.rect.bottom < SCREEN_HEIGHT:
            if pressed_keys[K_s]:
                self.rect.move_ip(0,self.speed)
         
        if self.rect.left > 0:
              if pressed_keys[K_a]:
                  self.rect.move_ip(-self.speed, 0)
        if self.rect.right < SCREEN_WIDTH:        
              if pressed_keys[K_d]:
                  self.rect.move_ip(self.speed, 0)
        self.speed =5
        if pressed_keys[K_SPACE]:
            self.speed=10
        if pressed_keys[K_LSHIFT]:
            self.speed=2

    def collision(self,E: Enemy):
        if E.rect.bottom > self.rect.top and E.rect.top < self.rect.bottom:
            if abs(E.rect.center[0]-self.rect.center[0])<0.5*(E.rect.width + self.rect.width):
                return 1
            else: 
                return 0
        else:
            return 0
 
    def draw(self, surface):
        surface.blit(self.image, self.rect) 
        surface.blit(font.render(f'Health: {round(self.health,1)}', True, WHITE), (20,20) )

class clock:
    def __init__(self):
        self.start = time.time()
        self.dur = 0
        self.image = font.render(f'Time: {round(self.dur,1)} seconds.', True, WHITE)
    
    def update(self):
        self.dur = time.time()-self.start
        self.image = font.render(f'Time: {round(self.dur,1)} seconds.', True, WHITE)
        self.en = font.render(f'Stayed alive for {round(self.dur,4)} seconds!', True, WHITE)
    
    def draw(self, surface):
        surface.blit(self.image,(20,40)) 

    def end(self, surface):
        x=self.en.get_rect()
        surface.blit(self.en,((SCREEN_WIDTH-x.width)//2, 2*(SCREEN_HEIGHT-x.height)//3 ))
         
P1 = Player()
E1 = Enemy()
E2 = Enemy([7,0])
E3 = Enemy([0,7])
E4 = Enemy([5,0])
E=[E1,E2,E3,E4]

GO=font1.render('GAME OVER!', True, WHITE)
GOR=GO.get_rect()
C = clock()

#game loop begins
while True:

    if P1.health > 0:
        C.update()
        P1.update()

        if C.dur < 10:
            E1.move()
            if P1.collision(E1) > 0:
                    DISPLAYSURF.fill(RED)
                    P1.health+=-1/6
            else:
                DISPLAYSURF.fill(GREEN)  
            E1.draw(DISPLAYSURF)
        elif C.dur < 20: 
            E1.move()     
            E2.move()
            if P1.collision(E1)+P1.collision(E2) > 0:
                    DISPLAYSURF.fill(RED)
                    P1.health+=-1/3
            else:
                DISPLAYSURF.fill(GREEN)
            E1.draw(DISPLAYSURF)
            E2.draw(DISPLAYSURF)
        elif C.dur < 30:
            E1.move()     
            E2.move()
            E3.move()
            if P1.collision(E1) + P1.collision(E2) + P1.collision(E3) > 0:
                    DISPLAYSURF.fill(RED)
                    P1.health+=-1
            else:
                DISPLAYSURF.fill(GREEN)
            E1.draw(DISPLAYSURF)
            E2.draw(DISPLAYSURF)
            E3.draw(DISPLAYSURF)
        else:
            E1.move()     
            E2.move()
            E3.move()
            E4.move()
            if P1.collision(E1) + P1.collision(E2) + P1.collision(E3) + P1.collision(E4)> 0:
                    DISPLAYSURF.fill(RED)
                    P1.health+=-2
            else:
                DISPLAYSURF.fill(GREEN)
            E1.draw(DISPLAYSURF)
            E2.draw(DISPLAYSURF)
            E3.draw(DISPLAYSURF)
            E4.draw(DISPLAYSURF)
        
        P1.draw(DISPLAYSURF)
        C.draw(DISPLAYSURF)
    else:
        DISPLAYSURF.fill(BLACK)
        DISPLAYSURF.blit(GO,((SCREEN_WIDTH-GOR.width)//2,(SCREEN_HEIGHT-GOR.height)//3))
        C.end(DISPLAYSURF)
            

    pygame.display.update()
    FramePerSec.tick(FPS)


        

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
