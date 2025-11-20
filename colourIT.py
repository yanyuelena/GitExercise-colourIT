import pygame

#windows setup 
WIDTH, HEIGHT = 900, 600 
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Colour IT!")

#colours constants
WHITE = (255, 255, 255)

FPS = 15

PLAYER_VEL = 5

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
#PLAYER SPRITTE
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
#MOVEMENT FUNC
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        
    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, self.rect)

def handle_move(player):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)

def draw_window(player):
    WINDOW.fill(WHITE)
    player.draw(WINDOW)
    pygame.display.update()

def main():
    player = Player(100, 100, 50, 50)
    
    clock = pygame.time.Clock()
    run = True
    while run: 
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

#Input/Movement
        handle_move(player)
#Updates player position
        player.loop(FPS)
#Drawing Everything
        draw_window(player)

    pygame.quit()

#javia 
#def update_world():


#lydia 
#def update_mobs():

if __name__ == "__main__":
    main()