import pygame as pg
from pygame.locals import *
import sys
from scripts.map_editor import toggle_map_editor
import scripts.shaders
import scripts.entities as entities
from random import randint

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
            if num == '3':
                f.write('1')
            else:
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

def pause_menu():
    PAUSE_surface = pg.Surface((455, 270))
    PAUSE_surface.fill((0, 0, 150))
    display_font = pg.font.SysFont('Helvetica', 15)
    text_surface = display_font.render(f"Game Paused", False, (255, 255, 255))
    PAUSE_surface.blit(text_surface, (455//3, 70))
    return PAUSE_surface

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
    
    map_name = "0_1"
    game_map =  load_map(map_name)
    grass_img = pg.image.load(f"{tile_path}1_grass.png")
    grassCOR_img = pg.image.load(f"{tile_path}1_grassCOR.png")
    grassCOR_img.set_colorkey((255, 255, 255))
    dirt_img = pg.image.load(f"{tile_path}1_dirt.png")
    dirtALT_img = pg.image.load(f"{tile_path}1_dirtALT.png")
    background1_img = pg.image.load(f"maps/background/{map_name}-1.png")
    background2_img = pg.image.load(f"maps/background/{map_name}-2.png")
    background3_img = pg.image.load(f"maps/background/{map_name}-3.png")
    background1_img.set_colorkey((255, 255, 255))
    background2_img.set_colorkey((255, 255, 255))
    background3_img.set_colorkey((255, 255, 255))
    background1_pos = 0
    background2_pos = 0
    #TODO
    ALL_ALPHA = 255

    goblin_img = pg.image.load(f"sprites/entities/mob_gobl.png")
    entities_list = [entities.Entity(136, 176, goblin_img)]

    #END TODO

    ANIMATION_timer = 0
    player_img = pg.image.load('sprites/player_animations/idle/idle_1.png')
    player_img.set_colorkey((255, 255, 255))
    player_rect = pg.rect.Rect(3*TILE_SIZE, 2*TILE_SIZE, TILE_SIZE/2, TILE_SIZE)
    player_moving_path = 'sprites/player_animations/moving/moving_'
    player_ymomentum = 0
    player_rotating_left = False
    player_rotating_right= False
    player_rotation = 0
    paused = False
    jumping = False
    onair_timer = 0
    last_orientation = True       #True -> Right |-| False -> Left
    total_gens = 0

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
                ##Pause & Unpause the game
                if event.key == K_p and not paused and not EDITOR_active:
                    paused = True
                elif event.key == K_p and paused:
                    paused = False
                ##Editor inputs
                if event.key == K_m and not EDITOR_active and not paused:
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
                    player_rotation = 0
                if event.key == K_a:
                    moving_left = False
                    player_rotation = 0
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
        ##Background
        SCREEN.blit(background3_img, (0, 0))
        if moving_right:
            background2_pos -= 0.1
            background1_pos -= 0.25
        elif moving_left:
            background2_pos += 0.1
            background1_pos += 0.25

        if background2_pos <= -LOCAL_RESOLUTION[0] or background2_pos >= LOCAL_RESOLUTION[0]:
            background2_pos = 0
        if background1_pos <= -LOCAL_RESOLUTION[0] or background1_pos >= LOCAL_RESOLUTION[0]:
            background1_pos = 0

        SCREEN.blit(background2_img, (background2_pos, 0))
        SCREEN.blit(background2_img, (background2_pos+LOCAL_RESOLUTION[0], 0))
        SCREEN.blit(background2_img, (background2_pos-LOCAL_RESOLUTION[0], 0))
        SCREEN.blit(background1_img, (background1_pos, 0))
        SCREEN.blit(background1_img, (background1_pos+LOCAL_RESOLUTION[0], 0))
        SCREEN.blit(background1_img, (background1_pos-LOCAL_RESOLUTION[0], 0))
    
        ##Foreground
        mapped_tiles = []
        tangible_tiles = []
        y=0
        for layer in game_map:
            x=0
            mapped_tiles.append([])
            for tile in layer:
                mapped_tiles[y].append(Rect(x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1], TILE_SIZE, TILE_SIZE))
                if tile == '1':
                    if total_gens == 0 and randint(0, 100) >= 95:
                        game_map[y][x] = '3'
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
                if tile == '3':
                    SCREEN.blit(dirtALT_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
                if tile != '0' and not EDITOR_active:
                    tangible_tiles.append(Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x+=1
            y+=1
        total_gens += 1

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

        if not EDITOR_active and not paused:
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
        elif EDITOR_active and not paused:
            try:
                if EDITOR_moving_up:
                    player_movement[1] -= 2
                if EDITOR_moving_down:
                    player_movement[1] += 2
            except NameError:
                print("EDITOR_moving_* not yet defined, skipping...")
                print("EDITOR_moving_* not yet defined, skipping...")

        if not paused:
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
        if not EDITOR_active and not paused:
            ANIMATION_timer += 0.05
            if ANIMATION_timer <= 0.3:
                curr_frame = 1
            elif ANIMATION_timer <= 0.6:
                curr_frame = 2
            elif ANIMATION_timer <= 0.9:
                curr_frame = 3
            elif ANIMATION_timer <= 1.2:
                curr_frame = 4
            elif ANIMATION_timer <= 1.5:
                curr_frame = 5
            elif ANIMATION_timer <= 1.8:
                curr_frame = 6
            elif ANIMATION_timer <= 2.1:
                curr_frame = 7
            else:
                curr_frame = 8
                ANIMATION_timer = 0
            player_mv_img = pg.image.load(player_moving_path + str(curr_frame) + '.png')
            player_mv_img.set_colorkey((255, 255, 255))
            if moving_right:
                SCREEN.blit(player_mv_img, (player_rect.x-scroll[0], player_rect.y-scroll[1]))
            elif moving_left:
                SCREEN.blit(pg.transform.flip(player_mv_img, True, False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))
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

        ##Manage entities
        if not paused:
            for entity in entities_list:
                entity.sprite.set_colorkey((255,255,255))
                SCREEN.blit(entity.sprite, (entity.x-scroll[0], entity.y-scroll[1]))
                #entity.update()

        #SCREEN & TIMING UPDATES----------------------------#
        if EDITOR_active:
            try:
                SCREEN.blit(EDITOR_surface, (0,0))
            except NameError:
                print("EDITOR_surface not yet defined, skipping...")
        if paused:
            PAUSE_surface = pause_menu()
            try:
                SCREEN.blit(PAUSE_surface, (0,0))
            except NameError:
                print("PAUSE_surface not yet defined, skipping...")
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
