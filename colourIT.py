import pygame, random, math, csv, json, os
from os import listdir
from os.path import isfile, join

pygame.font.init()
pygame.mixer.init()

# windows setup
WIDTH, HEIGHT = 1280, 720
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

# background image for level 1
background = pygame.image.load('assets/LevelMap/background.png').convert()

# background image for hub
hub_background = pygame.image.load('assets/LevelX/backgroundx.png').convert()

# background image for final hub
final_hub_background = pygame.image.load('assets/LevelX/backgroundx_red.png').convert()

FPS = 30

MUSIC_ON = True
SFX_ON = True

# FIXED: Fonts for main menu's text
TITLE_FONT = pygame.font.Font("comic.ttf", 80)
BUTTON_FONT = pygame.font.Font("comic.ttf", 40)

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

# colour constants
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
SUBRED = (90, 56, 58)
NOTBLACK = (40, 40, 40)

# pause icon
PAUSE_BUTTON_SIDE = 100
PAUSE_BUTTON_MARGIN = 20
PAUSE_ICON = pygame.image.load('assets/icons/pause.png').convert_alpha()
PAUSE_ICON = pygame.transform.scale(PAUSE_ICON, (PAUSE_BUTTON_SIDE, PAUSE_BUTTON_SIDE))

# health bar
BAR_WIDTH, BAR_HEIGHT, BAR_MARGIN = 200, 20, 20

# FIXED: dialogue box constants
DIALOGUE_BOX_HEIGHT = 150
DIALOGUE_BOX_WIDTH = 1000
DIALOGUE_BOX_MARGIN = 20
DIALOGUE_TEXT_FONT = pygame.font.Font("comic.ttf", 24)
DIALOGUE_TITLE_FONT = pygame.font.Font("comic.ttf", 30)
DIALOGUE_TEXT_COLOUR = BLACK
DIALOGUE_NAME_COLOUR = GOLD
DIALOGUE_BOX_COLOUR = WHITE
DIALOGUE_BORDER_COLOUR = DARK_GREY

# inventory icon constants
INVENTORY_BUTTON_SIDE = 100
INVENTORY_BUTTON_MARGIN = 20

# START OF ENTITY SPRITE AND MOVEMENT--------------------------------------------------------------------------
PLAYER_VEL = 8

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
        self.max_jumps = 1
        self.melee_attack = False
        self.hit_enemies = []

        self.hitbox = pygame.Rect(x + 55, y + 40, 40, 110)

        self.sprite = self.SPRITES["idle_left"][0]
        self.update()

        # player health
        self.health = 100
        self.max_health = 100
        # KNOCKBACK FOR TAKING DAMAGE
        self.knockback_timer = 0
        self.knockback_vel = 0
        # for collection system
        self.collection = Collection()

    def jump(self):
        self.y_vel = -self.GRAVITY * 16.5
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
            if not self.melee_attack:
                self.direction = "left"

            if not self.melee_attack and self.jump_count == 0:
                self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            if not self.melee_attack:
                self.direction = "right"

            if not self.melee_attack and self.jump_count == 0:
                self.animation_count = 0

    def melee(self):
        if not self.melee_attack:
            self.melee_attack = True
            self.animation_count = 0
            self.hit_enemies.clear()

    def create_attack_box(self):
        range_width = 40
        range_height = self.hitbox.height

        if self.direction == "right":
            return pygame.Rect(self.hitbox.right, self.hitbox.y, range_width, range_height)
        else:
            return pygame.Rect(self.hitbox.left - range_width, self.hitbox.y, range_width, range_height)

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
           
            if dx > 0:  # MOVE RIGHT
                player.rect.right = obj.rect.left + 55
                player.hitbox.right = obj.rect.left
            elif dx < 0:  # MOVE LEFT
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

