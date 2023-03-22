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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(BLUE)
pygame.display.set_caption("Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self,v = [0,0]):
        super().__init__() 
        self.vel = v
        self.image = pygame.image.load("mario2.png")
        self.rect = self.image.get_rect()
        self.pixels = pygame.surfarray.array2d(self.image)
        self.rect.center = (SCREEN_WIDTH//2, 0)

    def accelerate(self,v):
        self.vel=[self.vel[i]+v[i] for i in range(2)]
 
    def move(self):
        self.rect.move_ip(self.vel[0],self.vel[1])
        if (self.rect.bottom > SCREEN_HEIGHT + self.rect.height):
            self.rect.top = 0
            self.rect.center = (random.randint(self.rect.width//2,SCREEN_WIDTH-self.rect.width//2),-self.rect.height//2)
            self.vel = [0,0]

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

            self.vel = [p.vx,p.vy]


            #print(f'other pixels: \n{p_pixinter}\nenemy pixels: \n{self.pixels[0:53, 62:67]}')
            

    def draw(self, surface):
        surface.blit(self.image, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("mario2.png")
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

class grass(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("grass.png")
        self.pixels = pygame.surfarray.array2d(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH/2,SCREEN_HEIGHT)
        self.vx = 0
        self.vy = 0

    def move(self,x,y):
        l=(self.rect.center + x, self.rect.center + y)
        self.rect.center = l
    
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
g = grass()

#game loop begins
while True:
    if P1.health > 0:
        C.update()

        E1.move()

        if P1.collision(E1) == 1:
            P1.health+=-(E1.incidence(P1).sum()/1000)*((E1.vel[0]-P1.vx)**2 +(E1.vel[1]-P1.vy)**2)**0.5
            E1.hit(P1)
        if g.collision(E1) == 1:
            E1.hit(g)
        if g.collision(E1) + P1.collision(E1) == 0:
            E1.accelerate([0,10/60])
            
        
        P1.update()
        
        DISPLAYSURF.fill(BLUE)
        g.draw(DISPLAYSURF)
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


