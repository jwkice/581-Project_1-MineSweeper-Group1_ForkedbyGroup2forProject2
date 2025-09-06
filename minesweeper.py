import pygame 
import random

pygame.init()

NUM_BOMBS: int = 30
BOARD_WIDTH: int = 500
BOARD_HEIGHT: int = 500

def generate_bombs(rows: int, cols: int, bomb_count: int) -> set[tuple[int, int]]:
    """
    Returns a set of (row, col) positions for bombs.
    Clamps bomb_count to the number of cells.
    """
    total = rows * cols
    bomb_count = max(0, min(bomb_count, total))
    choices = random.sample(range(total), bomb_count)  # unique cells
    return {(i // cols, i % cols) for i in choices}

def ensure_safe_start(grid: list[list[int]], start_row: int, start_col: int, bomb_positions: set[tuple[int, int]]) -> tuple[list[list[int]], set[tuple[int, int]]]:
    """
    Ensures the first click in minesweeper is safe and opens up an area.
    Moves bombs if needed.
   """
    rows, cols = len(grid), len(grid[0])
    protected_area = set()
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r, c = start_row + dr, start_col + dc
            if 0 <= r < rows and 0 <= c < cols:
                protected_area.add((r, c))
    bombs_to_move = bomb_positions & protected_area
    if bombs_to_move:
        all_positions = {(r, c) for r in range(rows) for c in range(cols)}
        available_positions = all_positions - bomb_positions - protected_area
        new_bomb_positions = bomb_positions.copy()
        for bomb_pos in bombs_to_move:
            if available_positions:
                new_pos = available_positions.pop()
                new_bomb_positions.remove(bomb_pos)
                new_bomb_positions.add(new_pos)
                grid[bomb_pos[0]][bomb_pos[1]] = 0
                grid[new_pos[0]][new_pos[1]] = -1
        generate_numbers(grid) #this could be optimized to only update affected areas
        return grid, new_bomb_positions
    return grid, bomb_positions


def flood_fill(grid: list[list[int]], start_row: int, start_col: int) -> set[tuple[int, int]]:
    """
    Floodfill that reveals cells with 0 bombs around them, and stops at cells with numbers.
    """
    if not grid or not grid[0]:
        return set()
    
    rows = len(grid)
    cols = len(grid[0])
    if (start_row < 0 or start_row >= rows or 
        start_col < 0 or start_col >= cols or 
        grid[start_row][start_col] == -1):
        return set()
    to_reveal = set()
    to_visit = [(start_row, start_col)]
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    while to_visit:
        row, col = to_visit.pop()
        if (row < 0 or row >= rows or col < 0 or col >= cols or
            (row, col) in to_reveal):
            continue
        if grid[row][col] == -1:
            continue
        to_reveal.add((row, col))
        if grid[row][col] > 0:
            continue
        if grid[row][col] == 0:
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < rows and 0 <= new_col < cols and
                    (new_row, new_col) not in to_reveal):
                    to_visit.append((new_row, new_col))
    return to_reveal

def generate_numbers(grid):
    """
    Fill in the grid with numbers based on how mnay bombs its near
    """
    rows = len(grid)
    cols = len(grid[0])
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != -1:
                bomb_count = 0
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if grid[ni][nj] == -1:
                            bomb_count += 1
                grid[i][j] = bomb_count

def main():
    # Grid size
    board_rows = 10
    board_columns = 10
    cell_size = BOARD_WIDTH // board_columns

    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption("Minesweeper Grid")

    # Create a 2D grid
    grid = [[0 for _ in range(board_columns)] for _ in range(board_rows)]

    # Place bombs and mark grid with -1
    bombs = generate_bombs(board_rows, board_columns, NUM_BOMBS)
    for r, c in bombs:
        grid[r][c] = -1
    generate_numbers(grid)
    pygame.font.init()
    font = pygame.font.Font(None, cell_size // 2)
    print(f"💣 Bombs placed: {len(bombs)} / {NUM_BOMBS}  ✅  Grid: {board_rows}x{board_columns} 🧩")

    revealed = set()  # track revealed cells as (row, col) pairs
    first_click = True
    running = True
    while running:
        screen.fill((255, 255, 255))  # white background

        # --- INPUT (mouse clicks) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                col = mx // cell_size
                row = my // cell_size
                if 0 <= row < board_rows and 0 <= col < board_columns:
                    if first_click:
                        grid, bombs = ensure_safe_start(grid, row, col, bombs)
                        first_click = False
                    if grid[row][col] == -1:
                        revealed.add((row, col))
                    else:
                        new_reveals = flood_fill(grid, row, col)
                        revealed.update(new_reveals)

        # --- DRAW GRID + REVEALS ---
        for row in range(board_rows):
            for col in range(board_columns):
                x = col * cell_size
                y = row * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)
                if (row, col) in revealed:
                    if grid[row][col] == -1:
                        pygame.draw.rect(screen, (255, 100, 100), rect)
                        center = rect.center
                        pygame.draw.circle(screen, (0, 0, 0), center, cell_size // 4)
                    else:
                        # safe cell revealed: light gray
                        pygame.draw.rect(screen, (210, 210, 210), rect)
                        number = grid[row][col]
                        if number > 0:
                            number_colors = {
                                1: (0, 0, 255),
                                2: (0, 128, 0),
                                3: (255, 0, 0),
                                4: (128, 0, 128),
                                5: (128, 0, 0),
                                6: (64, 224, 208),
                                7: (0, 0, 0),
                                8: (128, 128, 128),
                            }
                            color = number_colors.get(number, (0, 0, 0))
                            text_surface = font.render(str(number), True, color)
                            text_rect = text_surface.get_rect(center=rect.center)
                            screen.blit(text_surface, text_rect)
                # cell border
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        pygame.display.flip()
    pygame.quit()

main()