# START OF OTHER ENTITIES SPRITE AND MOVEMENT--------------------------------------------------------------------------
class Slime(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Enemies", "Slime", 150, 150, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height, patrol_distance=300):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x, y, width, height)
       
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.move_timer = 0
        self.detection_range = patrol_distance
        self.health = 3
        self.is_attacking = False

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
            dx = self.rect.centerx - player.rect.centerx
            dy = self.rect.centery - player.rect.centery
            distance_to_player = math.hypot(dx, dy)
           
            if distance_to_player < self.detection_range:
                self.move_timer += 1
            else:
                self.move_timer = 0

            self.is_attacking = False

        if self.move_timer > 2:
                self.move_timer = 0
                self.is_attacking = True
               
                self.y_vel = -5
               
                direction = 1 if player.rect.x > self.rect.x else -1
                self.x_vel = direction * 6
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

class Tomato(Slime):
    SPRITES = load_sprite_sheets("Enemies", "Tomato", 150, 150, True)

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.rect = pygame.Rect(x, y, width, height)
        self.health = 60
        self.hurt_timer = 0
        self.invincibility_timer = 0
        self.projectiles = []
       
        self.state = "idle"
        self.state_timer = 0
        self.action_duration = 60
        self.speed = 5
       
        self.target_player = None
        self.last_action = "idle"

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
       
        self.hitbox.width = 100
        self.hitbox.height = 100
       
        self.hitbox.x = self.rect.centerx - (self.hitbox.width // 2)
        self.hitbox.y = self.rect.bottom - self.hitbox.height

    def loop(self, fps, player):
        for p in self.projectiles:
            p.move()
            if p.timer > 120:
                self.projectiles.remove(p)

        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.fall_count += 1

        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        if self.hurt_timer > 0:
            self.x_vel = 0

        else:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            self.target_player = player

            if self.state != "attack":
                if dx > 0: self.direction = "right"
                else: self.direction = "left"

            if distance < 800:
                self.state_timer += 1
               
                if self.state == "idle":
                    self.x_vel = 0
                    if self.state_timer > self.action_duration:
                        self.pick_new_state()

                elif self.state == "move":
                    if self.direction == "right": self.x_vel = self.speed
                    else: self.x_vel = -self.speed
                   
                    if self.state_timer > self.action_duration:
                        self.state = "idle"
                        self.state_timer = 0
                        self.action_duration = random.randint(15, 50)

                elif self.state == "attack":
                    self.x_vel = 0
                    pass

            else:
                self.state = "idle"
                self.x_vel = 0

        self.update_sprite()
        self.update()

    def pick_new_state(self):
        self.state_timer = 0

        if self.last_action == "move":
            self.state = "attack"
        else:
            if random.random() < 0.45:
                self.state = "move"
            else:
                self.state = "attack"
       
        if self.state == "move":
            self.action_duration = random.randint(15, 90)
            self.last_action = "move"
        elif self.state == "attack":
            self.animation_count = 0
            self.last_action = "attack"

    def shoot(self):
        if self.target_player:
            bullet_speed = 20
            if self.health <= 50:
                bullet_speed = 45

            bullet = Projectile(self.rect.centerx, self.rect.centery,
                            self.target_player.rect.centerx, self.target_player.rect.centery, speed=bullet_speed)
            self.projectiles.append(bullet)

    def update_sprite(self):
        sprite_sheet = "idle"

        if self.hurt_timer > 0:
            sprite_sheet = "hurt"
            self.hurt_timer -= 1
           
        elif self.state == "move":
            sprite_sheet = "move"
        elif self.state == "attack":
            sprite_sheet = "attack"
       
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]

        if sprite_sheet == "hurt":
            sprite_index = 0

        if self.state == "move" or self.state == "idle":
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)

           
        elif self.state == "attack":
            sprite_index = (self.animation_count // self.ANIMATION_DELAY)
           
            if sprite_index == len(sprites) - 1 and self.animation_count % self.ANIMATION_DELAY == 0:
                 self.shoot()
           
            if sprite_index >= len(sprites):
                self.state = "idle"
                self.state_timer = 0
                self.action_duration = random.randint(30, 60)
                sprite_index = 0
           
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win, camera):
        offset_x = 0
        offset_y = 0
        if self.hurt_timer > 0:
            shake_amount = 5
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
        real_x = self.rect.x
        real_y = self.rect.y
        self.rect.x += offset_x
        self.rect.y += offset_y

        draw_body = True
        if self.invincibility_timer > 0:
            if self.invincibility_timer % 10 < 5:
                draw_body = False

        if draw_body:
            super().draw(win, camera)
       
        for p in self.projectiles:
            p.draw(win, camera)
           
        self.rect.x = real_x
        self.rect.y = real_y

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, speed):
        super().__init__()
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = (255, 0, 0)
        self.timer = 0
        self.deflected = False
       
        dx = target_x - x
        dy = target_y - y
        angle = math.atan2(dy, dx)
       
        self.x_vel = math.cos(angle) * speed
        self.y_vel = math.sin(angle) * speed
   
    def deflect(self):
        self.x_vel *= -1.5
        self.y_vel *= -1.5
       
        self.color = (0, 255, 0)
       
        self.timer = 0
        self.deflected = True
       
    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.timer += 1
       
    def draw(self, win, camera):
        screen_x = self.rect.x + camera.offset_x
        screen_y = self.rect.y + camera.offset_y
        pygame.draw.rect(win, self.color, (screen_x, screen_y, self.rect.width, self.rect.height))

class Blueberry(Tomato):
    SPRITES = load_sprite_sheets("Enemies", "Blueberry", 150, 150, True)

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.health = 60
        self.action_duration = 40
        self.speed = 7

    def pick_new_state(self):
        super().pick_new_state()

        if self.state == "move":
            self.y_vel = -13

    def shoot(self):
        if self.target_player:
            # ANGLE COMPARED TO PLAYER
            dx = self.target_player.rect.centerx - self.rect.centerx
            dy = self.target_player.rect.centery - self.rect.centery
            base_angle = math.atan2(dy, dx)
           
            spread = [-0.3, 0, 0.3]
           
            for offset in spread:
                angle = base_angle + offset
               
                speed = 15
                x_vel = math.cos(angle) * speed
                y_vel = math.sin(angle) * speed
               
                bullet = Projectile(self.rect.centerx, self.rect.centery,
                                    self.rect.centerx + x_vel, self.rect.centery + y_vel, speed=speed)
               
                bullet.x_vel = x_vel
                bullet.y_vel = y_vel
                bullet.color = (0, 0, 255)
               
                self.projectiles.append(bullet)

