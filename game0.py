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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(GREEN)
pygame.display.set_caption("Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self,v = [0,0]):
        super().__init__() 
        self.vel = v
        self.image = pygame.image.load("mario2.png")
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH//2, 0)

    def accelerate(self,v):
        self.vel=[self.vel[i]+v[i] for i in range(2)]
 
    def move(self):
        self.rect.move_ip(self.vel[0],self.vel[1])
        if (self.rect.bottom > SCREEN_HEIGHT + self.rect.height):
            self.rect.top = 0
            self.rect.center = (random.randint(self.rect.width//2,SCREEN_WIDTH-self.rect.width//2),-self.rect.height//2)
            self.vel = [0,0]

    def hit(self, p):
        while p.collision(self) == 1:
            h=[self.rect.bottom, self.rect.top,p.rect.bottom,p.rect.top]
            w=[self.rect.left,self.rect.right,p.rect.left,p.rect.right]
            h.sort()
            w.sort()
            H=(h[2]-h[1])
            W=(w[2]-w[1])
            A=H*W/(self.rect.width*self.rect.height)
            l1=list(self.rect.center)
            l2=list(p.rect.center)
            l=[l1[i]-l2[i] for i in range(2)]
            l1=[l1[i]+A*l[i] for i in range(2)]
            self.rect.center = tuple(l1)
            self.vel = [p.vx,p.vy]

            

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
        self.vx = 0
        self.vy = 0
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()

        #speed
        if pressed_keys[K_SPACE]:
            self.speed = 10
        elif pressed_keys[K_LSHIFT]:
            self.speed = 2
        else:
            self.speed = 5

        #vertical movement
        if pressed_keys[K_w]:
            if self.rect.top > 0:
                self.rect.move_ip(0, -self.speed)
                self.vy = - self.speed
        elif pressed_keys[K_s]:
            if self.rect.bottom < SCREEN_HEIGHT:
                self.rect.move_ip(0,self.speed)
                self.vy = self.speed
        else:
            self.vy = 0

        #horizontal movement
        if pressed_keys[K_a]:
            if self.rect.left > 0:
                self.rect.move_ip(-self.speed, 0)
                self.vx = -self.speed
        elif pressed_keys[K_d]:
            if self.rect.right < SCREEN_WIDTH:
                self.rect.move_ip(self.speed, 0)
                self.vx = self.speed
        else:
            self.vx = 0


    def collision(self,E: Enemy):
        if E.rect.bottom > self.rect.top and E.rect.top < self.rect.bottom:
            if abs(E.rect.center[0]-self.rect.center[0]) < 0.5*(E.rect.width + self.rect.width):
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
C = clock()

#game loop begins
while True:
    C.update()
    E1.hit(P1)
    E1.move()
    P1.update()
    
    DISPLAYSURF.fill(GREEN)
    P1.draw(DISPLAYSURF)
    E1.draw(DISPLAYSURF)
    E1.accelerate([0,5/60])
    

    pygame.display.update()
    FramePerSec.tick(FPS)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
