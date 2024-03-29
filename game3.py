import pygame
import random
import sys
import time
from pygame.locals import *
import numpy as np

mass1 = float(input("Mass 1: "))
mass2 = float(input("Mass 2: "))

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
pygame.display.set_caption("Boing!")


class Enemy(pygame.sprite.Sprite):

    def __init__(self,v = [0,0],m = 10):
        super().__init__() 
        #       image properties
        self.image = pygame.image.load("sprites/weird1.png")
        self.rect = self.image.get_rect()
        self.pixels = pygame.surfarray.array2d(self.image)
       
        #       physical properties: velocities, mass, and position, respectively.
        self.vx = v[0]
        self.vy = v[1]
        self.mass = m
        self.rect.center = (SCREEN_WIDTH//2, self.rect.height/2)
 
    def move(self):
        #bounce off screen border
        if self.rect.top < 0:
            self.vy = abs(self.vy)
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.vy = -abs(self.vy)
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.left < 0:
            self.vx = abs(self.vx)
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.vx = -abs(self.vx)
            self.rect.right = SCREEN_WIDTH

        #move with specified velocity
        self.rect.move_ip(self.vx,self.vy)

    def tangent(self,p,inc): #when self and p overlap pixels, tangent will determine the tangent direction of collision
        #number of pixels in overlap
        N = inc.sum() 
        #initialize lists for determining diagonal/anti-diagonal and vertical/horizontal occurence in pixel overlap
        diags = [] 
        cartesians = []
        #do the count (is this memory efficient? probably not)
        if N > 0:
            for i in range(inc.shape[0]):
                for j in range(inc.shape[1]):
                    if inc[i,j] == 1:
                        diags.append(np.array([inc[i-1,j-1],inc[i-1,j+1]]))
                        cartesians.append(np.array([inc[i-1,j],inc[i,j+1]]))
            #determine counts. D = [#diag, #anti-diag], C=[#horizontal, #vertical]
            D=sum(diags)
            C=sum(cartesians)
            #find least-occured-direction magnitude
            md = min(D)
            mc = min(C)
            #remove least-occured directions
            D = D-md
            C = C-mc
            #initialize directions
            v1=np.array([-1,-1])
            v2=np.array([0,-2**0.5])
            v3=np.array([1,-1])
            v4=np.array([2**0.5,0])
            #take the linear combination determined by reduced counts; normalize tangent direction vector.
            tang=D[0]*v1 + C[0]*v4 + D[1]*v3 + C[1]*v2
            norm2 = tang.dot(tang)
            if norm2 !=0:
                tang=tang/(norm2**0.5)
            return tang
 
    def normal(self,p,inc): #determines normal direction of pixel overlap
        if inc.sum() > 0:
            v = self.tangent(p,inc)
            w=np.array([-v[1],v[0]])
            return w

    def incidence(self,p): 
        #returns a matrix with #rows/#cols corresponding to horiz/vert. pixels in the overlap between... 
        #self.rect and p.rect. The matrix value @(i,j) is 1 if both images are present at that pixel, else 0.
        if p.rectoverlap(self) == 1:
            #define shorter names for rect.center positions
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
            
            #make matrices for the pixels just in overlap
            p_pixinter = p.pixels[rxp1:rxp2, ryp1:ryp2]
            s_pixinter = self.pixels[rxs1:rxs2, rys1:rys2]

            #initialize a zero-matrix of the same size as overlap
            nrows = rxp2-rxp1
            ncols = ryp2-ryp1
            inc = np.zeros((nrows,ncols))

            #change relevant values to 1
            for i in range(nrows):
                for j in range(ncols):
                    if p_pixinter[i,j] != 0 and s_pixinter[i,j] != 0:
                        inc[i,j] = 1
        else:
            #if no overlap is present, return 0-vector
            inc = np.array([0])

        return inc

    def clipout(self, p, normal): #will clip two images apart in the shortest direction possible
        #declare position vectors
        vs = np.array(self.rect.center)
        vp = np.array(p.rect.center)
        #masses
        ms = self.mass
        mp = p.mass
        M = ms + mp
        #determine incidence/overlap
        inc = self.incidence(p)
        #start a step counter, and magnitude of initial incidence (=s0,and s1)
        step = 0
        s0 = inc.sum()
        s1 = s0
        #start parity of normal direction at +
        par = 1

        while inc.sum() > 0 and step < 10:
            #move positions in opposite normal directions
            vs = vs + (mp*par / M)*normal
            vp = vp - (ms*par / M)*normal
            self.rect.center = (vs[0],vs[1])
            p.rect.center = (vp[0],vp[1])
            #recalculate incidence
            inc = self.incidence(p)
            #check if the incidence magnitude got worse, if so then reverse the parity (change direction)
            if inc.sum() > (s0+s1)/2:
                par = -2*par
            #update prior incidence magnitudes and step counter
            s1 = s0
            s0=inc.sum()
            step += 1

        #print the number of steps taken (for debugging)
        print(step)

    def clipout2(self, p): #will clip two images apart in the shortest direction possible
        #declare position vectors

        #masses
        ms = self.mass
        mp = p.mass
        M = ms + mp
        #determine incidence/overlap
        inc = self.incidence(p)
        s0 = inc.sum()
        normal = self.normal(p,inc)
        #start a step counter, and magnitude of initial incidence (=s0,and s1)
        step = 1
        #start parity of normal direction at +
        scale = (s0**0.5)/2

        while inc.sum() > 0 and step < 100:

            print(f'step = {step}')
            print(f's0 = {inc.sum()}')
            vs = np.array(self.rect.center)
            vp = np.array(p.rect.center)

            vs1 = vs + scale*(mp / M)*normal
            vp1 = vp - scale*(ms / M)*normal
            vs2 = vs - scale*(mp / M)*normal
            vp2 = vp + scale*(ms / M)*normal

            self.rect.center = (vs1[0],vs1[1])
            p.rect.center = (vp1[0],vp1[1])
            inc1 = self.incidence(p)
            s1 = inc1.sum()

            self.rect.center = (vs2[0],vs2[1])
            p.rect.center = (vp2[0],vp2[1])
            inc2 = self.incidence(p)
            s2 = inc2.sum()
            
            if s2 > s1 and s1 < s0:
                self.rect.center = (vs1[0],vs1[1])
                p.rect.center = (vp1[0],vp1[1])
                inc = inc1
            elif s2 < s0:
                inc = inc2
            else:
                print('Whoops! Now ya fucked up!!!!')

            
            print(f's1 = {s1}')
            print(f's2 = {s2}')
            step += 1

        print(f'normal = {normal}')
        #print the number of steps taken (for debugging)

                
    def hit2(self,p,inc,normal): #transfer momentum between self and p along a specified direction of intersection
        if p.rectoverlap(self) == 1:
            mp = p.mass
            ms = self.mass
            M = ms + mp
            DM = ms - mp
            xp=p.rect.center[0]
            yp=p.rect.center[1]
            xs=self.rect.center[0]
            ys=self.rect.center[1]
            vs=np.array([self.vx,self.vy])
            vp=np.array([p.vx,p.vy])

            if inc.sum() > 0:
                #determine normal (_l) and tangent (ll) projections of velocities
                vs_l = (vs.dot(normal))*normal
                vsll = vs - vs_l
                vp_l = (vp.dot(normal))*normal
                vpll = vp - vp_l
                #set post-collision velocity vectors and update self and p velocities
                us = (2*mp*vp_l + DM*vs_l)/M + vsll
                up = (2*ms*vs_l - DM*vp_l)/M + vpll
                self.vx=us[0]
                self.vy=us[1]
                p.vx=up[0]
                p.vy=up[1]

    def draw(self, surface):
        surface.blit(self.image, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self,m = 10):
        super().__init__()
        #   image properties 
        self.image = pygame.image.load("sprites/Ball7.png")
        self.pixels = pygame.surfarray.array2d(self.image)
        self.rect = self.image.get_rect()

        #   physics properties
        self.rect.center = (SCREEN_WIDTH//2, 3*SCREEN_HEIGHT//4)
        self.acc = 5
        self.vx = 0
        self.vy = 0
        self.mass = m
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()

        #LSHIFT = acceleration modifier
        if pressed_keys[K_LSHIFT]:
            self.acc = 10
        else:
            self.acc = 5

        #vertical movement
        if pressed_keys[K_w]:
            self.vy += - self.acc/FPS
        elif pressed_keys[K_s]:
            self.vy += self.acc/FPS
        else:
            self.vy += 0

        #horizontal movement
        if pressed_keys[K_a]:
            self.vx += -self.acc/FPS
        elif pressed_keys[K_d]:
            self.vx += self.acc/FPS
        else:
            self.vx += 0

        #bounce off screen border
        if self.rect.top < 0:
            self.vy = abs(self.vy)
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_HEIGHT:
            self.vy = -abs(self.vy)
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.left < 0:
            self.vx = abs(self.vx)
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.vx = -abs(self.vx)
            self.rect.right = SCREEN_WIDTH

        #spacebar is the brake
        if pressed_keys[K_SPACE]:
            self.vx = self.vx/1.5
            self.vy = self.vy/1.5
        
        #move image
        self.rect.move_ip(self.vx, self.vy)
        

    def rectoverlap(self,E): #determines if the image rectange of self and E overlap (1) or don't (0).
        hori = (E.rect.right > self.rect.left and E.rect.left < self.rect.right)
        vert = (E.rect.bottom > self.rect.top and E.rect.top < self.rect.bottom)
        val = int(hori and vert)
        return val
 
    def draw(self, surface):
        surface.blit(self.image, self.rect) 
        #surface.blit(font.render(f'Health: {round(self.health,1)}', True, WHITE), (20,20) )
        surface.blit(font.render(f'Mass: {self.mass}', True, WHITE), (20,40) )
        surface.blit(font.render(f'Velocity: [{round(self.vx,2)},{round(self.vy,2)}]', True, WHITE), (20,60) )
         
P1 = Player(mass1)
E1 = Enemy([0,5],mass2)
normal=np.array([0,0])
s1 = 0
s2 = 0
#minimum overlap threshold:
thresh = 50
#game loop begins
while True:

    E1.move()
    P1.update()
    pce = P1.rectoverlap(E1)
    inc = E1.incidence(P1)

    #current overlap size
    s1 = inc.sum()
    
    #if overlap present
    if s1 > thresh:

        #determine normal direction of collision
        normal = E1.normal(P1,inc)

    #if no overlap on previous frame, and a new overlap just occured, then transfer momentum:
    if s2 <= thresh and s1 > thresh:
        E1.hit2(P1,inc,normal)



    #if there was a prior overlap, but the current overlap is worse, then clip the objects apart
    if s2 > thresh and s1 >= s2:
        E1.clipout2(P1)
        #reset the prior overlap to zero, so that a new collision can occur if necessary on the next frame
        s2 = 0
    else:
        s2 = s1

    #fill background
    DISPLAYSURF.fill(BLUE)
    
    #show normal direction of last overlap
    DISPLAYSURF.blit(font.render(f'Coll. Normal = {normal}', True, WHITE), (20,80) )

    #DISPLAYSURF.blit(font.render(f'Act. Normal = {act_normal}', True, WHITE), (20,100) )
    #DISPLAYSURF.blit(font.render(f'Error = {err_val}', True, WHITE), (20,120) )      

    #draw entities  
    P1.draw(DISPLAYSURF)
    E1.draw(DISPLAYSURF)

    #update the display
    pygame.display.update()
    #progress the clock?
    FramePerSec.tick(FPS)

    #allow for exiting the game
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()


