import pygame as pg
from pygame.locals import *

def render_lighting(light_sources):
    LIGHT_surface = pg.Surface((455, 270))
    LIGHT_surface.fill((0, 0, 0))
    px_array = pg.PixelArray(LIGHT_surface)
    for source in light_sources:
        x = source[0][0]
        y = source[0][1]
        r = source[1]
        pixels = []

#        for xp in range

    return LIGHT_surface


#x = 200
#y = 200
#r = 10


#for xp in range(x-r, x+r):
#    for yp in range(y-r, y+r):
#        print(f"({xp}, {yp})")
