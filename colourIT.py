import pygame, random, math, csv, json, os
from os import listdir
from os.path import isfile, join

pygame.font.init()
pygame.mixer.init()

#windows setup 
WIDTH, HEIGHT = 1280, 720 
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) 

FPS = 24

MUSIC_ON = True

#START OF ENTITY SPRITE AND MOVEMENT--------------------------------------------------------------------------
PLAYER_VEL = 5

def flip (sprites):
    return [pygame.transform.flip(sprite, True, False)for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile (join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

#PLAYER SPRITTE
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacter", "Sketch", 150, 150, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.melee_attack = False

#MOVEMENT FUNC
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"

            if not self.melee_attack:
                self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"

            if not self.melee_attack:
                self.animation_count = 0

    def melee(self):
        if not self.melee_attack:
            self.melee_attack = True
            self.animation_count = 0

    def loop(self, fps):
        # self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.x_vel != 0:
            sprite_sheet = "run"

        if self.melee_attack:
            sprite_sheet = "melee"

        sprite_sheet_name = sprite_sheet + "_" + self.direction

        sprites = self.SPRITES[sprite_sheet_name]
        if self.melee_attack:
            total_duration = len(sprites) * self.ANIMATION_DELAY
            
            if self.animation_count >= total_duration:
                self.melee_attack = False
                self.animation_count = 0
                sprites = self.SPRITES["idle_" + self.direction]
                sprite_index = 0
            else:
                sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        else:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
    
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))

def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)
    if keys[pygame.K_SPACE]:
        player.melee()
    

def draw_player(player): 
    player.draw(WINDOW)

#END OF MAIN CHARACTER/PLAYER SPRITE AND MOVEMENT--------------------------------------------------------------------------