class Cabbage(Tomato):
    SPRITES = load_sprite_sheets("Enemies", "Cabbage", 150, 150, True)

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.health = 60
        self.speed = 0
        self.dash_speed = 25
        self.dash_direction = 0

    def shoot(self):
        pass

    def pick_new_state(self):
        self.state_timer = 0
       
        if random.random() < 0.7:
            self.state = "charge"
            self.action_duration = 30
            self.x_vel = 0
        else:
            self.state = "idle"
            self.action_duration = 30

    def loop(self, fps, player):
        if self.state == "dash":
            self.y_vel = 0
            self.fall_count = 0
        else:
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
            self.fall_count += 1

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
       
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1

        if self.hurt_timer > 0:
            if self.x_vel > 0:
                self.x_vel -= 1
            elif self.x_vel < 0:
                self.x_vel += 1
           
            self.hurt_timer -= 1

            if self.hurt_timer == 0:
                self.state = "idle"
                self.state_timer = 0
                self.action_duration = 40
                self.dash_direction = 0
           
        else:
            if distance < 800 or self.state == "dash" or self.state == "charge":
               
                self.state_timer += 1
               
                if self.state == "idle":
                    self.x_vel = 0
                    if self.state_timer > self.action_duration:
                        self.pick_new_state()

                elif self.state == "charge":
                    self.x_vel = 0
                   
                    if player.rect.centerx > self.rect.centerx:
                        self.direction = "right"
                    else:
                        self.direction = "left"

                    if self.state_timer > self.action_duration:
                        self.state = "dash"
                        self.state_timer = 0
                        self.action_duration = 20
                       
                        if self.direction == "right":
                            self.dash_direction = self.dash_speed
                        else:
                            self.dash_direction = -self.dash_speed

                        self.rect.y -= 2
                        self.x_vel = self.dash_direction

                elif self.state == "dash":
                    if self.x_vel == 0 and self.dash_direction != 0:
                        self.health -= 10
                        self.hurt_timer = 15
                        self.state = "idle"
                        self.state_timer = 0
                        self.action_duration = 90

                        if self.dash_direction > 0:
                            self.x_vel = -15
                        else:
                            self.x_vel = 15

                        self.dash_direction = 0
                        print("Cabbage bonked into a wall!")
                   
                    else:
                        self.x_vel = self.dash_direction
                   
                    if self.state_timer > self.action_duration:
                        self.state = "idle"
                        self.state_timer = 0
                        self.action_duration = 40
                        self.dash_direction = 0
            else:
                self.state = "idle"
                self.x_vel = 0

        self.update_sprite()
        self.update()

    def update_sprite(self):
        sprite_sheet = "idle"
       
        if self.hurt_timer > 0:
            sprite_sheet = "hurt"

        elif self.state == "charge":
            sprite_sheet = "charge"
           
        elif self.state == "dash":
            sprite_sheet = "dash"

        elif self.state == "move":
            sprite_sheet = "move"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
       
        if sprite_sheet == "hurt":
            sprite_index = 0
           
        else:
            sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)

        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def draw(self, win, camera):
        offset_x = 0
        offset_y = 0

        if self.state == "charge":
            shake_amount = 5
            offset_x = random.randint(-shake_amount, shake_amount)
            offset_y = random.randint(-shake_amount, shake_amount)
       
        real_x = self.rect.x
        real_y = self.rect.y
       
        self.rect.x += offset_x
        self.rect.y += offset_y
       
        super().draw(win, camera)
       
        self.rect.x = real_x
        self.rect.y = real_y

# MAP SETTING -------------------------------------------------------------------------------------------------------
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
        map_data = []
        with open(os.path.join(level0)) as data:
            reader = csv.reader(data, delimiter=',')
            for row in reader: map_data.append(list(row))
            return map_data
   
    def load_tiles(self, level0):
        tiles = []
        map_data = self.read_csv(level0)
        x, y = 0, 0
        for row in map_data:
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

