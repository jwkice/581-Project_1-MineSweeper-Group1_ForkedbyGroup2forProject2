import pygame

pygame.init()

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

    running = True
    while running:
        screen.fill((255, 255, 255))  # white background

        # Draw the grid
        for row in range(board_rows):
            for col in range(board_columns):
                rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # black border

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