#MAP SETTING TEST (WILL CHANGE MAP AFTERWARDS) --------------------------------------------------------------------------
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet, scale = 1):
        pygame.sprite.Sprite.__init__(self)
        original_image = spritesheet.parse_sprite(image)
        self.image = pygame.transform.scale(original_image, 
                                           (int(original_image.get_width() * scale), 
                                            int(original_image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
    
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        
class TileMap():
    def __init__(self, test_level, spritesheet, scale = 1):
        self.tile_size = 16 * scale
        self.scale = scale
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.map_w, self.map_h = 0, 0
        self.tiles = self.load_tiles(test_level)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()
        
    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))
        
    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)
    
    def read_csv(self, test_level):
        map = []
        with open(os.path.join(test_level)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data: map.append(list(row))
            return map
    
    def load_tiles(self, test_level):
        tiles = []
        map = self.read_csv(test_level)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:
                if tile == '-1':
                    self.start_x, self.start_y = x * self.tile_size, y * self.tile_size 
                elif tile == '0':
                    tiles.append(Tile('green.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '1':
                    tiles.append(Tile('blue.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '2':
                    tiles.append(Tile('brown.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                x += 1
            y += 1
        
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles 
#MAP SETTING TEST END ---------------------------------------------------------------------------------------------------

# fonts for main menu's text 
TITLE_FONT = pygame.font.SysFont("comicsans", 80)
BUTTON_FONT = pygame.font.SysFont("comicsans", 40)

# buttons dimensions
BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING = 600, 80, 30
PAUSE_BUTTON_SIDE = 50
PAUSE_BUTTON_MARGIN = 20

# buttons positions
BUTTON_X = WIDTH//2 - BUTTON_WIDTH//2
TITLE_Y = 50
NEW_GAME_BUTTON_Y = 200
LOAD_GAME_BUTTON_Y = NEW_GAME_BUTTON_Y + BUTTON_HEIGHT + BUTTON_SPACING
SETTINGS_Y = LOAD_GAME_BUTTON_Y + BUTTON_HEIGHT + BUTTON_SPACING
QUIT_Y = SETTINGS_Y + BUTTON_HEIGHT + BUTTON_SPACING

BGM_BUTTON_Y = 200

#colours constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHT_GREY = (200, 200, 200)
PURPLE = (150, 0, 200)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)



def draw_button(text, x, y, width, height, mouse_pos):

    button = pygame.Rect(x, y, width, height)

    if button.collidepoint(mouse_pos):
        pygame.draw.rect(WINDOW, GREY, button)
    else:
        pygame.draw.rect(WINDOW, BLACK, button)

    # drawing border
    pygame.draw.rect(WINDOW, BLACK, button, 3)

    # draw text at the center 
    button_text = BUTTON_FONT.render(text, 1, WHITE)
    text_x = x + (width - button_text.get_width()) // 2
    text_y = y + (height - button_text.get_height()) // 2
    WINDOW.blit(button_text, (text_x, text_y))

    return button

def draw_pause_button(mouse_pos):
    button_x = WIDTH - PAUSE_BUTTON_SIDE - PAUSE_BUTTON_MARGIN
    button_y = PAUSE_BUTTON_MARGIN
    button = pygame.Rect(button_x, button_y, PAUSE_BUTTON_SIDE, PAUSE_BUTTON_SIDE)
    if button.collidepoint(mouse_pos):
        pygame.draw.rect(WINDOW, RED, button)
    else:
        pygame.draw.rect(WINDOW, ORANGE, button)

    return button

def save_game(player):
    save_data = {
        "player_x": player.rect.x,
        "player_y": player.rect.y,
    }
    file = open('savegame.json', 'w')
    json.dump(save_data, file)
    file.close()
    print("Game Saved!")

def load_game(player): 
    file = open('savegame.json', 'r')
    save_data = json.load(file)
    file.close()
    player.rect.x = save_data["player_x"]
    player.rect.y = save_data["player_y"]
    print("Game Loaded!")

def if_save_exists():
    return os.path.exists('savegame.json')

class Camera:
    def __init__(self, map_width, map_height):
        self.offset_x = 0
        self.offset_y = 0
        self.map_width = map_width
        self.map_height = map_height 
    def get_offset_position(self, entity):
        screen_x = entity.rect.x + self.offset_x
        screen_y = entity.rect.y + self.offset_y
        return pygame.Rect(screen_x, screen_y, entity.rect.width, entity.rect.height)
    def follow_player(self, player):
        self.offset_x = -player.rect.centerx + WIDTH//2 
        self.offset_y = -player.rect.centery + HEIGHT//2

def main():
    player = Player(100, 100, 50, 50)
    pygame.display.set_caption("Colour IT!")
    clock = pygame.time.Clock()

    page = 0
    pause = False
    
    # load map declares..?
    class SpriteSheet:
        def parse_sprite(self, name):
            path = join("assets", "LevelMap", name)
            return pygame.image.load(path).convert_alpha()
    
    spritesheet = SpriteSheet()
    tile_map = TileMap('assets/LevelMap/test_level.csv', spritesheet, scale = 3) #also scales up the map here

    camera = Camera(tile_map.map_w, tile_map.map_h) 

    pygame.mixer.music.load('assets/Sounds/background_music.wav')
    pygame.mixer.music.play(-1)

    run = True
    while run: 
        global WINDOW, MUSIC_ON
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        
        if page == 0: #main menu page 
            WINDOW.fill(GREY)
            title_text = TITLE_FONT.render("Colour IT!", 1, BLACK)
            WINDOW.blit(title_text, ((WIDTH//2 - title_text.get_width()//2, TITLE_Y)))

            NEW_GAME_BUTTON = draw_button("New Game", BUTTON_X, NEW_GAME_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            LOAD_GAME_BUTTON = draw_button("Load Game", BUTTON_X, LOAD_GAME_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            SETTINGS_BUTTON = draw_button("Settings", BUTTON_X, SETTINGS_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            QUIT_BUTTON = draw_button("Quit Game", BUTTON_X, QUIT_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 1: #new game page 
            if pause == False:
                WINDOW.fill(WHITE)

                handle_move(player)
                player.loop(FPS)

                PAUSE_BUTTON = draw_pause_button(mouse_pos)

                camera.follow_player(player)
                for tile in tile_map.tiles:
                    tile_screen_position = camera.get_offset_position(tile)
                    WINDOW.blit(tile.image, tile_screen_position)
                player_screen_position = camera.get_offset_position(player)
                WINDOW.blit(player.sprite, player_screen_position)

            elif pause == True:
                WINDOW.fill(WHITE)
                draw_player(player)
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill(GREY)
                overlay.set_alpha(128)
                WINDOW.blit(overlay, (0, 0))

                pause_text = TITLE_FONT .render("Paused!", 1, BLACK)
                WINDOW.blit(pause_text, ((WIDTH//2 - pause_text.get_width()//2, TITLE_Y)))

                RESUME_BUTTON = draw_button("Resume", BUTTON_X, NEW_GAME_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                SAVE_BUTTON = draw_button("Save Game", BUTTON_X, LOAD_GAME_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                MENU_BUTTON = draw_button("Main Menu", BUTTON_X, SETTINGS_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)


        elif page == 3: #settings page 
            WINDOW.fill(WHITE)
            settings_title = TITLE_FONT.render("Settings", 1, BLACK)
            WINDOW.blit(settings_title, ((WIDTH//2 - settings_title.get_width()//2, TITLE_Y)))
        

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if page == 0:
                    if NEW_GAME_BUTTON.collidepoint(mouse_pos):
                        page = 1
                        pause = False
                    if LOAD_GAME_BUTTON.collidepoint(mouse_pos):
                        if if_save_exists():
                            load_game(player)
                            page = 1
                            pause = False
                        else: 
                            print("No save file found!")
                    if SETTINGS_BUTTON.collidepoint(mouse_pos):
                        page = 3
                    if QUIT_BUTTON.collidepoint(mouse_pos):
                        run = False

                elif page == 1:
                    if pause == False:
                        if PAUSE_BUTTON.collidepoint(mouse_pos):
                            pause = True
                    elif pause == True:
                        if RESUME_BUTTON.collidepoint(mouse_pos):
                            pause = False
                        if MENU_BUTTON.collidepoint(mouse_pos):
                            page = 0
                        if SAVE_BUTTON.collidepoint(mouse_pos):
                            save_game(player)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if page == 1:
                        pause = not pause
                    elif page == 2 or page == 3:
                        page = 0
                    elif page == 0:
                        run = False
                    
                if event.key == pygame.K_F11:
                    WINDOW = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


    pygame.quit() 



if __name__ == "__main__":
    main()