class TileMapX(TileMap): # assign tiles for hub map
    def load_tiles(self, level0):
        tiles = []
        map_data = self.read_csv(level0)
        x, y = 0, 0
        for row in map_data:
            x = 0
            for tile in row:
                if tile == '-1':
                    self.start_x, self.start_y = x * self.tile_size, y * self.tile_size
                elif tile == '0':
                    tiles.append(Tile('ground.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '1':
                    tiles.append(Tile('level0_redroot.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '2':
                    tiles.append(Tile('level0_blueroot.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
                elif tile == '3':
                    tiles.append(Tile('level0_greenroot.png', x * self.tile_size, y * self.tile_size, self.spritesheet, self.scale))
               
                x += 1
            y += 1
       
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles

class MiniMap():
    @staticmethod
    def draw_minimap(tilemap_obj, surface, player = None, size = 200, padding = 10):
        if getattr(tilemap_obj, 'map_w', 0) == 0 or getattr(tilemap_obj, 'map_h', 0) == 0:
            return
   
        mini_w, mini_h = size, size
        mini = pygame.transform.scale(tilemap_obj.map_surface, (mini_w, mini_h))

        x = WIDTH - mini_w - padding
        y = HEIGHT - mini_h - padding

        pygame.draw.rect(surface, SUBRED, (x - 2, y - 2, mini_w + 4, mini_h + 4))
       
        surface.blit(mini, (x, y))

        if player is not None and tilemap_obj.map_w > 0 and tilemap_obj.map_h > 0:
            lightblue = (173, 216, 230)
            px = int ((player.rect.centerx / tilemap_obj.map_w) * mini_w)
            py = int ((player.rect.centery / tilemap_obj.map_h) * mini_h)
            markersize = max(8, min(6, mini_w // 50))
            pygame.draw.rect(surface, lightblue, (x + px - markersize//2, y + py - markersize//2, markersize, markersize))

class Pre_Cutscene:
    def __init__(self, image_paths, durations):
        self.images = [pygame.image.load(path).convert() for path in image_paths]
        if isinstance(durations, (list, tuple)):
            self.durations = [int(d) for d in durations]
        else:
            self.durations = [int(durations)]

        if len(self.durations) < len(self.images):
            last = self.durations[-1]
            self.durations += [last] * (len(self.images) - len(self.durations))

        self.current_image_index = 0
        self.frame_count = 0
        self.finished = False

    def update(self):
        if self.finished:
            return

        self.frame_count += 1
        current_duration = self.durations[self.current_image_index]
        if self.frame_count >= current_duration:
            self.frame_count = 0
            self.current_image_index += 1
            if self.current_image_index >= len(self.images):
                self.finished = True

    def draw(self, screen):
        if self.finished:
            return

        if self.current_image_index < len(self.images):
            img = self.images[self.current_image_index]
            img_scaled = pygame.transform.scale(img, (WIDTH, HEIGHT))
            screen.blit(img_scaled, (0, 0))

def draw_button(text, x, y, width, height, mouse_pos):

    button = pygame.Rect(x, y, width, height)

    if button.collidepoint(mouse_pos):
        pygame.draw.rect(WINDOW, GREY, button)
    else:
        pygame.draw.rect(WINDOW, WHITE, button)

    pygame.draw.rect(WINDOW, BLACK, button, 3)

    button_text = BUTTON_FONT.render(text, 1, BLACK)
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

def save_game(player, enemies, collectibles, current_page):
    saved_enemies = []
    for enemy in enemies:
        saved_enemies.append({
            "type": type(enemy).__name__,
            "x": enemy.rect.x,
            "y": enemy.rect.y
        })

    saved_collectibles = []
    for item in collectibles:
        saved_collectibles.append({
            "name": item.item_name,
            "x": item.rect.x,
            "y": item.rect.y
        })

    save_data = {
        "player_x": player.rect.x,
        "player_y": player.rect.y,
        "player_health": player.health,
        "inventory": player.collection.items,
        "enemies": saved_enemies,
        "collectibles": saved_collectibles,
        "current_page": current_page
    }
    with open('savegame.json', 'w') as file:
        json.dump(save_data, file)
    print("Game Saved!")

def load_game(player):
    with open('savegame.json', 'r') as file:
        save_data = json.load(file)
    player.rect.x = save_data["player_x"]
    player.rect.y = save_data["player_y"]
    player.health = save_data["player_health"]

    loaded_page = save_data["current_page"]

    if "inventory" in save_data:
        player.collection.items = save_data["inventory"]

    loaded_enemies = []
    if "enemies" in save_data:
        for enemy_data in save_data["enemies"]:
            if enemy_data["type"] == "Slime":
                loaded_enemies.append(Slime(enemy_data["x"], enemy_data["y"], 150, 150))
            elif enemy_data["type"] == "Tomato":
                loaded_enemies.append(Tomato(enemy_data["x"], enemy_data["y"], 150, 150))
            elif enemy_data["type"] == "Blueberry":
                loaded_enemies.append(Blueberry(enemy_data["x"], enemy_data["y"], 150, 150))
            elif enemy_data["type"] == "Cabbage":
                loaded_enemies.append(Cabbage(enemy_data["x"], enemy_data["y"], 150, 150))
    else:
        loaded_enemies = [
            Slime(1950, 1070, 150, 150),
            Slime(4830, 3630, 150, 150),
            Slime(4850, 1520, 150, 150),
            Slime(5050, 1520, 150, 150),
            Slime(1340, 2280, 150, 150),
            Slime(2950, 2480, 150, 150),
            Tomato(2853, 4500, 150, 150),
            Blueberry(3950, 1130, 150, 150),
            Cabbage(1940, 1570, 150, 150)
        ]

    loaded_collectibles = []
    if "collectibles" in save_data:
        for collectible_data in save_data["collectibles"]:
            loaded_collectibles.append(CollectibleItem(collectible_data["x"], collectible_data["y"], collectible_data["name"]))
    else:
        loaded_collectibles = [CollectibleItem(3950, 1130, "Double Jump")]
    print("Game Loaded!")
    return loaded_enemies, loaded_collectibles, loaded_page


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
        # FIXED: Font
        message_font = pygame.font.Font("comic.ttf", 30)
        message_text = message_font.render(message, 1, BLACK)

        message_x = WIDTH//2 - message_text.get_width()//2
        message_y = HEIGHT - 100

        WINDOW.blit(message_text, (message_x, message_y))

def draw_health_bar(x, y, health, max_health):
    pygame.draw.rect(WINDOW, RED, (x, y, BAR_WIDTH, BAR_HEIGHT))
    current_width = int((health/max_health)*BAR_WIDTH)
    pygame.draw.rect(WINDOW, GREEN, (x, y, current_width, BAR_HEIGHT))
    pygame.draw.rect(WINDOW, BLACK, (x, y, BAR_WIDTH, BAR_HEIGHT),1 )

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
                self.current_text = self.full_text[:int(self.character_index)]
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
            surface.blit(continue_text, (continue_x, box_y + box_height - 40))

class Collection:
    def __init__(self):
        self.items = {
            "Red Bucket": False,
            "Blue Bucket": False,
            "Green Bucket": False,
            "Double Jump": False,
        }
        self.is_open = False
   
    def collect_item(self, item_name):
        if item_name in self.items:
            if self.items[item_name] == False:  
                self.items[item_name] = True  
                return True  
            else:
                return False  
   
    def has_item(self, item_name):
        return self.items.get(item_name, False)
   
    def toggle_inventory(self):
        self.is_open = not self.is_open

    def draw_inventory_screen(self, surface, width, height):
        if not self.is_open:
            return  
       
        overlay = pygame.Surface((width, height))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        surface.blit(overlay, (0, 0))
       
        # FIXED: Font
        title_font = pygame.font.Font("comic.ttf", 80)
        title = title_font.render("Inventory", True, WHITE)
        surface.blit(title, (width // 2 - title.get_width() // 2, 50))
       
        item_font = pygame.font.Font("comic.ttf", 40)
        y = 200
       
        for item_name, have_it in self.items.items():
            if have_it:
                color = GREEN
                symbol = " / "
            else:
                color = GREY
                symbol = " X "
           
            text = item_font.render(symbol + item_name, True, color)
            surface.blit(text, (width // 2 - text.get_width() // 2, y))
            y += 70
       
        close_font = pygame.font.Font("comic.ttf", 30)
        close_text = close_font.render("Press I to close and open inventory~", True, WHITE)
        surface.blit(close_text, (width // 2 - close_text.get_width() // 2, height - 80))
   
def draw_inventory_button(mouse_pos):
    button_x = WIDTH - INVENTORY_BUTTON_SIDE - INVENTORY_BUTTON_MARGIN
    button_y = PAUSE_BUTTON_MARGIN + PAUSE_BUTTON_SIDE + INVENTORY_BUTTON_MARGIN
   
    button = pygame.Rect(button_x, button_y, INVENTORY_BUTTON_SIDE, INVENTORY_BUTTON_SIDE)
   
    if button.collidepoint(mouse_pos):
        pygame.draw.rect(WINDOW, LIGHT_GREY, button)
    else:
        pygame.draw.rect(WINDOW, WHITE, button)
   
    pygame.draw.rect(WINDOW, BLACK, button, 3)
   
    # FIXED: Font
    inv_font = pygame.font.Font("comic.ttf", 30)
    inv_text = inv_font.render("INV", True, BLACK)
    text_x = button_x + (INVENTORY_BUTTON_SIDE - inv_text.get_width()) // 2
    text_y = button_y + (INVENTORY_BUTTON_SIDE - inv_text.get_height()) // 2
    WINDOW.blit(inv_text, (text_x, text_y))
   
    return button

class CollectibleItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_name):
        super().__init__()
        self.item_name = item_name
        image_path = None

        if item_name == "Green Bucket":
            image_path = 'assets/icons/cabbage.jpg'
        elif item_name == "Blue Bucket":
            image_path = 'assets/icons/blueberry.jpg'
        elif item_name == "Red Bucket":
            image_path = 'assets/icons/tomato.jpg'
        elif item_name == "Double Jump":
            image_path = 'assets/icons/doublejump.jpg'

        if image_path:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            self.image = pygame.Surface((40, 40))
            self.image.fill(GOLD)

        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = pygame.Rect(x, y, 40, 40)
   
    def update(self):
        pass

    def draw(self, win, camera):
        screen_x = self.rect.x + camera.offset_x
        screen_y = self.rect.y + camera.offset_y
        win.blit(self.image, (screen_x, screen_y))

def draw_tomatoboss_health_bar(boss):
    bar_x = WIDTH//2 - BAR_WIDTH//2
    bar_y = 100
    pygame.draw.rect(WINDOW, RED, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT))
    tomatoboss_left_health = int((boss.health/60) * BAR_WIDTH)
    pygame.draw.rect(WINDOW, GREEN, (bar_x, bar_y, tomatoboss_left_health, BAR_HEIGHT))
    pygame.draw.rect(WINDOW, BLACK, (bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT),1 )

    # FIXED: Font
    tomatoboss_font = pygame.font.Font("comic.ttf", 60)
    tomatoboss_text = tomatoboss_font.render("BOSS", True, BLACK)
    text_x = WIDTH // 2 - tomatoboss_text.get_width() // 2
    WINDOW.blit(tomatoboss_text, (text_x, bar_y - 80))

def main():
    player = Player(100, 100, 50, 50)
    dialogue_box = DialogueBox()
    pygame.display.set_caption("Colour IT!")
    clock = pygame.time.Clock()

    collectibles = [CollectibleItem(3950, 1130,"Double Jump")]
    enemies = []
   
    page = 0
    pause = False
    show_new_game_warning = False

    message = ""
    message_timer = 0
    MESSAGE_DURATION = FPS*2
   
    class SpriteSheet:
        def parse_sprite(self, name):
            path = join("assets", "LevelMap", name)
            return pygame.image.load(path).convert_alpha()
   
    class SpriteSheetX:
        def parse_sprite(self, name):
            path = join("assets", "LevelX", name)
            return pygame.image.load(path).convert_alpha()
   
    spritesheet = SpriteSheet()
    spritesheet_x = SpriteSheetX()
    tile_map = TileMap('assets/LevelMap/level0.csv', spritesheet, scale = 1)
    tile_map_x = TileMapX('assets/LevelX/level_x.csv', spritesheet_x, scale = 1)

    camera = Camera(tile_map.map_w, tile_map.map_h)
    camera_x = Camera(tile_map_x.map_w, tile_map_x.map_h)

    bg_map = pygame.transform.scale(background, (tile_map.map_w, tile_map.map_h))
    bg_map_x = pygame.transform.scale(hub_background, (tile_map_x.map_w, tile_map_x.map_h))
    bg_map_xred = pygame.transform.scale(final_hub_background, (tile_map_x.map_w, tile_map_x.map_h))

    cutscene_dir = os.path.join('assets', 'Cutscene')
    try:
        cutscene_files = sorted([f for f in listdir(cutscene_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except Exception:
        cutscene_files = []
    cutscene_paths = [os.path.join(cutscene_dir, f) for f in cutscene_files]
    cut = None
    default_durations = [15, 10, 10, 30, 55, 55, 60, 50]
    cutscene_durations = default_durations if len(default_durations) == len(cutscene_paths) else [5] * len(cutscene_paths)

    final_cutscene_dir = os.path.join('assets', 'FinalCutscene')
    try:
        final_cutscene_files = sorted([f for f in listdir(final_cutscene_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    except Exception:
        final_cutscene_files = []
    final_cutscene_paths = [os.path.join(final_cutscene_dir, f) for f in final_cutscene_files]
    final_cut = None
    defin_durations = [55, 55, 55, 55, 55, 55, 50]
    final_cutscene_durations = defin_durations if len(defin_durations) == len(final_cutscene_paths) else [5] * len(final_cutscene_paths)

    RedCollision_zone = pygame.Rect(444, 746, 200, 746)

    pygame.mixer.music.load('assets/sounds/background_music.wav')
    pygame.mixer.music.play(-1)
    attack_sound = pygame.mixer.Sound('assets/sounds/attack.wav')
    attack_sound.set_volume(0.2)
    jump_sound = pygame.mixer.Sound('assets/sounds/jump.flac')
    jump_sound.set_volume(1)
    run_sound = pygame.mixer.Sound('assets/sounds/run.wav')
    run_sound.set_volume(2)

    run = True
    while run:
        global WINDOW, MUSIC_ON, SFX_ON
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        if message_timer > 0:
            message_timer -= 1
       
        if page == 0:
            WINDOW.fill(BLACK)
            title_text = TITLE_FONT.render("Colour IT!", 1, WHITE)
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

                # FIXED: Font
                message_font = pygame.font.Font("comic.ttf", 40)
                message1 = message_font.render("You have an existing game!", 1, BLACK)
                message2 = message_font.render("Start a new game anyway?", 1, BLACK)
                message3 = message_font.render("Press ESC to return", 1, BLACK)
                WINDOW.blit(message1, ((WIDTH//2 - message1.get_width()//2, TITLE_Y + 100)))
                WINDOW.blit(message2, ((WIDTH//2 - message2.get_width()//2, TITLE_Y + 150)))
                WINDOW.blit(message3, ((WIDTH//2 - message3.get_width()//2, TITLE_Y + 200)))
                YES_BUTTON = draw_button("Yes! Start a new game.", BUTTON_X, THIRD_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                NO_BUTTON = draw_button("No!", BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 1:
            if not pause:
                WINDOW.fill(SUBRED)
                WINDOW.blit(bg_map, (camera.offset_x, camera.offset_y))
               
                player.loop(FPS)
                handle_move(player, tile_map.tiles, run_sound, SFX_ON)
                dialogue_box.update_dialogue()
               
                for item in collectibles[:]:
                    if player.hitbox.colliderect(item.rect):
                        if player.collection.collect_item(item.item_name):
                            collectibles.remove(item)
                            if item.item_name == "Double Jump":
                                player.max_jumps = 2

                for enemy in enemies[:]:
                    enemy.loop(FPS, player)
                    handle_enemy_physics(enemy, tile_map.tiles)
                   
                    if enemy.health <= 0:
                        drop_name = None
                        if isinstance(enemy, Cabbage): drop_name = "Green Bucket"
                        elif isinstance(enemy, Blueberry): drop_name = "Blue Bucket"
                        elif isinstance(enemy, Tomato): drop_name = "Red Bucket"
                       
                        if drop_name:
                            collectibles.append(CollectibleItem(enemy.rect.centerx - 20, enemy.rect.centery, drop_name))
                        enemies.remove(enemy)
                        continue

                    if hasattr(enemy, 'projectiles'):
                        for p in enemy.projectiles[:]:
                            if any(p.rect.colliderect(t.rect) for t in tile_map.tiles):
                                enemy.projectiles.remove(p)
                                continue

                            if p.rect.colliderect(player.hitbox) and not p.deflected:
                                if player.knockback_timer == 0:
                                    player.health -= 20
                                    player.knockback_timer = 10
                                    player.knockback_vel = -15 if player.rect.centerx < p.rect.centerx else 15
                                    enemy.projectiles.remove(p)
                                    if player.health <= 0: page = 4

                            elif p.rect.colliderect(enemy.hitbox) and p.deflected:
                                if not (hasattr(enemy, 'invincibility_timer') and enemy.invincibility_timer > 0):
                                    enemy.health -= 15 if enemy.health <= 50 else 5
                                    enemy.projectiles.remove(p)
                                    if isinstance(enemy, Tomato):
                                        enemy.hurt_timer, enemy.invincibility_timer = 10, 80

                    if player.melee_attack:
                        if 0 <= player.animation_count < 5:
                            attack_box = player.create_attack_box()
                            if attack_box.colliderect(enemy.hitbox):
                                if not (hasattr(enemy, 'invincibility_timer') and enemy.invincibility_timer > 0):
                                    if enemy not in player.hit_enemies:
                                        player.hit_enemies.append(enemy)
                                        enemy.health -= 200
                                        if isinstance(enemy, Tomato):
                                            enemy.hurt_timer, enemy.invincibility_timer = 6, 50
                                        enemy.x_vel = 5 if player.rect.centerx < enemy.rect.centerx else -5
                               
                            if hasattr(enemy, 'projectiles'):
                                for p in enemy.projectiles:
                                    if attack_box.colliderect(p.rect) and not p.deflected:
                                        p.deflect()
                   
                    elif player.hitbox.colliderect(enemy.hitbox) and player.knockback_timer == 0:
                        player.health -= 15
                        player.y_vel = -5
                        player.knockback_vel = -15 if player.rect.x < enemy.rect.x else 15
                        player.knockback_timer = 10
                        if player.health <= 0: page = 4

                camera.follow_player(player)
                for tile in tile_map.tiles:
                    WINDOW.blit(tile.image, camera.get_offset_position(tile))
                WINDOW.blit(player.sprite, camera.get_offset_position(player))

                for enemy in enemies:
                    enemy.draw(WINDOW, camera)
                    if isinstance(enemy, Tomato) and math.hypot(player.rect.x - enemy.rect.x, player.rect.y - enemy.rect.y) < 600:
                        draw_tomatoboss_health_bar(enemy)
               
                for item in collectibles:
                    item.draw(WINDOW, camera)

                MiniMap.draw_minimap(tile_map, WINDOW, player)
                PAUSE_BUTTON = draw_pause_button(mouse_pos)
                draw_health_bar(BAR_MARGIN, BAR_MARGIN, player.health, player.max_health)
                dialogue_box.draw_dialogue_box(WINDOW, WIDTH, HEIGHT)
                INVENTORY_BUTTON = draw_inventory_button(mouse_pos)
                player.collection.draw_inventory_screen(WINDOW, WIDTH, HEIGHT)

                if all(player.collection.has_item(b) for b in ["Red Bucket", "Blue Bucket", "Green Bucket"]):
                    page = 7

            else:
                WINDOW.fill(WHITE)
                WINDOW.blit(player.sprite, camera.get_offset_position(player))
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.fill(GREY); overlay.set_alpha(128)
                WINDOW.blit(overlay, (0, 0))
                WINDOW.blit(TITLE_FONT.render("Paused!", 1, BLACK), (WIDTH//2 - 150, TITLE_Y))
                RESUME_BUTTON = draw_button("Resume", BUTTON_X, FIRST_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                SAVE_BUTTON = draw_button("Save Game", BUTTON_X, SECOND_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                BGM_BUTTON = draw_button("BGM ON" if MUSIC_ON else "BGM OFF", BUTTON_X, THIRD_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                SFX_BUTTON = draw_button("SFX ON" if SFX_ON else "SFX OFF", BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                MENU_BUTTON = draw_button("Main Menu", BUTTON_X, FIFTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 3:
            WINDOW.fill(GREY)
            WINDOW.blit(TITLE_FONT.render("Settings", 1, BLACK), (WIDTH//2 - 150, TITLE_Y))
            BGM_BUTTON = draw_button("BGM ON" if MUSIC_ON else "BGM OFF", BUTTON_X, FIRST_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            SFX_BUTTON = draw_button("SFX ON" if SFX_ON else "SFX OFF", BUTTON_X, SECOND_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
            MENU_BUTTON = draw_button("Main Menu", BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 4:
            WINDOW.fill(DARK_GREY)
            WINDOW.blit(TITLE_FONT.render("HAHA! GAME OVER!", 1, RED), (WIDTH//2 - 350, TITLE_Y))
            MENU_BUTTON = draw_button("Main Menu", BUTTON_X, SECOND_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 5:
            if cut is None:
                v_paths = [p for p in cutscene_paths if os.path.exists(p)]
                if not v_paths: page = 6
                else: cut = Pre_Cutscene(v_paths, cutscene_durations)
            if cut:
                cut.update(); cut.draw(WINDOW)
                if cut.finished: cut = None; page = 6

        elif page == 6 or page == 8:
            curr_bg = bg_map_x if page == 6 else bg_map_xred
            if not pause:
                WINDOW.fill(NOTBLACK)
                WINDOW.blit(curr_bg, (camera_x.offset_x, camera_x.offset_y))
                player.loop(FPS); handle_move(player, tile_map_x.tiles, run_sound, SFX_ON)
                camera_x.follow_player(player)
                for tile in tile_map_x.tiles:
                    WINDOW.blit(tile.image, camera_x.get_offset_position(tile))
                WINDOW.blit(player.sprite, camera_x.get_offset_position(player))
               
                if page == 6 and player.hitbox.colliderect(RedCollision_zone):
                    # FIXED: Font
                    info_text = pygame.font.Font("comic.ttf", 30).render("Press F to interact.", 1, WHITE)
                    WINDOW.blit(info_text, (WIDTH//2 - info_text.get_width()//2, HEIGHT - 150))

                PAUSE_BUTTON = draw_pause_button(mouse_pos)
                INVENTORY_BUTTON = draw_inventory_button(mouse_pos)
                player.collection.draw_inventory_screen(WINDOW, WIDTH, HEIGHT)
            else:
                WINDOW.fill(WHITE)
                WINDOW.blit(player.sprite, camera_x.get_offset_position(player))
                overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.fill(GREY); overlay.set_alpha(128)
                WINDOW.blit(overlay, (0, 0))
                WINDOW.blit(TITLE_FONT.render("Paused!", 1, BLACK), (WIDTH//2 - 150, TITLE_Y))
                RESUME_BUTTON = draw_button("Resume", BUTTON_X, FIRST_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                SAVE_BUTTON = draw_button("Save Game", BUTTON_X, SECOND_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                BGM_BUTTON = draw_button("BGM ON" if MUSIC_ON else "BGM OFF", BUTTON_X, THIRD_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                SFX_BUTTON = draw_button("SFX ON" if SFX_ON else "SFX OFF", BUTTON_X, FOURTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
                MENU_BUTTON = draw_button("Main Menu", BUTTON_X, FIFTH_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)

        elif page == 7:
            if final_cut is None:
                v_paths = [p for p in final_cutscene_paths if os.path.exists(p)]
                if not v_paths: page = 8; player.rect.x, player.rect.y = 980, 220
                else: final_cut = Pre_Cutscene(v_paths, final_cutscene_durations)
            if final_cut:
                final_cut.update(); final_cut.draw(WINDOW)
                if final_cut.finished: final_cut = None; page = 8; player.rect.x, player.rect.y = 980, 220

        if message_timer > 0: draw_message(message)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if page == 0:
                    if show_new_game_warning:
                        if YES_BUTTON.collidepoint(mouse_pos):
                            if os.path.exists('savegame.json'): os.remove('savegame.json')
                            player.rect.x, player.rect.y, player.health = 980, 220, 100
                            enemies = [Slime(1950, 1070, 150, 150), Slime(4830, 3630, 150, 150), Slime(4850, 1520, 150, 150), Slime(5050, 1520, 150, 150), Slime(1340, 2280, 150, 150), Slime(2950, 2480, 150, 150), Tomato(2853, 4500, 150, 150), Blueberry(3950, 1130, 150, 150), Cabbage(1940, 1570, 150, 150)]
                            player.collection, collectibles, player.max_jumps = Collection(), [CollectibleItem(3950, 1130, "Double Jump")], 1
                            show_new_game_warning, page, pause = False, 5, False
                            dialogue_box.start_dialogue("Tutorial", "SPACE to attack, I for inventory, ESC to pause")
                        elif NO_BUTTON.collidepoint(mouse_pos): show_new_game_warning = False
                    else:
                        if NEW_GAME_BUTTON.collidepoint(mouse_pos):
                            if if_save_exists(): show_new_game_warning = True
                            else:
                                player.rect.x, player.rect.y, player.health = 980, 220, 100
                                enemies = [Slime(1950, 1070, 150, 150), Slime(4830, 3630, 150, 150), Slime(4850, 1520, 150, 150), Slime(5050, 1520, 150, 150), Slime(1340, 2280, 150, 150), Slime(2950, 2480, 150, 150), Tomato(2853, 4500, 150, 150), Blueberry(3950, 1130, 150, 150), Cabbage(1940, 1570, 150, 150)]
                                player.collection, collectibles, player.max_jumps = Collection(), [CollectibleItem(3950, 1130, "Double Jump")], 1
                                page, pause = 5, False
                                dialogue_box.start_dialogue("Tutorial", "SPACE to attack, I for inventory, ESC to pause")
                        if LOAD_GAME_BUTTON.collidepoint(mouse_pos):
                            if if_save_exists():
                                enemies, collectibles, page = load_game(player)
                                player.max_jumps = 2 if player.collection.has_item("Double Jump") else 1
                                pause = False
                            else: message, message_timer = "No saved game found!", MESSAGE_DURATION
                        if SETTINGS_BUTTON.collidepoint(mouse_pos): page = 3
                        if QUIT_BUTTON.collidepoint(mouse_pos): run = False

                elif page in [1, 6, 8]:
                    if not pause:
                        if PAUSE_BUTTON.collidepoint(mouse_pos): pause = True
                        if INVENTORY_BUTTON.collidepoint(mouse_pos): player.collection.toggle_inventory()
                    else:
                        if RESUME_BUTTON.collidepoint(mouse_pos): pause = False
                        if MENU_BUTTON.collidepoint(mouse_pos): page = 0
                        if SAVE_BUTTON.collidepoint(mouse_pos): save_game(player, enemies, collectibles, page); message, message_timer = "Game Saved!", MESSAGE_DURATION
                        if BGM_BUTTON.collidepoint(mouse_pos): toggle_bgm()
                        if SFX_BUTTON.collidepoint(mouse_pos): toggle_sfx()
                elif page == 3:
                    if BGM_BUTTON.collidepoint(mouse_pos): toggle_bgm()
                    if SFX_BUTTON.collidepoint(mouse_pos): toggle_sfx()
                    if MENU_BUTTON.collidepoint(mouse_pos): page = 0
                elif page == 4:
                    if MENU_BUTTON.collidepoint(mouse_pos):
                        page = 0
                        player.health = player.max_health;
                    if os.path.exists("savegame.json"):
                        os.remove("savegame.json")

            if event.type == pygame.KEYDOWN:
                if page in [1, 6, 8] and not pause:
                    if event.key == pygame.K_SPACE:
                        if dialogue_box.active:
                            if dialogue_box.finished: dialogue_box.close_dialogue()
                            else: dialogue_box.skip_dialogue()
                        else:
                            player.melee()
                            if SFX_ON: attack_sound.play()
                    if event.key == pygame.K_i: player.collection.toggle_inventory()
                    elif event.key == pygame.K_w and player.jump_count < player.max_jumps:
                        player.jump()
                        if SFX_ON: jump_sound.play()
                if event.key == pygame.K_ESCAPE:
                    if page == 0 and show_new_game_warning: show_new_game_warning = False
                    elif page in [1, 6, 8]: pause = not pause
                    elif page in [3, 5, 7]:
                        if page == 5: page = 6; cut = None
                        elif page == 7: page = 8; final_cut = None; player.rect.x, player.rect.y = 980, 220
                        else: page = 0
                if event.key == pygame.K_f and page == 6 and RedCollision_zone.colliderect(player.rect):
                    page, pause, player.rect.x, player.rect.y = 1, False, 980, 220

    pygame.quit()

if __name__ == "__main__":
    main()