import pygame
import random
import sys
import os
import math

# Import speak from backend
try:
    from backend.TextToSpeech import speak
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.TextToSpeech import speak

def start_game():
    pygame.init()

    # Screen setup
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Friday's Ultra Breakout")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (10, 10, 15)
    RED = (255, 50, 50)
    BLUE = (50, 150, 255)
    GREEN = (50, 255, 150)
    YELLOW = (255, 220, 50)
    PURPLE = (200, 50, 255)
    CYAN = (50, 255, 255)
    ORANGE = (255, 150, 50)

    # Initialize all variables in start_game scope for nonlocal access
    paddle_width = 120
    paddle_x = WIDTH // 2 - paddle_width // 2
    balls = []
    bricks = []
    powerups = []
    particles = []
    trails = []
    game_state = "PLAYING"
    lives = 3
    score = 0
    combo = 0
    level = 1
    spoken_msg = False
    screen_shake = 0

    class Ball:
        def __init__(self, x, y, dx, dy):
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.radius = 8
            self.active = True

        def update(self):
            self.x += self.dx
            self.y += self.dy

            # Wall bounds
            if self.x - self.radius <= 0:
                self.x = self.radius
                self.dx *= -1
            elif self.x + self.radius >= WIDTH:
                self.x = WIDTH - self.radius
                self.dx *= -1
                
            if self.y - self.radius <= 0:
                self.y = self.radius
                self.dy *= -1
            
            # Trail
            trails.append(Trail(self.x, self.y, RED))

            if self.y > HEIGHT + 20:
                self.active = False

        def draw(self, surface):
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x - 2), int(self.y - 2)), 3) # highlight

    class Trail:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.radius = 6
            self.color = color
            self.lifetime = 255

        def update(self):
            self.radius *= 0.9
            self.lifetime -= 20
            return self.lifetime > 0

        def draw(self, surface):
            s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, max(0, int(self.lifetime))), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(s, (self.x - self.radius, self.y - self.radius))

    class Particle:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.color = color
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(-4, 4)
            self.lifetime = 255
            self.size = random.uniform(2, 6)

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.1 # Gravity for particles
            self.lifetime -= random.randint(5, 15)
            self.size *= 0.95
            return self.lifetime > 0

        def draw(self, surface):
            if self.size > 0.5:
                s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, max(0, int(self.lifetime))), (int(self.size), int(self.size)), int(self.size))
                surface.blit(s, (self.x - self.size, self.y - self.size))

    class PowerUp:
        def __init__(self, x, y, type):
            self.rect = pygame.Rect(x - 12, y - 12, 24, 24)
            self.type = type # 'life', 'wide', 'fast', 'multiball'
            self.speed = 3
            if type == 'life': self.color, self.symbol = RED, "L"
            elif type == 'wide': self.color, self.symbol = GREEN, "W"
            elif type == 'fast': self.color, self.symbol = YELLOW, "S"
            elif type == 'multiball': self.color, self.symbol = CYAN, "M"

        def update(self):
            self.rect.y += self.speed
            return self.rect.y < HEIGHT

        def draw(self, surface, font):
            pygame.draw.circle(surface, self.color, self.rect.center, 12)
            pygame.draw.circle(surface, WHITE, self.rect.center, 12, 2)
            sym = font.render(self.symbol, True, BLACK)
            surface.blit(sym, (self.rect.centerx - sym.get_width()//2, self.rect.centery - sym.get_height()//2))

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20, bold=True)
    big_font = pygame.font.SysFont("Arial", 48, bold=True)

    def generate_level(lvl):
        bricks = []
        rows = min(4 + lvl, 8)
        cols = 10
        colors = [BLUE, GREEN, YELLOW, PURPLE, RED, CYAN, ORANGE]
        
        for r in range(rows):
            for c in range(cols):
                # Different patterns based on level
                if lvl % 3 == 1: # Full block
                    make = True
                elif lvl % 3 == 2: # Checkerboard
                    make = (r + c) % 2 == 0
                else: # Pyramid
                    make = (c >= r and c < cols - r)
                
                if make:
                    brick_rect = pygame.Rect(c * (WIDTH // cols) + 5, r * 30 + 60, (WIDTH // cols) - 10, 25)
                    hp = 2 if lvl > 3 and random.random() < 0.2 else 1
                    bricks.append({'rect': brick_rect, 'color': colors[r % len(colors)], 'hp': hp})
        return bricks
    
    def reset_level(keep_score=False, next_level=False):
        nonlocal balls, paddle_x, paddle_width, bricks, powerups, particles, trails, game_state, lives, score, combo, level, spoken_msg, screen_shake
        paddle_width = 120
        paddle_x = WIDTH // 2 - paddle_width // 2
        balls = [Ball(WIDTH // 2, HEIGHT - 100, random.choice([-5, 5]), -5)]
        powerups = []
        particles = []
        trails = []
        combo = 0
        screen_shake = 0
        spoken_msg = False
        
        if not keep_score:
            score = 0
            lives = 3
            level = 1
        if next_level:
            level += 1
            
        bricks = generate_level(level)

    reset_level()

    def trigger_particles(x, y, color):
        for _ in range(20):
            particles.append(Particle(x, y, color))

    running = True
    while running:
        screen.fill(BLACK)
        clock.tick(60)
        
        # Screen Shake effect setup
        shake_x, shake_y = 0, 0
        if screen_shake > 0:
            shake_x = random.randint(-screen_shake, screen_shake)
            shake_y = random.randint(-screen_shake, screen_shake)
            screen_shake -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == "GAMEOVER":
                    if event.key == pygame.K_r:
                        game_state = "PLAYING"
                        reset_level(keep_score=False)
                    if event.key == pygame.K_q:
                        running = False
                elif game_state == "WIN":
                    if event.key == pygame.K_n:
                        game_state = "PLAYING"
                        reset_level(keep_score=True, next_level=True)
                    if event.key == pygame.K_q:
                        running = False

        if game_state == "PLAYING":
            # Paddle Control
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle_x > 0: paddle_x -= 8
            if keys[pygame.K_RIGHT] and paddle_x < WIDTH - paddle_width: paddle_x += 8

            paddle_rect = pygame.Rect(paddle_x, HEIGHT - 50, paddle_width, 15)

            # Update Balls
            for ball in balls:
                ball.update()

                # Paddle Collision
                if paddle_rect.collidepoint(ball.x, ball.y + ball.radius) and ball.dy > 0:
                    ball.dy *= -1
                    # Angle bounce
                    ball.dx = ((ball.x - paddle_rect.centerx) / (paddle_width / 2)) * 7
                    ball.y = paddle_rect.top - ball.radius
                    combo = 0 # reset combo

                # Brick Collision
                for brick in bricks[:]:
                    if brick['rect'].collidepoint(ball.x, ball.y - ball.radius) or \
                       brick['rect'].collidepoint(ball.x, ball.y + ball.radius) or \
                       brick['rect'].collidepoint(ball.x - ball.radius, ball.y) or \
                       brick['rect'].collidepoint(ball.x + ball.radius, ball.y):
                        
                        trigger_particles(ball.x, ball.y, brick['color'])
                        ball.dy *= -1
                        screen_shake = 3
                        
                        combo += 1
                        points = 10 * combo
                        score += points
                        
                        brick['hp'] -= 1
                        if brick['hp'] <= 0:
                            bricks.remove(brick)
                            # PowerUp Drop
                            if random.random() < 0.2: # 20% chance
                                ptype = random.choice(['life', 'wide', 'fast', 'multiball'])
                                powerups.append(PowerUp(brick['rect'].centerx, brick['rect'].centery, ptype))
                        else:
                            brick['color'] = WHITE # Visual indicator of damage
                        break # Only hit one brick per frame per ball

            # Filter active balls
            balls = [b for b in balls if b.active]

            # PowerUp Logic
            for p in powerups[:]:
                if not p.update():
                    powerups.remove(p)
                elif p.rect.colliderect(paddle_rect):
                    if p.type == 'life': 
                        lives += 1
                        speak("Extra life")
                    elif p.type == 'wide': 
                        paddle_width = min(300, paddle_width + 60)
                        speak("Wide paddle")
                    elif p.type == 'fast': 
                        for b in balls:
                            b.dx *= 1.2
                            b.dy *= 1.2
                        speak("Speed up")
                    elif p.type == 'multiball':
                        new_balls = []
                        for b in balls:
                            new_balls.append(Ball(b.x, b.y, b.dx, -abs(b.dy)))
                            new_balls.append(Ball(b.x, b.y, -b.dx, -abs(b.dy)))
                        balls.extend(new_balls)
                        speak("Multi ball")
                    powerups.remove(p)

            # Particles & Trails
            particles = [p for p in particles if p.update()]
            trails = [t for t in trails if t.update()]

            # Death Logic
            if not balls:
                lives -= 1
                combo = 0
                paddle_width = 120
                if lives > 0:
                    speak(f"Life lost. {lives} remaining")
                    balls = [Ball(WIDTH // 2, HEIGHT - 100, random.choice([-5, 5]), -5)]
                else:
                    game_state = "GAMEOVER"

            # Level Clear Logic
            if not bricks:
                game_state = "WIN"

        # Setup Shake Surface
        display_surface = pygame.Surface((WIDTH, HEIGHT))
        display_surface.fill(BLACK)

        # Drawing on display_surface
        for t in trails: t.draw(display_surface)
        for p in particles: p.draw(display_surface)
        
        for brick in bricks:
            pygame.draw.rect(display_surface, brick['color'], brick['rect'], border_radius=4)
            # draw highlight
            pygame.draw.rect(display_surface, WHITE, brick['rect'], 1, border_radius=4)
        
        # Draw Paddle with gradient/glow
        pygame.draw.rect(display_surface, CYAN, (paddle_x, HEIGHT - 50, paddle_width, 15), border_radius=7)
        pygame.draw.rect(display_surface, WHITE, (paddle_x+5, HEIGHT - 48, paddle_width-10, 5), border_radius=3)
        
        for p in powerups: p.draw(display_surface, font)
        for ball in balls: ball.draw(display_surface)

        # HUD
        hud_text = f"SCORE: {score}   LIVES: {lives}   LEVEL: {level}   COMBO: x{combo}"
        score_surface = font.render(hud_text, True, WHITE)
        display_surface.blit(score_surface, (20, 15))

        if game_state == "GAMEOVER":
            if not spoken_msg:
                msg = f"Game Over. Your final score is {score}. Press R to restart or Q to quit."
                speak(msg)
                spoken_msg = True
            overlay = big_font.render("GAME OVER", True, RED)
            sub = font.render("PRESS 'R' TO RETRY OR 'Q' TO QUIT", True, WHITE)
            display_surface.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - 50))
            display_surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))
            
        if game_state == "WIN":
            if not spoken_msg:
                msg = f"Level {level} cleared! Brilliant job. Press N for next level."
                speak(msg)
                spoken_msg = True
            overlay = big_font.render("LEVEL CLEARED!", True, GREEN)
            sub = font.render(f"SCORE: {score} - PRESS 'N' FOR NEXT LEVEL OR 'Q' TO QUIT", True, WHITE)
            display_surface.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - 50))
            display_surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

        # Blit display_surface to screen with shake offset
        screen.blit(display_surface, (shake_x, shake_y))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    start_game()
