import pygame, random, math, csv, json, os
from os import listdir
from os.path import isfile, join

pygame.font.init()
pygame.mixer.init()

#windows setup 
WIDTH, HEIGHT = 1280, 720 
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE) 

FPS = 30

MUSIC_ON = True
SFX_ON = True 

# fonts for main menu's text 
TITLE_FONT = pygame.font.SysFont("comicsans", 80)
BUTTON_FONT = pygame.font.SysFont("comicsans", 40)

# buttons dimensions
BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING = 500, 70, 25

# buttons positions
BUTTON_X = WIDTH//2 - BUTTON_WIDTH//2
TITLE_Y = 40
FIRST_BUTTON_Y = 160
SECOND_BUTTON_Y = FIRST_BUTTON_Y + BUTTON_HEIGHT + BUTTON_SPACING
THIRD_BUTTON_Y = SECOND_BUTTON_Y + BUTTON_HEIGHT + BUTTON_SPACING
FOURTH_BUTTON_Y = THIRD_BUTTON_Y + BUTTON_HEIGHT + BUTTON_SPACING
FIFTH_BUTTON_Y = FOURTH_BUTTON_Y + BUTTON_HEIGHT + BUTTON_SPACING

#colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHT_GREY = (200, 200, 200)
PURPLE = (150, 0, 200)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
DARK_GREY = (40, 40, 40)

#pause icon
PAUSE_BUTTON_SIDE = 100
PAUSE_BUTTON_MARGIN = 20
PAUSE_ICON = pygame.image.load('assets/icons/pause.png').convert_alpha()
PAUSE_ICON = pygame.transform.scale(PAUSE_ICON, (PAUSE_BUTTON_SIDE, PAUSE_BUTTON_SIDE))

# health bar 
BAR_WIDTH, BAR_HEIGHT, BAR_MARGIN = 200, 20, 20

# dialogue box constants
DIALOGUE_BOX_HEIGHT = 150
DIALOGUE_BOX_WIDTH = 1000
DIALOGUE_BOX_MARGIN = 20
DIALOGUE_TEXT_FONT = pygame.font.SysFont("comicsans", 24)
DIALOGUE_TITLE_FONT = pygame.font.SysFont("comicsans",30, bold=True)
DIALOGUE_TEXT_COLOUR = BLACK
DIALOGUE_NAME_COLOUR = GOLD
DIALOGUE_BOX_COLOUR = WHITE
DIALOGUE_BORDER_COLOUR = DARK_GREY

#START OF ENTITY SPRITE AND MOVEMENT--------------------------------------------------------------------------
PLAYER_VEL = 7

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
            sprites.append(surface)
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

#PLAYER SPRITTE
class Player(pygame.sprite.Sprite):
    COLOR = RED
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacter", "Sketch", 150, 150, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.melee_attack = False

        self.hitbox = pygame.Rect(x + 55, y + 40, 40, 110)

        self.sprite = self.SPRITES["idle_left"][0]
        self.update()

        #player health
        self.health = 100
        self.max_health = 100
        #KNOCKBACK FOR TAKING DAMAGE
        self.knockback_timer = 0
        self.knockback_vel = 0

#MOVEMENT FUNC
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.jump_count += 1
        self.fall_count = 0
        if not self.melee_attack:
            self.animation_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"

            if not self.melee_attack and self.jump_count == 0:
                self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"

            if not self.melee_attack and self.jump_count == 0:
                self.animation_count = 0

    def melee(self):
        if not self.melee_attack:
            self.melee_attack = True
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.melee_attack:
            sprite_sheet = "melee"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

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

        elif sprite_sheet == "jump":
            sprite_index = (self.animation_count // self.ANIMATION_DELAY)
            if sprite_index >= len(sprites):
                        sprite_index = len(sprites) - 1

        else:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
    
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.hitbox.x = self.rect.x + 55
        self.hitbox.y = self.rect.y + 40

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))

def handle_vertical_collision(player, objects, dy):
    collided_objects = []

    for obj in objects:
        if player.hitbox.colliderect(obj.rect):
            if dy > 0: 
                offset = player.hitbox.bottom - player.rect.bottom 
                player.rect.bottom = obj.rect.top - offset
                player.hitbox.bottom = obj.rect.top
                player.landed()
                collided_objects.append(obj)
            
            elif dy < 0:
                offset = player.hitbox.top - player.rect.top
                player.rect.top = obj.rect.bottom - offset
                player.hitbox.top = obj.rect.bottom
                player.hit_head()
                collided_objects.append(obj)
    
    return collided_objects


