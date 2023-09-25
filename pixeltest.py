import pygame
import random
import sys
import time
from pygame.locals import *
import numpy as np

pygame.init()

image = pygame.image.load("sprites/Ball3.png")
rect = image.get_rect()
pixels = pygame.surfarray.array2d(image)
x1=int(input("Row start: "))
x2=int(input("Row end: "))
y1=int(input("Col start: "))
y2=int(input("Col end: "))
d= pixels[x1:x2][y1:y2]
print(d)
print(d.sum())
print(pixels.shape)
