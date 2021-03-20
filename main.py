import pygame as pg
from pygame.locals import *
import sys
from scripts.map_editor import toggle_map_editor

def load_map(path):
    f = open('maps/' + path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for line in data:
        game_map.append(list(line))
    return game_map

def save_map(path, game_map):
    f = open('maps/' + path + '.txt', 'w')
    for line in game_map:
        f.write('\n')
        for num in line:
            f.write(num)
    f.close()

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
    grassCOR_img = pg.image.load(f"{tile_path}1_grassCOR.png")
    grassCOR_img.set_colorkey((255, 255, 255))
    dirt_img = pg.image.load(f"{tile_path}1_dirt.png")

    player_img = pg.image.load('sprites/player_animations/idle/idle_1.png')
    player_img.set_colorkey((255, 255, 255))
    player_rect = pg.rect.Rect(3*TILE_SIZE, 2*TILE_SIZE, TILE_SIZE/2, TILE_SIZE)
    player_ymomentum = 0
    jumping = False
    onair_timer = 0
    last_orientation = True       #True -> Right |-| False -> Left

    precise_scroll = [player_rect.x, player_rect.y]
    
    EDITOR_active = False
    EDITOR_current_tile = 0
    EDITOR_isMouseClicked = False
    EDITOR_moving_up = False
    EDITOR_moving_down = False
    TILE_TYPES = 2

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
                ##Editor inputs
                if event.key == K_m and not EDITOR_active:
                    EDITOR_active = True
                elif event.key == K_m and EDITOR_active:
                    EDITOR_active = False
                    save_map("0_1", game_map)                   #Save map
                    precise_scroll[0] = 0                       #Reset camera
                    precise_scroll[1] = 0
                    player_rect.x = 3*TILE_SIZE                 #Reset player position
                    player_rect.y = 2*TILE_SIZE
                if event.key == K_w and EDITOR_active:
                    EDITOR_moving_up = True
                if event.key == K_s and EDITOR_active:
                    EDITOR_moving_down = True

            if event.type == KEYUP:
                if event.key == K_d:
                    moving_right = False
                if event.key == K_a:
                    moving_left = False
                if event.key == K_SPACE and jumping:
                    jumping = False
                ##Editor inputs
                if event.key == K_w:
                    EDITOR_moving_up = False
                if event.key == K_s:
                    EDITOR_moving_down = False

            if event.type == MOUSEBUTTONDOWN:
                ##Editor inputs
                if event.button == 1 and EDITOR_active:
                    EDITOR_isMouseClicked = True
                if event.button == 3 and EDITOR_active:
                    if EDITOR_current_tile == TILE_TYPES:
                        EDITOR_current_tile = 0
                    else:
                        EDITOR_current_tile += 1

        #CAMERA------------------------------------------#
        if not EDITOR_active:
            precise_scroll[0] += (player_rect.x-precise_scroll[0]-(454/2 + 4))/20
            precise_scroll[1] += (player_rect.y-precise_scroll[1]-(LOCAL_RESOLUTION[1]/2 + 4))/20
        else:
            precise_scroll[0] += player_rect.x-precise_scroll[0]-(454/2 + 4)
            precise_scroll[1] += player_rect.y-precise_scroll[1]-(LOCAL_RESOLUTION[1]/2 + 4)
        scroll = precise_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        #DRAWING-----------------------------------------#
        mapped_tiles = []
        tangible_tiles = []
        y=0
        for layer in game_map:
            x=0
            mapped_tiles.append([])
            for tile in layer:
                mapped_tiles[y].append(Rect(x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1], TILE_SIZE, TILE_SIZE))
                if tile == '1': 
                    SCREEN.blit(dirt_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                elif tile == '2': 
                    try:
                        if game_map[y][x+1] == '0':
                            SCREEN.blit(grassCOR_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                    except IndexError:
                        if x == len(layer)-1 and game_map[y][x-1] == '0':
                            SCREEN.blit(pg.transform.flip(grassCOR_img, True, False), (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                        elif x == len(layer)-1:
                            SCREEN.blit(grassCOR_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                    try:
                        if game_map[y][x-1] == '0':
                            SCREEN.blit(pg.transform.flip(grassCOR_img, True, False), (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                    except IndexError:
                        if x == 0 and game_map[y][x+1] == '0':
                            SCREEN.blit(grassCOR_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                        elif x == 0:
                            SCREEN.blit(pg.transform.flip(grassCOR_img, True, False), (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                    try:
                        if (game_map[y][x-1] == '0' and game_map[y][x+1] == '0') or (game_map[y][x-1] != '0' and game_map[y][x+1] != '0'):
                            SCREEN.blit(grass_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                        if x == 0 and game_map[y][x+1] == '0':
                            SCREEN.blit(grassCOR_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                    except IndexError:
                        pass
                if tile != '0' and not EDITOR_active:
                    tangible_tiles.append(Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x+=1
            y+=1

        #Movement & Collision--------------------------#
        player_movement = [0, 0]
        if not EDITOR_active:
            player_last_place = player_movement

        if moving_right:
            player_movement[0] += 2
            last_orientation = True
        if moving_left:
            player_movement[0] -= 2
            last_orientation = False

        if not EDITOR_active:
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
        else:
            try:
                if EDITOR_moving_up:
                    player_movement[1] -= 2
                if EDITOR_moving_down:
                    player_movement[1] += 2
            except NameError:
                print("EDITOR_moving_* not yet defined, skipping...")

        player_rect, collisions = move(player_rect, player_movement, tangible_tiles)
        
        if not EDITOR_active:
            if collisions['bottom'] and onair_timer > 0:
                onair_timer = 0
                jumping = False
                player_ymomentum = 1
            elif not collisions['bottom']:
                onair_timer += 1

            if collisions['top']:    
                player_ymomentum = 1
            
        ##Draw player or editor surface
        if not EDITOR_active:
            if moving_right:
                SCREEN.blit(player_img, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
            elif moving_left:
                SCREEN.blit(pg.transform.flip(player_img, True, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))
            else:
                if last_orientation:
                    SCREEN.blit(player_img, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
                else:
                    SCREEN.blit(pg.transform.flip(player_img, True, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))
        if EDITOR_active:
            ##Map editor related code (Update map info and add screen elements)
            try:
                EDITOR_surface, game_map = toggle_map_editor(game_map, EDITOR_isMouseClicked, EDITOR_current_tile, scroll, mapped_tiles)
            except NameError:
                EDITOR_surface, game_map = toggle_map_editor(game_map, None, EDITOR_current_tile, scroll, mapped_tiles)
            EDITOR_isMouseClicked = False

        #SCREEN & TIMING UPDATES----------------------------#
        if EDITOR_active:
            try:
                SCREEN.blit(EDITOR_surface, (0,0))
            except NameError:
                print("EDITOR_surface not yet defined, skipping...")
        pg.transform.scale(SCREEN, RESOLUTION, FSCREEN)
        pg.display.update()
        CLOCK.tick(60)
        
        #DEBUGGING SECTION----------------------------------#
#        print(f"topColi = {collisions['top']} ||| bottomColi = {collisions['bottom']}")
#        if collisions['top']:
#            pg.image.save(FSCREEN, f"debug/{debug_var}.png")
#            debug_var += 1
#        print(EDITOR_current_tile)       
    
    pg.quit()
