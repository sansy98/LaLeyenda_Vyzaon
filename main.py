import pygame as pg
from pygame.locals import *
import sys


def load_map(path):
    f = open('maps/' + path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for line in data:
        game_map.append(list(line))
    return game_map

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_states = {'top': False, 'bottom': False, 'right': False, 'left': False}

    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_states['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_states['left'] = True

    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_states['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_states['top'] = True
    
    return rect, collision_states


if __name__ == "__main__":
    
    pg.init()
    CLOCK = pg.time.Clock()

    displayInfo = pg.display.Info()
    RESOLUTION = (displayInfo.current_w, displayInfo.current_h)
    LOCAL_RESOLUTION = (455, 270)           #(57, 34)
    FSCREEN = pg.display.set_mode(RESOLUTION, pg.FULLSCREEN)
    SCREEN = pg.Surface(LOCAL_RESOLUTION)

    TILE_SIZE = 16
    tile_path = 'sprites/tiles/'

    moving_right = False
    moving_left = False

    game_map =  load_map("0_1")
    grass_img = pg.image.load(f"{tile_path}1_grass.png")
    dirt_img = pg.image.load(f"{tile_path}1_dirt.png")

    player_img = pg.image.load('sprites/player_animations/idle/idle_0.png')
    player_img.set_colorkey((255, 255, 255))
    player_rect = pg.rect.Rect(3*TILE_SIZE, 2*TILE_SIZE, TILE_SIZE/2, TILE_SIZE)
    player_ymomentum = 0
    jumping = False
    onair_timer = 0
    last_orientation = True       #True -> Right |-| False -> Left

    precise_scroll = [player_rect.x, player_rect.y]
    

    #Debug vars, ignore these
    #debug_var = 0


    while True:
        SCREEN.fill((0, 200, 240))

        #Events/Buttons----------------------------------#
        for event in pg.event.get():
            if event.type == QUIT:  
                pg.quit()
                break

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: 
                    pg.quit()
                    sys.exit()
                if event.key == K_d:
                    moving_right = True
                if event.key == K_a:
                    moving_left = True
                if event.key == K_SPACE and onair_timer == 0:    
                    jumping = True

            if event.type == KEYUP:
                if event.key == K_d:
                    moving_right = False
                if event.key == K_a:
                    moving_left = False
                if event.key == K_SPACE and jumping:
                    jumping = False

        #CAMERA------------------------------------------#
        precise_scroll[0] += (player_rect.x-precise_scroll[0]-(454/2 + 4))/20
        precise_scroll[1] += (player_rect.y-precise_scroll[1]-(LOCAL_RESOLUTION[1]/2 + 4))/20
        scroll = precise_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        #DRAWING-----------------------------------------#
        tangible_tiles = []
        y=0
        for layer in game_map:
            x=0
            for tile in layer:
                if tile == '2': 
                    SCREEN.blit(grass_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                elif tile == '1': 
                    SCREEN.blit(dirt_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                if tile != '0':
                    tangible_tiles.append(Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x+=1
            y+=1

        #Movement & Collision--------------------------#
        player_movement = [0, 0]
        if moving_right:
            player_movement[0] += 2
            last_orientation = True
        if moving_left:
            player_movement[0] -= 2
            last_orientation = False

        player_movement[1] += player_ymomentum
        if jumping:
            if onair_timer == 0:
                player_ymomentum = -2
            player_ymomentum += -0.2
        else: player_ymomentum += 0.2
        if onair_timer > 8:
            jumping = False
        if player_ymomentum > 3:
            player_ymomentum = 3
        
        player_rect, collisions = move(player_rect, player_movement, tangible_tiles)

        if collisions['bottom'] and onair_timer > 0:
            onair_timer = 0
            jumping = False
            player_ymomentum = 1
        elif not collisions['bottom'] and jumping:
            onair_timer += 1
            print(onair_timer)
        if collisions['top']:    
            player_ymomentum = 1
        
        if moving_right:
            SCREEN.blit(player_img, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
        elif moving_left:
            SCREEN.blit(pg.transform.flip(player_img, True, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))
        else:
            if last_orientation:
                SCREEN.blit(player_img, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
            else:
                SCREEN.blit(pg.transform.flip(player_img, True, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))

        #SCREEN & TIMING UPDATES----------------------------#

        pg.transform.scale(SCREEN, RESOLUTION, FSCREEN)
        pg.display.update()
        CLOCK.tick(60)
        
        #DEBUGGING SECTION----------------------------------#
#        print(f"topColi = {collisions['top']} ||| bottomColi = {collisions['bottom']}")
#        if collisions['top']:
#            pg.image.save(FSCREEN, f"debug/{debug_var}.png")
#            debug_var += 1
        
    pg.quit()
