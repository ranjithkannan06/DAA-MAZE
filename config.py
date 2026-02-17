import pygame

# Screen Dimensions
WIDTH = 1200
HEIGHT = 800
FPS = 60

# Colors (Cyber Dark Theme)
COLOR_BG = (10, 12, 16)         # Deep Slate
COLOR_WALL = (25, 28, 35)       # Muted Dark Grid
COLOR_PATH = (220, 225, 235)    # Off-White Path
COLOR_START = (0, 255, 128)      # Spring Green (Start)
COLOR_GOAL = (191, 0, 255)       # Electric Purple (Goal)
COLOR_PLAYER = (0, 200, 255)     # Deep Cyan
COLOR_AI = (255, 80, 0)          # Cyber Orange
COLOR_TRAP = (255, 40, 80)       # Neon Rose
COLOR_POWERUP = (0, 255, 200)    # Seafoam Neon
COLOR_TEXT = (210, 220, 240)
COLOR_GRAPH_EDGE = (60, 70, 90, 60)
COLOR_HEURISTIC = (130, 140, 160)
COLOR_ANNOTATION = (255, 255, 0)
COLOR_FOG = (5, 6, 8, 245)
COLOR_PATH_TRAIL_PLAYER = (0, 200, 255, 40)
COLOR_PATH_TRAIL_AI = (255, 80, 0, 40)
COLOR_UI_PANEL = (15, 20, 25, 210) # Solid Tech Panel

# Gradients & Tech Effects
COLOR_GRADIENT_START = (18, 20, 28)
COLOR_GRADIENT_END = (8, 10, 14)
COLOR_TECH_GLOW = (0, 255, 128, 30)
COLOR_GRID_LINE = (30, 35, 45)

# Animation Settings
ANIM_SPEED_PULSE = 0.05
ANIM_SPEED_MOVE = 0.2  # Interpolation factor (0.1 to 1.0)

# Grid Settings
TILE_SIZE = 40
UI_PANEL_WIDTH = 300

# Weights
WEIGHT_NORMAL = 1
WEIGHT_TRAP = 3
WEIGHT_POWERUP = -2

# Difficulty Settings
DIFFICULTIES = {
    '1': {'name': 'Easy', 'grid_size': (15, 15)},
    '2': {'name': 'Medium', 'grid_size': (21, 21)},
    '3': {'name': 'Hard', 'grid_size': (31, 25)}
}

# Controls
CONTROLS = {
    'UP': pygame.K_w,
    'DOWN': pygame.K_s,
    'LEFT': pygame.K_a,
    'RIGHT': pygame.K_d,
    'UP_LEFT': pygame.K_q,
    'UP_RIGHT': pygame.K_e,
    'DOWN_LEFT': pygame.K_z,
    'DOWN_RIGHT': pygame.K_c,
    'UP_ALT': pygame.K_UP,
    'DOWN_ALT': pygame.K_DOWN,
    'LEFT_ALT': pygame.K_LEFT,
    'RIGHT_ALT': pygame.K_RIGHT,
    'TOGGLE_GRAPH': pygame.K_g,
    'TOGGLE_HEURISTIC': pygame.K_h,
    'TOGGLE_AI_ANNOTATION': pygame.K_a,
    'TOGGLE_PAUSE': pygame.K_SPACE,
    'START': pygame.K_RETURN
}
