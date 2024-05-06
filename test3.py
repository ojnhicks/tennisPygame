import pygame
import pygame_menu
import sys
import random
import time

# Initialize Pygame and constants
pygame.init()

# Game constants
WIDTH, HEIGHT = 1063, 1001
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_WIDTH, PLAYER_HEIGHT = 100, 20
BALL_RADIUS = 7
SCORE_FONT = pygame.font.SysFont("comicsans", 50)
POWER_FONT = pygame.font.SysFont("comicsans", 20)
WINNING_SCORE = 10
POWER_MIN = 0.025
POWER_MAX = 4.5
POWER_INCREMENT = 0.175
AI_VEL = 2


# Menu setup
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ace Academy - Main Menu")

# Player and Ball Classes
class Player:
    COLOR = BLACK
    VEL = 6

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, right=True):
        if right:
            self.x += self.VEL
        else:
            self.x -= self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball:
    MAX_VEL = 6
    COLOR = BLACK

    def __init__(self, x, y, radius, image_path="tennis_ball.png"):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = 0
        self.y_vel = -self.MAX_VEL
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.radius * 2, self.radius * 2))
        self.last_collision_time = time.time()

    def draw(self, win):
        win.blit(self.image, (self.x - self.radius, self.y - self.radius))

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel *= -1
        self.x_vel = 0


# Define game functions
def draw(win, players, ball, left_score, right_score, power_level):
    background = pygame.image.load('tennis.png')  
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    win.blit(background, (0, 0))

    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (40, 20))
    win.blit(right_score_text, (40, HEIGHT - 80))

    for player in players:
        player.draw(win)

    pygame.draw.rect(win, WHITE, (WIDTH - 100, HEIGHT - 50, 80, 20))
    pygame.draw.rect(win, BLACK, (WIDTH - 100, HEIGHT - 50, 80 * (power_level / POWER_MAX), 20))

    ball.draw(win)

    pygame.display.update()


