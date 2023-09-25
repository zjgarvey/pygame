import pygame
import random
import sys
import time
from pygame.locals import *
import numpy as np

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
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(BLUE)
pygame.display.set_caption("Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self,v = [0,0]):
        super().__init__() 
        self.vx= v[0]
        self.vy = v[1]

        self.image = pygame.image.load("sprites/mario2.png")
        self.rect = self.image.get_rect()
        self.pixels = pygame.surfarray.array2d(self.image)
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//4)

    def accelerate(self,v):
        self.vx+=v[0]
        self.vy+=v[1]
 
    def move(self):

        if self.rect.top < 0:
            self.vy = -self.vy
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.vy = -self.vy
            self.rect.bottom = SCREEN_HEIGHT

        if self.rect.left < 0:
            self.vx = -self.vx
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.vx = -self.vx
            self.rect.right = SCREEN_WIDTH

        self.rect.move_ip(self.vx,self.vy)



    def incidence(self,p):
        if p.collision(self) == 1:
            xp=p.rect.center[0]
            yp=p.rect.center[1]
            xs=self.rect.center[0]
            ys=self.rect.center[1]
            
            

            #player-pixel-relative x-interval of intersection
            rxp1 = max([p.rect.left,self.rect.left]) - p.rect.left
            rxp2 = min([self.rect.right, p.rect.right]) - p.rect.left
            #enemy(self)-pixel-relative x-interval of intersection
            rxs1 = max([self.rect.left,p.rect.left]) - self.rect.left
            rxs2 = min([p.rect.right,self.rect.right]) - self.rect.left

            #player-pixel-relative y-interval of intersection
            ryp1 = max([self.rect.top, p.rect.top]) - p.rect.top
            ryp2 = min([p.rect.bottom, self.rect.bottom]) - p.rect.top
            #enemy(self)-pixel-relative y-interval of intersection
            rys1 = max([self.rect.top,p.rect.top]) - self.rect.top
            rys2 = min([self.rect.bottom,p.rect.bottom]) - self.rect.top

            #print(f'other intervals = {[[rxp1,rxp2],[ryp1,ryp2]]}, enemy intervals = {[[rxs1,rxs2],[rys1,rys2]]}')
            

            p_pixinter = p.pixels[rxp1:rxp2, ryp1:ryp2]
            s_pixinter = self.pixels[rxs1:rxs2, rys1:rys2]

            nrows = rxp2-rxp1
            ncols = ryp2-ryp1
            inc = np.zeros((nrows,ncols))

            for i in range(nrows):
                for j in range(ncols):
                    if p_pixinter[i,j] != 0 or s_pixinter[i,j] != 0:
                        inc[i,j] = 1

            return inc


    def hit(self, p):
        if p.collision(self) == 1:
            xp=p.rect.center[0]
            yp=p.rect.center[1]
            xs=self.rect.center[0]
            ys=self.rect.center[1]
            
            inc=self.incidence(p)

            if inc.sum() !=0:
                if inc.shape[0] < inc.shape[1]: #then push self out of player horizontally
                    B=inc.transpose()
                    ls=[sum(B[i]) for i in range(B.shape[0])]
                    l=max(ls)
                    c=list(self.rect.center)
                    if xs > xp:
                        c[0]+=l
                    else:
                        c[0]+=-l
                    self.rect.center = tuple(c)
                else: #push self out of player veritcally      
                    ls=[sum(inc[i]) for i in range(inc.shape[0])]
                    l=max(ls)
                    c=list(self.rect.center)
                    if ys > yp:
                        c[1]+=l
                    else:
                        c[1]+=-l
                    self.rect.center = tuple(c)

                v=[self.vx,self.vy]
                self.vx = p.vx
                self.vy = p.vy
                p.vx = v[0]
                p.vy = v[1]


            #print(f'other pixels: \n{p_pixinter}\nenemy pixels: \n{self.pixels[0:53, 62:67]}')
            
    def hit2(self, p): #(old) rectangular collision only
        if p.collision(self) == 1:
            xp=p.rect.center[0]
            yp=p.rect.center[1]
            xs=self.rect.center[0]
            ys=self.rect.center[1]
            
            inc=self.incidence(p)
            v=[self.vx,self.vy]

            if inc.sum() > 0:
                if inc.shape[0] < inc.shape[1]: #then push self out of player horizontally
                    B=inc.transpose()
                    ls=[sum(B[i]) for i in range(B.shape[0])]
                    l=max(ls)
                    c=list(self.rect.center)
                    if xs > xp:
                        c[0]+=l
                    else:
                        c[0]+=-l
                    self.rect.center = tuple(c)
                    self.vx = p.vx
                    p.vx = v[0]
                else: #push self out of player veritcally      
                    ls=[sum(inc[i]) for i in range(inc.shape[0])]
                    l=max(ls)
                    c=list(self.rect.center)
                    if ys > yp:
                        c[1]+=l
                    else:
                        c[1]+=-l
                    self.rect.center = tuple(c)
                    self.vy = p.vy
                    p.vy = v[1]

    def draw(self, surface):
        surface.blit(self.image, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("sprites/mario2.png")
        self.pixels = pygame.surfarray.array2d(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH//2, 3*SCREEN_HEIGHT//4)
        self.health=100
        self.speed = 5
        self.vx = 0
        self.vy = 0
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()

        #speed
        if pressed_keys[K_LSHIFT]:
            self.speed = 10
        else:
            self.speed = 5

        #vertical movement
        if pressed_keys[K_w]:
            self.vy += - self.speed/FPS
        elif pressed_keys[K_s]:
            self.vy += self.speed/FPS
        else:
            self.vy += 0

        #horizontal movement
        if pressed_keys[K_a]:
            self.vx += -self.speed/FPS
        elif pressed_keys[K_d]:
            self.vx += self.speed/FPS
        else:
            self.vx += 0

        if self.rect.top < 0:
            self.vy = -self.vy
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.vy = -self.vy
            self.rect.bottom = SCREEN_HEIGHT

        #Screen Edge Collision
        if self.rect.left < 0:
            self.vx = -self.vx
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.vx = -self.vx
            self.rect.right = SCREEN_WIDTH

            
        self.rect.move_ip(self.vx, self.vy)

        if pressed_keys[K_SPACE]:
            self.vx = self.vx/2
            self.vy = self.vy/2

    def collision(self,E):
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
    if P1.health > 0:
        C.update()
        E1.move()
        P1.update()
        E1.hit2(P1)

        DISPLAYSURF.fill(BLUE)
        P1.draw(DISPLAYSURF)
        E1.draw(DISPLAYSURF)

        pygame.display.update()
        FramePerSec.tick(FPS)
    else:
        if int(time.time()) % 2 == 0:
            DISPLAYSURF.fill(BLACK)
        else: 
            DISPLAYSURF.fill(RED)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()