def handle_horizontal_collision(player, objects, dx):
    if dx == 0:
        return

    collided_object = None
    
    for obj in objects:
        if player.hitbox.colliderect(obj.rect):
            collided_object = obj
            
            if dx > 0:  #MOVE RIGHT
                player.rect.right = obj.rect.left + 55
                player.hitbox.right = obj.rect.left
            elif dx < 0:  #MOVE LEFT
                player.rect.left = obj.rect.right - 55
                player.hitbox.left = obj.rect.right
            
            player.x_vel = 0
            break
    
    return collided_object

def handle_move(player, objects, run_sound, sfx_on):
    keys = pygame.key.get_pressed()

    if player.knockback_timer > 0:
        player.x_vel = player.knockback_vel
        player.knockback_timer -= 1
        run_sound.stop()

    else:

        is_running = (keys[pygame.K_a] or keys[pygame.K_d]) and player.jump_count==0

        if keys[pygame.K_a]:
            player.move_left(PLAYER_VEL)
        elif keys[pygame.K_d]:
            player.move_right(PLAYER_VEL)
        else:
            player.x_vel = 0

        if is_running and SFX_ON:
            if run_sound.get_num_channels() == 0:
                run_sound.play(loops=-1)
        else: 
            run_sound.stop()

    player.move(player.x_vel, 0)
    player.update()
    handle_horizontal_collision(player, objects, player.x_vel)
    
    player.move(0, player.y_vel)
    player.update()
    handle_vertical_collision(player, objects, player.y_vel)

def handle_enemy_physics(enemy, objects):
    enemy.move(enemy.x_vel, 0)
    enemy.update()
    handle_enemy_horizontal_collision(enemy, objects, enemy.x_vel)
    
    enemy.move(0, enemy.y_vel)
    enemy.update()
    handle_enemy_vertical_collision(enemy, objects, enemy.y_vel)

def draw_player(player): 
    player.draw(WINDOW)

#END OF MAIN CHARACTER/PLAYER SPRITE AND MOVEMENT--------------------------------------------------------------------------