def handle_collision(ball, left_player, right_player):
    MAX_SPEED = 8

    if ball.x + ball.radius >= WIDTH:
        ball.x = WIDTH - ball.radius
        ball.x_vel *= -1
    elif ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.x_vel *= -1

    if ball.y_vel < 0:
        if (
            left_player.x <= ball.x <= left_player.x + left_player.width
            and left_player.y <= ball.y - ball.radius <= left_player.y + left_player.height
        ):
            ball.y_vel *= -1
            ball.x_vel = (ball.x - (left_player.x + left_player.width // 2)) // 20
            if abs(ball.x_vel) > MAX_SPEED:
                ball.x_vel = (ball.x_vel / abs(ball.x_vel)) * MAX_SPEED

    elif ball.y_vel > 0:
        if (
            right_player.x <= ball.x <= right_player.x + right_player.width
            and right_player.y <= ball.y + ball.radius <= right_player.y + right_player.height
        ):
            ball.y_vel *= -1
            ball.x_vel = (ball.x - (right_player.x + right_player.width // 2)) // 20
            if abs(ball.x_vel) > MAX_SPEED:
                ball.x_vel = (ball.x_vel / abs(ball.x_vel)) * MAX_SPEED


def handle_player_movement(keys, left_player, right_player):
    if keys[pygame.K_d] and left_player.x + left_player.width + left_player.VEL <= WIDTH:
        left_player.move(right=True)
    if keys[pygame.K_a] and left_player.x - left_player.VEL >= 0:
        left_player.move(right=False)

    if keys[pygame.K_w] and left_player.y - left_player.VEL >= 0:
        left_player.y -= left_player.VEL
    if keys[pygame.K_s] and left_player.y + left_player.height + left_player.VEL <= HEIGHT // 2:
        left_player.y += left_player.VEL

    if keys[pygame.K_RIGHT] and right_player.x + right_player.width + right_player.VEL <= WIDTH:
        right_player.move(right=True)
    if keys[pygame.K_LEFT] and right_player.x - right_player.VEL >= 0:
        right_player.move(right=False)

    if keys[pygame.K_DOWN] and right_player.y + right_player.height + right_player.VEL <= HEIGHT:
        right_player.y += right_player.VEL
    if keys[pygame.K_UP] and right_player.y - right_player.VEL >= HEIGHT // 2:
        right_player.y -= right_player.VEL


def handle_ai_movement(ball, right_player):
    ai_target_point = ball.x + random.randint(-25, 25)

    min_x = 0
    max_x = WIDTH - right_player.width

    if right_player.x + (right_player.width // 2) < ai_target_point and right_player.x + right_player.width + AI_VEL <= max_x:
        right_player.x += AI_VEL

    if right_player.x + (right_player.width // 2) > ai_target_point and right_player.x - AI_VEL >= min_x:
        right_player.x -= AI_VEL

def handle_forehand_collision(ball, player, score, collision_cooldown=3):
    forehand_zone_start_forehand = player.x
    forehand_zone_end_forehand = player.x + (player.width // 2)

    if time.time() - ball.last_collision_time < collision_cooldown:
        return score
    MAX_SPEED = 8

    if player.x <= ball.x <= player.x + player.width and player.y <= ball.y - ball.radius <= player.y + player.height:
        ball.y_vel *= -1
        ball.last_collision_time = time.time()
        ball.x_vel = (ball.x - (player.x + player.width // 2)) // 20

        if forehand_zone_start <= ball.x <= forehand_zone_end:
            score += 1

    if ball.x + ball.radius >= WIDTH:
        ball.x = WIDTH - ball.radius
        ball.x_vel *= -1
    if ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.x_vel *= -1

    if ball.y + ball.radius >= HEIGHT:
        ball.y = HEIGHT - ball.radius
        ball.y_vel *= -1
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.y_vel *= -1

    if abs(ball.x_vel) > MAX_SPEED:
        ball.x_vel = (ball.x_vel / abs(ball.x_vel)) * MAX_SPEED

    return score

def handle_backhand_collision(ball, player, score, collision_cooldown = 3):
    backhand_zone_start_backhand = player.x + (player.width // 2)
    backhand_zone_end_backhand = player.x + player.width

    if time.time() - ball.last_collision_time < collision_cooldown:
        return score
    MAX_SPEED = 8

    if player.x <= ball.x <= player.x + player.width and player.y <= ball.y - ball.radius <= player.y + player.height:
        ball.y_vel *= -1
        ball.last_collision_time = time.time()
        ball.x_vel = (ball.x - (player.x + player.width // 2)) // 20

        if backhand_zone_start <= ball.x <= backhand_zone_end:
            score += 1

    if ball.x + ball.radius >= WIDTH:
        ball.x = WIDTH - ball.radius
        ball.x_vel *= -1
    if ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.x_vel *= -1

    if ball.y + ball.radius >= HEIGHT:
        ball.y = HEIGHT - ball.radius
        ball.y_vel *= -1
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.y_vel *= -1

    if abs(ball.x_vel) > MAX_SPEED:
        ball.x_vel = (ball.x_vel / abs(ball.x_vel)) * MAX_SPEED

    return score


# Define an updated player movement function for unrestricted movement
def handle_player_movement_anywhere(keys, player):
    # The player can move freely within the game boundaries
    if keys[pygame.K_d] and player.x + player.width + player.VEL <= WIDTH:
        player.move(right=True)
    if keys[pygame.K_a] and player.x - player.VEL >= 0:
        player.move(right=False)

    if keys[pygame.K_w] and player.y - player.VEL >= 0:
        player.y -= player.VEL
    if keys[pygame.K_s] and player.y + player.height + player.VEL <= HEIGHT:
        player.y += player.VEL


# Game mode functions
def start_vs_player_game():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ace Academy - VS Player Mode")

    left_player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), 10, PLAYER_WIDTH, PLAYER_HEIGHT)
    right_player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), HEIGHT - 10 - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, "tennis_ball.png")

    left_score = 0
    right_score = 0
    players = [left_player, right_player]

    serving = True
    power_level = POWER_MIN
    power_direction = 1
    clock = pygame.time.Clock()

    holding_space = False
    power_building = False
    left_serve = True

    while True:
        clock.tick(FPS)
        draw(WIN, players, ball, left_score, right_score, power_level)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and serving:
                holding_space = True
                power_building = True

            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and serving:
                holding_space = False
                if power_building:
                    if left_serve:
                        ball.y = left_player.y + left_player.height
                        ball.y_vel = ball.MAX_VEL * power_level
                        ball.x = left_player.x + left_player.width // 2
                    else:
                        ball.y = right_player.y
                        ball.y_vel = -ball.MAX_VEL * power_level
                        ball.x = right_player.x + right_player.width // 2
                        
                    serving = False
                    power_building = False
                    power_level = POWER_MIN
        
        keys = pygame.key.get_pressed()
        handle_player_movement(keys, left_player, right_player)

        if not serving:
            ball.move()
            handle_collision(ball, left_player, right_player)

        if ball.y < 0:
            right_score += 1
            ball.reset()
            left_player.reset()
            right_player.reset()
            ball.x = right_player.x + right_player.width // 2
            ball.y = right_player.y  - ball.radius
            left_serve = False
            serving = True

        elif ball.y > HEIGHT:
            left_score += 1
            ball.reset()
            left_player.reset()
            right_player.reset()
            ball.x = left_player.x + left_player.width // 2
            ball.y = left_player.y + left_player.height
            left_serve = True
            serving = True

        if left_score >= WINNING_SCORE:
            break
        elif right_score >= WINNING_SCORE:
            break

    # Reset the scores and player positions for the next game
    left_score = 0
    right_score = 0
    left_player.reset()
    right_player.reset()
    ball.reset()

def start_vs_ai_gamemode():
    # Set up the game for AI versus player mode
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ace Academy - VS AI Mode")

    # Create players and ball
    left_player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), 10, PLAYER_WIDTH, PLAYER_HEIGHT)
    right_player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), HEIGHT - 10 - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, "tennis_ball.png")

    # Initialize game variables
    left_score = 0
    right_score = 0
    players = [left_player, right_player]
    serving = True
    power_level = POWER_MIN
    power_direction = 1
    clock = pygame.time.Clock()

    holding_space = False
    power_building = False
    left_serve = True  # Left player serves

    # Main game loop
    while True:
        clock.tick(FPS)
        draw(WIN, players, ball, left_score, right_score, power_level)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Start power building when space bar is held down
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and serving:
                holding_space = True
                power_building = True

            # Serve when space bar is released
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and serving:
                holding_space = False
                if power_building:
                    ball.y = left_player.y + left_player.height
                    ball.y_vel = ball.MAX_VEL * power_level
                    ball.x = left_player.x + left_player.width // 2

                    serving = False  # Serving done
                    power_building = False
                    power_level = POWER_MIN
        
        # Player and AI movements
        keys = pygame.key.get_pressed()
        handle_player_movement(keys, left_player, right_player)
        handle_ai_movement(ball, right_player)

        # Power level increment when holding space bar
        if holding_space and power_building:
            power_level += POWER_INCREMENT * power_direction
            if power_level >= POWER_MAX:
                power_direction = -1
            elif power_level <= POWER_MIN:
                power_direction = 1

        # Ball movement and collision handling
        if not serving:
            ball.move()
            handle_collision(ball, left_player, right_player)

        # Ball goes off the top, right player scores
        if ball.y < 0:
            right_score += 1
            ball.reset()  # Reset the ball
            serving = True  # Restart serving
            left_player.reset()  # Reset players
            right_player.reset()
        
        # Ball goes off the bottom, left player scores
        elif ball.y > HEIGHT:
            left_score += 1
            ball.reset()
            serving = True
            left_player.reset()
            right_player.reset()

        # Check for winning condition
        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            break

    # Reset the scores and player positions for the next game
    left_score = 0
    right_score = 0
    left_player.reset()
    right_player.reset()
    ball.reset()


def start_forehand_learning():
    # Set up the game display
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ace Academy - Forehand Learning Mode")

    # Set up player, ball, and game variables
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), 10, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    # Set the initial ball position and velocity
    initial_ball_y_vel = 15  # Change this value to set a different initial velocity
    ball = Ball(WIDTH // 2, 10 + PLAYER_HEIGHT, BALL_RADIUS, 'tennis_ball.png')
    ball.y_vel = initial_ball_y_vel  # Set the initial velocity for the ball

    score = 0
    running = True

    while running:
        clock.tick(FPS)
        draw(WIN, [player], ball, score, 0, POWER_MIN)  # Draw the game screen

        # Handle player movement and collisions
        keys = pygame.key.get_pressed()
        handle_player_movement_anywhere(keys, player)
        score = handle_forehand_collision(ball, player, score)  # Handle forehand collision

        # Move the ball
        ball.move()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit loop if quit event is detected
                break

        # Check if learning objective is completed
        if score >= WINNING_SCORE:
            text = SCORE_FONT.render("You managed to hit 10 forehand shots", 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(2000)  # Pause for 2 seconds
            score = 0  # Reset score

    pygame.quit()  # Exit Pygame when done
  

def start_backhand_learning():
    # Set up the game display
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ace Academy - Backhand Learning Mode")

    # Set up player, ball, and game variables
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), 10, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    # Set the initial ball position and velocity
    initial_ball_y_vel = 15  # Change this value to set a different initial velocity
    ball = Ball(WIDTH // 2, 10 + PLAYER_HEIGHT, BALL_RADIUS, 'tennis_ball.png')
    ball.y_vel = initial_ball_y_vel  # Set the initial velocity for the ball

    score = 0
    running = True

    while running:
        clock.tick(FPS)
        draw(WIN, [player], ball, score, 0, POWER_MIN)  # Draw the game screen

        # Handle player movement and collisions
        keys = pygame.key.get_pressed()
        handle_player_movement_anywhere(keys, player)
        score = handle_backhand_collision(ball, player, score)  # Handle backhand collision

        # Move the ball
        ball.move()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit loop if quit event is detected
                break

        # Check if learning objective is completed
        if score >= WINNING_SCORE:
            text = SCORE_FONT.render("You managed to hit 10 backhand shots", 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(2000)  # Pause for 2 seconds
            score = 0  # Reset score

    pygame.quit()  # Exit Pygame when donea

def start_serve_learning():
    # Initialize game screen
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ace Academy - Serve Learning Mode")

    # Set up clock and player position
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2 - (PLAYER_WIDTH // 2), HEIGHT - 10 - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
    
    # Initialize ball position and other variables
    ball = Ball(WIDTH // 2, HEIGHT - 10 - PLAYER_HEIGHT, BALL_RADIUS, 'tennis_ball.png')
    ball.y_vel = 0
    ball.x_vel = 0

    power_level = POWER_MIN
    serving = True
    holding_space = False
    power_building = False
    power_direction = 1
    score = 0  # Initialize score

    while True:
        clock.tick(FPS)
        draw(WIN, [player], ball, score, 0, power_level)  # Draw with current score and power level

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Power building when holding space
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and serving:
                holding_space = True
                power_building = True

            # Serve when space bar is released
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE and serving:
                holding_space = False
                if power_building:
                    # Check if power level is above 80% of the max power
                    if power_level >= 0.8 * POWER_MAX:
                        score += 1  # Increment score for a high-power serve
                    # Serve the ball
                    ball.y = player.y - BALL_RADIUS  # Serve from player's position
                    ball.y_vel = -ball.MAX_VEL * power_level  # Velocity based on power level
                    ball.x = player.x + player.width // 2
                    serving = False  # Serving completed
                    power_building = False
                    power_level = POWER_MIN  # Reset power level

        # Handle power level increment during serving
        if holding_space and power_building:
            power_level += POWER_INCREMENT * power_direction
            if power_level >= POWER_MAX:
                power_direction = -1
            elif power_level <= POWER_MIN:
                power_direction = 1

        # Move the ball if not serving
        if not serving:
            ball.move()

            # Reset after ball leaves the screen (simulate successful serve)
            if ball.y < 0:
                ball.reset()  # Reset ball position and velocity
                serving = True  # Reset to allow for another serve

        # Check if the winning score is achieved
        if score >= WINNING_SCORE:
            # Display success message when winning score is achieved
            text = SCORE_FONT.render("Congratulations! You served 10 times!", 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            time.sleep(2)  # Pause for a couple of seconds
            pygame.quit()  # Quit after achieving the goal
            break

        pygame.display.update()  # Update the game screen




# Main menu setup
mainmenu = pygame_menu.Menu("Ace Academy", 800, 800, theme=pygame_menu.themes.THEME_SOLARIZED)
mainmenu.add.text_input("Name: ", default="", maxchar=20)
mainmenu.add.button("Select Gamemode", lambda: mainmenu._open(gamemode))
mainmenu.add.button("Options", lambda: mainmenu._open(options))
mainmenu.add.button("Quit", pygame_menu.events.EXIT)

# Gamemode menu setup
gamemode = pygame_menu.Menu("Select Gamemode", 800, 800, theme=pygame_menu.themes.THEME_SOLARIZED)
gamemode.add.button("Learn", lambda: mainmenu._open(learn))
gamemode.add.button("VS AI", start_vs_ai_gamemode)
gamemode.add.button("VS Player", start_vs_player_game)  # Start "VS Player" mode

# Options menu setup
options = pygame_menu.Menu("Options", 800, 800, theme=pygame_menu.themes.THEME_SOLARIZED)
options.add.selector("Volume:", [("Low", 1), ("Medium", 2), ("High", 3)])
options.add.selector("Graphics:", [("Low", 1), ("Medium", 2), ("High", 3)])

# Additional menus
learn = pygame_menu.Menu("Learn Menu", 800, 800, theme=pygame_menu.themes.THEME_GREEN)
learn.add.button("Forhand", start_forehand_learning)
learn.add.button("Backhand", start_backhand_learning)
learn.add.button("Serve", start_serve_learning)


# Main menu loop
def run_main_menu():
    while True:
        events = pygame.event.get()
        if mainmenu.is_enabled():
            mainmenu.update(events)
            mainmenu.draw(surface)

        pygame.display.update()

# Start the main menu loop
if __name__ == "__main__":
    run_main_menu()  # Run the main menu system
