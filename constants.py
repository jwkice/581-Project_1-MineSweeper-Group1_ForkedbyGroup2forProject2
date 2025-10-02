"""
Constants for the Minesweeper game
"""

# Display settings
BOARD_WIDTH = 500
BOARD_HEIGHT = 600
UI_HEIGHT = 100

# Color definitions
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_LIGHT_GRAY = (230, 230, 230)
COLOR_GRAY = (200, 200, 200)
COLOR_RED = (255, 0, 0)
COLOR_DARK_RED = (200, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_DARK_GREEN = (0, 128, 0)
COLOR_BOMB_RED = (255, 100, 100)
COLOR_BROWN = (139, 69, 19)

# Number colors for revealed cells
NUMBER_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (128, 0, 128),
    5: (128, 0, 0),
    6: (64, 224, 208),
    7: (0, 0, 0),
    8: (128, 128, 128),
}

# Direction offsets for neighbor checking
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]
