import pygame
import random
import sys
import os

# Import speak from backend
try:
    from backend.TextToSpeech import speak
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.TextToSpeech import speak

def start_game():
    pygame.init()

    # Constants
    WIDTH, HEIGHT = 800, 600
    BLOCK_SIZE = 20
    FPS = 8

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (213, 50, 80)
    GREEN = (0, 255, 0)
    BLUE = (50, 153, 213)
    YELLOW = (255, 255, 0)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Friday\'s Snake Game')

    clock = pygame.time.Clock()
    font_style = pygame.font.SysFont("bahnschrift", 25)
    score_font = pygame.font.SysFont("comicsansms", 35)

    def show_score(score):
        value = score_font.render("Your Score: " + str(score), True, YELLOW)
        screen.blit(value, [0, 0])

    def draw_snake(block_size, snake_list):
        for x in snake_list:
            pygame.draw.rect(screen, GREEN, [x[0], x[1], block_size, block_size])

    def message(msg, color):
        mesg = font_style.render(msg, True, color)
        screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])

    def gameLoop():
        game_over = False
        game_close = False

        x1 = WIDTH / 2
        y1 = HEIGHT / 2

        x1_change = 0
        y1_change = 0

        snake_List = []
        Length_of_snake = 1

        foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
        foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0

        spoken_over = False

        while not game_over:

            while game_close == True:
                screen.fill(BLUE)
                message("You Lost! Press C-Play Again or Q-Quit", RED)
                show_score(Length_of_snake - 1)
                pygame.display.update()

                if not spoken_over:
                    speak(f"Game over. Your score was {Length_of_snake - 1}. Press C to play again or Q to quit.")
                    spoken_over = True

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            game_over = True
                            game_close = False
                        if event.key == pygame.K_c:
                            gameLoop()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        x1_change = -BLOCK_SIZE
                        y1_change = 0
                    elif event.key == pygame.K_RIGHT:
                        x1_change = BLOCK_SIZE
                        y1_change = 0
                    elif event.key == pygame.K_UP:
                        y1_change = -BLOCK_SIZE
                        x1_change = 0
                    elif event.key == pygame.K_DOWN:
                        y1_change = BLOCK_SIZE
                        x1_change = 0

            if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
                game_close = True
            x1 += x1_change
            y1 += y1_change
            screen.fill(BLACK)
            pygame.draw.rect(screen, RED, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])
            snake_Head = []
            snake_Head.append(x1)
            snake_Head.append(y1)
            snake_List.append(snake_Head)
            if len(snake_List) > Length_of_snake:
                del snake_List[0]

            for x in snake_List[:-1]:
                if x == snake_Head:
                    game_close = True

            draw_snake(BLOCK_SIZE, snake_List)
            show_score(Length_of_snake - 1)

            pygame.display.update()

            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
                foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
                Length_of_snake += 1

            clock.tick(FPS)

        pygame.quit()

    gameLoop()

if __name__ == "__main__":
    start_game()
