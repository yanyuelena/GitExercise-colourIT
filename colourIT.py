import pygame

pygame.font.init()

#windows setup 
WIDTH, HEIGHT = 1280, 720 
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT)) 

FPS = 15

# fonts for main menu's text 
TITLE_FONT = pygame.font.SysFont("comicsans", 80)
BUTTON_FONT = pygame.font.SysFont("comicsans", 40)
# buttons dimensions
BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING = 600, 100, 50
# buttons positions
BUTTON_X = WIDTH//2 - BUTTON_WIDTH//2
TITLE_Y = 50
START_Y = 200
OPTION_Y = START_Y + BUTTON_HEIGHT + BUTTON_SPACING
QUIT_Y = OPTION_Y + BUTTON_HEIGHT + BUTTON_SPACING


#colours constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHT_GREY = (200, 200, 200)


def draw_window():
    WINDOW.fill(WHITE)
    pygame.display.update()

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
    pygame.display.set_caption("Colour IT!")
    clock = pygame.time.Clock()


   
    pygame.display.update()


    run = True
    while run: 
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        draw_window()

        title_text = TITLE_FONT.render("Colour IT!", 1, BLACK)
        WINDOW.blit(title_text, ((WIDTH//2 - title_text.get_width()//2, TITLE_Y)))

        START_BUTTON = draw_button("START GAME!", BUTTON_X, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
        OPTION_BUTTON = draw_button("Options", BUTTON_X, OPTION_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
        QUIT_BUTTON = draw_button("Quit Game", BUTTON_X, QUIT_Y, BUTTON_WIDTH, BUTTON_HEIGHT, mouse_pos)
        pygame.display.update()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if START_BUTTON.collidepoint(mouse_pos):
                    return "start!"
                if OPTION_BUTTON.collidepoint(mouse_pos):
                    return "options!"
                if QUIT_BUTTON.collidepoint(mouse_pos):
                    return "quit!"


    return "quit"



if __name__ == "__main__":
    main()