#START OF OTHER ENTITIES SPRITE AND MOVEMENT--------------------------------------------------------------------------
class Slime(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Enemies", "Slime", 150, 150, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height, patrol_distance=200):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x, y, width, height)
        
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.move_timer = 0

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.hitbox.width = 60
        self.hitbox.height = 40
        self.hitbox.x = self.rect.centerx - (self.hitbox.width // 2)
        y_offset = 0 
        self.hitbox.y = self.rect.bottom - self.hitbox.height + y_offset

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def loop(self, fps, player):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.ai_behavior(player)
        
        if self.fall_count == 0 and not self.is_attacking:
            self.x_vel = 0

        self.fall_count += 1
        self.update_sprite()
        self.update()

    def ai_behavior(self, player):
        if self.fall_count == 0:
            self.move_timer += 1
            self.is_attacking = False

        if self.move_timer > 4:
                self.move_timer = 0
                self.is_attacking = True
                
                self.y_vel = -5 
                
                direction = 1 if player.rect.x > self.rect.x else -1
                self.x_vel = direction * 5
                self.direction = "right" if direction == 1 else "left"

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.x_vel = 0
    
    def hit_head(self):
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.y_vel < 0: sprite_sheet = "move"
        elif self.x_vel != 0: sprite_sheet = "move"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        if sprite_sheet == "move":
            sprite_index = (self.animation_count // self.ANIMATION_DELAY)
            if sprite_index >= len(sprites):
                sprite_index = len(sprites) - 1
        else:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win, camera):
        hitbox_screen_pos = camera.get_offset_position(self)

        screen_x = hitbox_screen_pos.centerx - (self.sprite.get_width() // 2)
        screen_y = hitbox_screen_pos.bottom - self.sprite.get_height()
        
        win.blit(self.sprite, (screen_x, screen_y))

def handle_enemy_horizontal_collision(enemy, objects, dx):
    if dx == 0:
        return

    for obj in objects:
        if enemy.hitbox.colliderect(obj.rect):
            offset_left = enemy.hitbox.x - enemy.rect.x
            offset_right = enemy.rect.right - enemy.hitbox.right
            if dx > 0:
                enemy.hitbox.right = obj.rect.left
                enemy.rect.right = enemy.hitbox.right + offset_right
            elif dx < 0:
                enemy.hitbox.left = obj.rect.right
                enemy.rect.left = enemy.hitbox.left - offset_left
            
            enemy.x_vel = 0
            break


def handle_enemy_vertical_collision(enemy, objects, dy):
    collided_objects = []

    for obj in objects:
        if enemy.hitbox.colliderect(obj.rect):
            if dy > 0:
                offset = enemy.hitbox.bottom - enemy.rect.bottom
                enemy.rect.bottom = obj.rect.top - offset
                enemy.hitbox.bottom = obj.rect.top
                enemy.landed()
                collided_objects.append(obj)
            
            elif dy < 0:
                offset = enemy.hitbox.top - enemy.rect.top
                enemy.rect.top = obj.rect.bottom - offset
                enemy.hitbox.top = obj.rect.bottom
                enemy.hit_head()
                collided_objects.append(obj)
    
    return collided_objects

#END OF OTHER ENTITIES SPRITE AND MOVEMENT--------------------------------------------------------------------------


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
    def __init__(self, level0, spritesheet, scale = 1):
        self.tile_size = 64 * scale
        self.scale = scale
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.map_w, self.map_h = 0, 0
        self.tiles = self.load_tiles(level0)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()
        
    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))
        
    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)
    
    def read_csv(self, level0):
        map = []
        with open(os.path.join(level0)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data: map.append(list(row))
            return map
    
    def load_tiles(self, level0):
        tiles = []
        map = self.read_csv(level0)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:
                if tile == '-1':
                    self.start_x, self.start_y = x * self.tile_size, y * self.tile_size 
                elif tile == '0':
                    tiles.append(Tile('lava0.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '1':
                    tiles.append(Tile('lava1.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '2':
                    tiles.append(Tile('lava2.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '3':
                    tiles.append(Tile('lava3.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '7':
                    tiles.append(Tile('pipe01.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '4':
                    tiles.append(Tile('pipe00.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '5':
                    tiles.append(Tile('pipe0.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '8':
                    tiles.append(Tile('pipe1.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '11':
                    tiles.append(Tile('pipeturn.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '12':
                    tiles.append(Tile('pipeturn0.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '6':
                    tiles.append(Tile('pipeturn1.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '13':
                    tiles.append(Tile('pipeturn2.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '10':
                    tiles.append(Tile('pipe2.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                
                x += 1
            y += 1
        
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles 
#MAP SETTING TEST END ---------------------------------------------------------------------------------------------------


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
        pygame.draw.rect(WINDOW, LIGHT_GREY, button)
    else:
        pygame.draw.rect(WINDOW, WHITE, button)

    icon_x = button_x + (PAUSE_BUTTON_SIDE - PAUSE_ICON.get_width()) // 2
    icon_y = button_y + (PAUSE_BUTTON_SIDE - PAUSE_ICON.get_height()) // 2
    WINDOW.blit(PAUSE_ICON, (icon_x, icon_y))

    return button

# json saving part -----------------------------------------------------------
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

# player camera follow -------------------------------------------------------------
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

# bgm and sfx control part ------------------------------------------------------
def toggle_bgm():
    global MUSIC_ON
    if MUSIC_ON:
        pygame.mixer.music.pause()
        MUSIC_ON = False
    else:
        pygame.mixer.music.unpause()
        MUSIC_ON = True

def toggle_sfx():
    global SFX_ON
    SFX_ON = not SFX_ON

def draw_message(message):
    if message:
        message_font = pygame.font.SysFont("comicsans", 30)
        message_text = message_font.render(message, 1, BLACK)

        message_x = WIDTH//2 - message_text.get_width()//2
        message_y = HEIGHT - 100

        WINDOW.blit(message_text, (message_x, message_y))

def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(WINDOW, RED, (x, y, BAR_WIDTH, BAR_HEIGHT))
    current_width = int((health/max_health)*BAR_WIDTH)
    pygame.draw.rect(WINDOW, GREEN, (x, y, current_width, BAR_HEIGHT))
    pygame.draw.rect(WINDOW, BLACK, (x, y, BAR_WIDTH, BAR_HEIGHT),1 )

#def dialogue part -------------------------------------------------------
class DialogueBox:
    def __init__(self):
        self.active = False
        self.current_text = ""
        self.full_text = ""
        self.speaker = ""
        self.character_index = 0
        self.typing_speed = 2
        self.finished = False

    def start_dialogue(self, speaker, text):
        self.active = True
        self.speaker = speaker
        self.current_text = ""
        self.full_text = text
        self.character_index = 0
        self.finished = False 

    def update_dialogue(self):
        if self.active and not self.finished:
            if self.character_index < len(self.full_text):
                self.character_index += self.typing_speed
                self.current_text = self.full_text[:self.character_index]
            else: 
                self.finished = True
                self.current_text = self.full_text
                
    def skip_dialogue(self):
        if self.active:
            self.current_text = self.full_text
            self.character_index = len(self.full_text)
            self.finished = True

    def close_dialogue(self):
        self.active = False
        self.current_text = ""
        self.full_text = ""
        self.speaker = ""
        self.character_index = 0
        self.finished = False

    def draw_dialogue_box(self, surface, width, height):
        if not self.active:
            return
        
        box_width = DIALOGUE_BOX_WIDTH
        box_height = DIALOGUE_BOX_HEIGHT
        box_x = DIALOGUE_BOX_MARGIN
        box_y = HEIGHT - DIALOGUE_BOX_HEIGHT - DIALOGUE_BOX_MARGIN
        
        pygame.draw.rect(WINDOW, DIALOGUE_BOX_COLOUR, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(WINDOW, DIALOGUE_BORDER_COLOUR, (box_x, box_y, box_width, box_height), 3 )

        if self.speaker:
            name_surface = DIALOGUE_TEXT_FONT.render(self.speaker, True, DIALOGUE_TEXT_COLOUR)
            surface.blit(name_surface, (box_x + 15, box_y + 10))
            text_start_y = box_y + 50
        else:
            text_start_y = box_y + 10

        text_surface = DIALOGUE_TEXT_FONT.render(self.current_text, True, DIALOGUE_TEXT_COLOUR)
        surface.blit(text_surface, (box_x + 15, text_start_y))

        if self.finished:
            continue_text = DIALOGUE_TEXT_FONT.render("Press spacebar to continue...", True, DIALOGUE_TEXT_COLOUR)
            continue_x = box_x + box_width - continue_text.get_width() - 15
            continue_y = box_y + box_height - continue_text.get_width() - 10

# game over screen  ---------------------------------------------------------------------



# ---------------------------------------------------------------------------------

def main():
    player = Player(100, 100, 50, 50)
    dialogue_box = DialogueBox()
    pygame.display.set_caption("Colour IT!")
    clock = pygame.time.Clock()

    page = 0
    pause = False
    show_new_game_warning = False

    # for dialogue box 
    message = ""
    message_timer = 0
    MESSAGE_DURATION = FPS*2
    
    # load map declares..?
    class SpriteSheet:
        def parse_sprite(self, name):
            path = join("assets", "LevelMap", name)
            return pygame.image.load(path).convert_alpha()
    
    spritesheet = SpriteSheet()
    tile_map = TileMap('assets/LevelMap/level0.csv', spritesheet, scale = 1) #also scales up the map here

    camera = Camera(tile_map.map_w, tile_map.map_h) 

    enemies = [Slime(2000, 4000, 150, 150)]

    #main bgm
    pygame.mixer.music.load('assets/sounds/background_music.wav')
    pygame.mixer.music.play(-1)
    #sound effects 
    attack_sound = pygame.mixer.Sound('assets/sounds/attack.wav')
    attack_sound.set_volume(0.5)
    jump_sound = pygame.mixer.Sound('assets/sounds/jump.flac')
    jump_sound.set_volume(1)
    run_sound = pygame.mixer.Sound('assets/sounds/run.wav')
    run_sound.set_volume(1)

    run = True
    while run: 
        global WINDOW, MUSIC_ON, SFX_ON
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        if message_timer > 0:
            message_timer -= 1

        if page == 0: #main menu page 
            WINDOW.fill(GREY)
            title_text = TITLE_FONT.render("Colour IT!", 1, BLACK)
            WINDOW.blit(title_text, ((WIDTH//2 - title_text.get_width()//2, TITLE_Y)))

            NEW_GAME_BUTTON = draw_button("New Game", BUTTON_X, FIRST_BUTTON_Y+BUTTON_SPACING*2, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            LOAD_GAME_BUTTON = draw_button("Load Game", BUTTON_X, SECOND_BUTTON_Y+BUTTON_SPACING*2, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            SETTINGS_BUTTON = draw_button("Settings", BUTTON_X, THIRD_BUTTON_Y+BUTTON_SPACING*2, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            QUIT_BUTTON = draw_button("Quit Game", BUTTON_X, FOURTH_BUTTON_Y+BUTTON_SPACING*2, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

            if show_new_game_warning:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill(GREY)
                WINDOW.blit(overlay, (0, 0))
                warning_text = TITLE_FONT .render("Warning", 1, RED)
                WINDOW.blit(warning_text, ((WIDTH//2 - warning_text.get_width()//2, TITLE_Y)))

                message_font = pygame.font.SysFont("comicsans", 40)
                message1 = message_font.render("You have an existing game!", 1, BLACK)
                message2 = message_font.render("Start a new game anyway?", 1, BLACK)
                message3 = message_font.render("Press ESC to return", 1, BLACK)
                WINDOW.blit(message1, ((WIDTH//2 - message1.get_width()//2, TITLE_Y + 100)))
                WINDOW.blit(message2, ((WIDTH//2 - message2.get_width()//2, TITLE_Y + 150)))
                WINDOW.blit(message3, ((WIDTH//2 - message3.get_width()//2, TITLE_Y + 200)))
                YES_BUTTON = draw_button("Yes! Start a new game.", BUTTON_X, THIRD_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                NO_BUTTON = draw_button("No!", BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 1: #new game page 
            if pause == False:
                WINDOW.fill(WHITE)
                
                player.loop(FPS)
                handle_move(player, tile_map.tiles, run_sound, SFX_ON)

                dialogue_box.update_dialogue()


                for enemy in enemies:
                    enemy.loop(FPS, player)
                    handle_enemy_physics(enemy, tile_map.tiles)

                    if player.melee_attack and player.hitbox.colliderect(enemy.hitbox):
                        enemies.remove(enemy)
                    
                    elif player.hitbox.colliderect(enemy.hitbox):
                        if player.health > 0 and player.knockback_timer == 0:
                            player_initial_health = player.health
                            player.health -= 5
                            player.y_vel = -5
                            if player.rect.x < enemy.rect.x:
                                player.knockback_vel = -15
                            else:
                                player.knockback_vel = 15

                            player.knockback_timer = 10

                            print(f"OUCH! You initially had {player_initial_health}, now you have {player.health}!")

                camera.follow_player(player)

                for tile in tile_map.tiles:
                    tile_screen_position = camera.get_offset_position(tile)
                    WINDOW.blit(tile.image, tile_screen_position)

                for enemy in enemies:
                    enemy_pos = camera.get_offset_position(enemy)
                    WINDOW.blit(enemy.sprite, enemy_pos)
                
                player_screen_position = camera.get_offset_position(player)
                WINDOW.blit(player.sprite, player_screen_position)
                #START OF CHECK HITBOX HERE#======================================================================
                """
                pygame.draw.rect(WINDOW, (255, 0, 0), pygame.Rect(
                    player.hitbox.x + camera.offset_x,
                    player.hitbox.y + camera.offset_y,
                    player.hitbox.width,
                    player.hitbox.height
                ), 2)

                # ENEMY HITBOX
                enemy_rect = camera.get_offset_position(enemy)    
                hx = enemy.hitbox.x + camera.offset_x
                hy = enemy.hitbox.y + camera.offset_y
                pygame.draw.rect(WINDOW, (255, 0, 0), (hx, hy, enemy.hitbox.width, enemy.hitbox.height), 2)
                """
                #END OF CHECK HITBOX HERE#========================================================================

                for enemy in enemies:
                    enemy.draw(WINDOW, camera)

                PAUSE_BUTTON = draw_pause_button(mouse_pos)
                draw_health_bar(BAR_MARGIN, BAR_MARGIN, player.health, player.max_health)
                dialogue_box.draw_dialogue_box(WINDOW, WIDTH, HEIGHT)

            elif pause == True:
                WINDOW.fill(WHITE)
                
                player_screen_position = camera.get_offset_position(player)
                WINDOW.blit(player.sprite, player_screen_position)

                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill(GREY)
                overlay.set_alpha(128)
                WINDOW.blit(overlay, (0, 0))

                pause_text = TITLE_FONT .render("Paused!", 1, BLACK)
                WINDOW.blit(pause_text, ((WIDTH//2 - pause_text.get_width()//2, TITLE_Y)))

                RESUME_BUTTON = draw_button("Resume", BUTTON_X, FIRST_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                SAVE_BUTTON = draw_button("Save Game", BUTTON_X, SECOND_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                bgm_text = "BGM ON" if MUSIC_ON else "BGM OFF"
                BGM_BUTTON = draw_button(bgm_text, BUTTON_X, THIRD_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                sfx_text = "Sound Effects ON" if SFX_ON else "Sound Effects OFF"
                SFX_BUTTON = draw_button(sfx_text, BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                MENU_BUTTON = draw_button("Main Menu", BUTTON_X, FIFTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)


        elif page == 3: #settings page 
            WINDOW.fill(GREY)
            settings_title = TITLE_FONT.render("Settings", 1, BLACK)
            WINDOW.blit(settings_title, ((WIDTH//2 - settings_title.get_width()//2, TITLE_Y)))

            bgm_text = "BGM ON" if MUSIC_ON else "BGM OFF"
            BGM_BUTTON = draw_button(bgm_text, BUTTON_X, FIRST_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            sfx_text = "Sound Effects ON" if SFX_ON else "Sound Effects OFF"
            SFX_BUTTON = draw_button(sfx_text, BUTTON_X, SECOND_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            MENU_BUTTON = draw_button("Main Menu", BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
        
        if message_timer > 0:
            draw_message(message)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if page == 0:
                    if show_new_game_warning:
                        if YES_BUTTON.collidepoint(mouse_pos):
                            if os.path.exists('savegame.json'):
                                os.remove('savegame.json')
                            player.rect.x = tile_map.start_x
                            player.rect.y = tile_map.start_y
                            player.update()
                            player.health = player.max_health
                            show_new_game_warning = False
                            page = 1
                            pause = False
                            dialogue_box.start_dialogue("You", "I need to bring back colour to the world!")
                        if NO_BUTTON.collidepoint(mouse_pos):
                            show_new_game_warning = False
                    else:
                        if NEW_GAME_BUTTON.collidepoint(mouse_pos):
                            pause = False
                            if if_save_exists():
                                show_new_game_warning = True
                            else: 
                                player.rect.x = tile_map.start_x
                                player.rect.y = tile_map.start_y
                                player.update()
                                player.health = player.max_health 
                                page = 1
                                pause = False
                                dialogue_box.start_dialogue("You", "I need to bring back colour to the world!")
                        if LOAD_GAME_BUTTON.collidepoint(mouse_pos):
                            if if_save_exists():
                                load_game(player)
                                page = 1
                                pause = False
                            else: 
                                message = "No saved game found!"
                                message_timer = MESSAGE_DURATION
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
                            message = "Game Saved!"
                            message_timer = MESSAGE_DURATION
                        if BGM_BUTTON.collidepoint(mouse_pos):
                            toggle_bgm()
                        if SFX_BUTTON.collidepoint(mouse_pos):
                            toggle_sfx()
                elif page == 3:
                    if BGM_BUTTON.collidepoint(mouse_pos):
                        toggle_bgm()
                    if SFX_BUTTON.collidepoint(mouse_pos):
                        toggle_sfx()
                    if MENU_BUTTON.collidepoint(mouse_pos):
                        page = 0

            if event.type == pygame.KEYDOWN:
                if page == 1 and not pause:
                    if event.key == pygame.K_SPACE:
                        player.melee()
                        if SFX_ON:
                            attack_sound.play()
                    elif event.key == pygame.K_w and player.jump_count < 2:
                        player.jump()
                        if SFX_ON:
                            jump_sound.play()
                if event.key == pygame.K_ESCAPE:
                    if page == 0 and show_new_game_warning:
                        show_new_game_warning = False   
                    elif page == 1:
                        pause = not pause
                    elif page == 3:
                        page = 0
                    elif page == 0:
                        run = False
                if event.key == pygame.K_F11:
                    WINDOW = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                if event.key == pygame.K_SPACE:
                    if dialogue_box.active:
                        if dialogue_box.finished:
                            dialogue_box.close_dialogue()
                        else: 
                            dialogue_box.skip_dialogue()
                    else: 
                        player.melee()


    pygame.quit() 



if __name__ == "__main__":
    main()