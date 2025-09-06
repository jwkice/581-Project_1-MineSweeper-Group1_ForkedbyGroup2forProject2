import pygame 
import random

pygame.init()

def generate_bombs(rows, cols, bomb_count):
    """
    Returns a set of (row, col) positions for bombs.
    Clamps bomb_count to the number of cells.
    """
    total = rows * cols
    bomb_count = max(0, min(bomb_count, total))
    choices = random.sample(range(total), bomb_count)  # unique cells
    return {(i // cols, i % cols) for i in choices}

def main():
    # Size of board
    board_width = 500
    board_height = 500

    # Grid size
    board_rows = 10
    board_columns = 10
    cell_size = board_width // board_columns

    screen = pygame.display.set_mode((board_width, board_height))
    pygame.display.set_caption("Minesweeper Grid")

    # Create a 2D grid
    grid = [[0 for _ in range(board_columns)] for _ in range(board_rows)]

    # Place bombs and mark grid with -1
    bomb_count = 15  # tweak as you like
    bombs = generate_bombs(board_rows, board_columns, bomb_count)
    for r, c in bombs:
        grid[r][c] = -1


    print(f"💣 Bombs placed: {len(bombs)} / {bomb_count}  ✅  Grid: {board_rows}x{board_columns} 🧩")

    revealed = set()  # NEW: track revealed cells as (row, col) pairs

    running = True
    while running:
        screen.fill((255, 255, 255))  # white background

        # --- INPUT (mouse clicks) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #left-click reveals a single cell
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                col = mx // cell_size
                row = my // cell_size
                # ensure inside grid
                if 0 <= row < board_rows and 0 <= col < board_columns:
                    revealed.add((row, col))

        # --- DRAW GRID + REVEALS ---
        for row in range(board_rows):
            for col in range(board_columns):
                x = col * cell_size
                y = row * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)

                if (row, col) in revealed:
                    if grid[row][col] == -1:
                        # bomb cell revealed: light red + small black circle
                        pygame.draw.rect(screen, (255, 180, 180), rect)
                        pygame.draw.circle(screen, (0, 0, 0), rect.center, cell_size // 6)
                    else:
                        # safe cell revealed: light gray
                        pygame.draw.rect(screen, (220, 220, 220), rect)
                else:
                    # hidden cell: white (already from fill)
                    pass

                # cell border
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
