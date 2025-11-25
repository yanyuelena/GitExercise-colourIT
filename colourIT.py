import pygame
import random
import math
from os import listdir
from os.path import isfile, join

pygame.font.init()

#windows setup 
WIDTH, HEIGHT = 1280, 720 
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT)) 

FPS = 15

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

# fonts for main menu's text 
TITLE_FONT = pygame.font.SysFont("comicsans", 80)
BUTTON_FONT = pygame.font.SysFont("comicsans", 40)
# buttons dimensions
BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING = 600, 100, 50
# buttons positions
BUTTON_X = WIDTH//2 - BUTTON_WIDTH//2
TITLE_Y = 50
START_Y = 200
SETTINGS_Y = START_Y + BUTTON_HEIGHT + BUTTON_SPACING
QUIT_Y = SETTINGS_Y + BUTTON_HEIGHT + BUTTON_SPACING


#colours constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHT_GREY = (200, 200, 200)

def draw_window():
    WINDOW.fill(WHITE)

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


def main():
    player = Player(100, 100, 50, 50)
    pygame.display.set_caption("Colour IT!")
    clock = pygame.time.Clock()

    page = 0

    run = True
    while run: 
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        draw_window()

        
        
        if page == 0: #added to make buttons work
            title_text = TITLE_FONT.render("Colour IT!", 1, BLACK)
            WINDOW.blit(title_text, ((WIDTH//2 - title_text.get_width()//2, TITLE_Y)))

            START_BUTTON = draw_button("START GAME!", BUTTON_X, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            SETTINGS_BUTTON = draw_button("Settings", BUTTON_X, SETTINGS_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            QUIT_BUTTON = draw_button("Quit Game", BUTTON_X, QUIT_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 1: #Input/Movement & update player position
            handle_move(player)
            player.loop(FPS)
            draw_player(player)

        elif page == 2:
            settings_title = TITLE_FONT.render("Settings", 1, BLACK)
            WINDOW.blit(settings_title, ((WIDTH//2 - settings_title.get_width()//2, TITLE_Y)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if START_BUTTON.collidepoint(mouse_pos):
                    page = 1
                if SETTINGS_BUTTON.collidepoint(mouse_pos):
                    page = 2
                if QUIT_BUTTON.collidepoint(mouse_pos):
                    run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if page == 1 or page == 2:
                        page = 0
                    elif page == 0:
                        run = False


    pygame.quit() #return "quit" closes the window so i chg :P




if __name__ == "__main__":
    main()