import pygame as pg
from pygame.locals import *
import os, sys
from math import floor


def toggle_map_editor(game_map, isMouseClicked, current_tile, scroll, mapped_tiles):
    editor_surface = pg.Surface((455, 270))
    display_font = pg.font.SysFont('Helvetica', 15)
    displayInfo = pg.display.Info()
    native_res = (displayInfo.current_w, displayInfo.current_h)
    text_surface = display_font.render(f"Current tile: {current_tile}", False, (255, 0, 0))
    cells = []
    
    #Edit tile
    if isMouseClicked:
        raw_mouse_pos = pg.mouse.get_pos()
        mouse_pos = ((raw_mouse_pos[0]*455)/native_res[0], (raw_mouse_pos[1]*270)/native_res[1])
        tile_found = False
        try:
            y=0
            for layer in mapped_tiles:
                x=0
                for tile in layer:
                    if tile.collidepoint(mouse_pos):
                        tile_found = True
                        game_map[y][x] = str(current_tile)
                        break
                    x+=1
                if tile_found:
                    break
                y+=1
        except IndexError:
            print(f"game_map[{y}][{x}] out of range!")
            IndexErrored = True
        else:
            IndexErroed = False
        if IndexErroed:
            raise IndexError

    #Draw grid
    for y in range(0, len(game_map)):
        pg.draw.rect(editor_surface, (100, 100, 100), pg.Rect(-scroll[0], y*16-scroll[1], len(game_map[0])*16, 1))
    for x in range(0, len(game_map[0])+1):
        pg.draw.rect(editor_surface, (100, 100, 100), pg.Rect(x*16-scroll[0], -scroll[1], 1, (len(game_map)*16)-15))
    
    #Add selected tile text to returned surface
    editor_surface.blit(text_surface, (0,0))
    editor_surface.set_colorkey((0, 0, 0))
    return editor_surface, game_map
