import os
import pygame 
import random
import time

pygame.init()
os.system('clear' if os.name != 'nt' else 'cls') # gets rid of stupid warning

BOARD_WIDTH: int = 500
BOARD_HEIGHT: int = 600
UI_HEIGHT: int = 100 

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
    bombs_to_move = bomb_positions & protected_area #set union
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
    Floodfill algorithm that reveals cells with 0 bombs around them, and stops at cells with numbers.
    """
    if not grid or not grid[0]:
        return set()
    #define helper variables and preallocations
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
    # flood
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

def draw_game_over_popup(screen, width, height, ai_mode, players_turn, game_won=False):
    """Draw a game over popup with play again and quit buttons"""
    # Semi-transparent overlay
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Popup background
    popup_width = 300
    popup_height = 200
    popup_x = (width - popup_width) // 2
    popup_y = (height - popup_height) // 2
    
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, (255, 255, 255), popup_rect)
    pygame.draw.rect(screen, (0, 0, 0), popup_rect, 3)
    
    # Title
    title_font = pygame.font.Font(None, 36)
    if ai_mode == 'interactive':
        if game_won:
            if not players_turn:    #Turns are switched after every move. Whoever's turn it is NOT played the last move
                #Player made final move
                title_text = 'You Won!'
            else:
                #Computer made final move
                title_text = 'Computer Won!'
        else:
            if not players_turn:
                #Player made final move
                title_text = 'Game Over! You Lost!'
            else:
                #Computer made final move
                title_text = 'Game Over! Computer Lost!'
    elif ai_mode == 'automatic':
        title_text = "Computer Won!" if game_won else "Game Over!"
    else:
        title_text = "You Won!" if game_won else "Game Over!"
    title_color = (0, 128, 0) if game_won else (255, 0, 0)
    title_surface = title_font.render(title_text, True, title_color)
    title_rect = title_surface.get_rect(center=(popup_x + popup_width//2, popup_y + 50))
    screen.blit(title_surface, title_rect)
    
    # Buttons
    button_font = pygame.font.Font(None, 24)
    
    # Play Again button
    play_again_rect = pygame.Rect(popup_x + 20, popup_y + 100, 100, 40)
    pygame.draw.rect(screen, (0, 200, 0), play_again_rect)
    pygame.draw.rect(screen, (0, 0, 0), play_again_rect, 2)
    play_again_text = button_font.render("Play Again", True, (255, 255, 255))
    play_again_text_rect = play_again_text.get_rect(center=play_again_rect.center)
    screen.blit(play_again_text, play_again_text_rect)
    
    # Quit button
    quit_rect = pygame.Rect(popup_x + 180, popup_y + 100, 100, 40)
    pygame.draw.rect(screen, (200, 0, 0), quit_rect)
    pygame.draw.rect(screen, (0, 0, 0), quit_rect, 2)
    quit_text = button_font.render("Quit", True, (255, 255, 255))
    quit_text_rect = quit_text.get_rect(center=quit_rect.center)
    screen.blit(quit_text, quit_text_rect)
    
    return play_again_rect, quit_rect


def hidden_neighbors(row, col, revealed, flagged, board_rows, board_cols):
    '''For a given cell (row, col), returns the number of neighboring cells that are not revealed or flagged'''
    hidden = 0
    for i in range(-1, 2):
        if row+i >= 0 and row+i < board_rows:
            for j in range(-1, 2):
                if (col+j >= 0 and col+j < board_cols) and (i != 0 or j != 0):
                    if ((row+i, col+j) not in revealed) and ((row+i, col+j) not in flagged):
                        hidden += 1
    return hidden

def flagged_neighbors(row, col, flagged, board_rows, board_cols):
    '''For a given cell (row, col), returns the number of neighboring cells that are flagged'''
    num_flagged = 0
    for i in range(-1, 2):
        if row+i >= 0 and row+i < board_rows:
            for j in range(-1, 2):
                if (col+j >= 0 and col+j < board_cols) and (i != 0 or j != 0):
                    if (row+i, col+j) in flagged:
                        num_flagged += 1
    return num_flagged

def is_hidden(row, col, revealed, flagged):
    '''For a given cell (row, col), returns True if the cell is not in revealed or flagged'''
    return ((row, col) not in revealed) and ((row, col) not in flagged)

def main():
    # Grid size

    # get user values for board size and bombs
    print("===== MINESWEEPER =====\n-----------\n Settings |\n-----------\n ")
    board_rows = int(input("Rows? "))
    board_columns = int(input("Columns? "))
    NUM_BOMBS = int(input("Bombs? "))

    if board_rows < board_columns:
        cell_size = (BOARD_WIDTH - UI_HEIGHT) // board_columns
    
    else:
        cell_size = (BOARD_HEIGHT - UI_HEIGHT) // board_rows

    # ask if use wants to use AI
    ai_bool_query = input("AI? (on/off): ").lower()
    if ai_bool_query == 'on':
        ai_type_query = input("Interactive or Automatic? (interactive/automatic): ").lower() #interactive anything else is automatic
        ai_level_query = input("AI Difficulty? (easy/medium/hard): ").lower() #medium for medium, hard for hard, anything else for easy
        
        match ai_type_query:
            case 'interactive':
                ai_mode = 'interactive'
            case _:
                ai_mode = 'automatic'
        
        match ai_level_query:
            case 'hard':
                ai_level = 'hard'

            case 'medium':
                ai_level = 'medium'

            case _:
                ai_level = 'easy'
    
    else:
        ai_mode = 'off'

    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption("Minesweeper")

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
    flagged = set()   # track flagged cells as (row, col) pairs
    first_click = True
    running = True
    game_over = False
    game_won = False
    start_time = time.time()
    game_started = False
    
    
    players_turn = True  #for interactive mode: True if it is player's turn, False if it is computer's turn

    while running:

        screen.fill((255, 255, 255))  # white background
        
        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_surface = title_font.render("MINESWEEPER", True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(BOARD_WIDTH//2, 30))
        screen.blit(title_surface, title_rect)
        
        # Draw timer
        if game_started and not game_over:
            elapsed_time = int(time.time() - start_time)
            timer_font = pygame.font.Font(None, 24)
            timer_surface = timer_font.render(f"Time: {elapsed_time}s", True, (0, 0, 0))
            screen.blit(timer_surface, (10, 60))
        
        # Draw bomb count and flag count
        bomb_font = pygame.font.Font(None, 24)
        remaining_bombs = NUM_BOMBS - len(flagged)
        bomb_surface = bomb_font.render(f"Bombs: {remaining_bombs}", True, (0, 0, 0))
        screen.blit(bomb_surface, (BOARD_WIDTH - 100, 60))

        

        # AI Solver
        if not game_over and (ai_mode == 'automatic' or (ai_mode == 'interactive' and not players_turn)):
            time.sleep(1)
            found = False
            if ai_level == 'medium' or ai_level == 'hard':
                for row in range(board_rows):
                    for col in range(board_columns):
                        if (row, col) in revealed and hidden_neighbors(row, col, revealed, flagged, board_rows, board_columns) != 0:
                            if grid[row][col] == flagged_neighbors(row, col, flagged, board_rows, board_columns):
                                #Number of flagged neighbors equal to number of adjacent bombs
                                found = True
                                cell_revealed = False
                                for i in range(-1, 2):
                                    if row+i >= 0 and row+i < board_rows:
                                        for j in range(-1, 2):
                                            if (col+j >= 0 and col+j < board_columns) and (i != 0 or j != 0):
                                                if is_hidden(row+i, col+j, revealed, flagged):
                                                    #Neighbor cell is hidden, reveal neighbor
                                                    if grid[row+i][col+j] == -1:
                                                        revealed.add((row+i, col+j))
                                                        game_over = True
                                                    else:
                                                        new_reveals = flood_fill(grid, row+i, col+j)
                                                        revealed.update(new_reveals)
                                                        
                                                        # Check for win condition
                                                        total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                                        if len(revealed) == total_safe_cells:
                                                            game_won = True
                                                            game_over = True
                                                    players_turn = True
                                                    cell_revealed = True
                                                    break
                                        if cell_revealed:
                                            break
                            elif grid[row][col] == (hidden_neighbors(row, col, revealed, flagged, board_rows, board_columns) + flagged_neighbors(row, col, flagged, board_rows, board_columns)):
                                #Number of hidden neighbors equal to number of adjacent bombs
                                found = True
                                cell_flagged = False
                                for i in range(-1, 2):
                                    if row+i >= 0 and row+i < board_rows:
                                        for j in range(-1, 2):
                                            if (col+j >= 0 and col+j < board_columns) and (i != 0 or j != 0):
                                                if is_hidden(row+i, col+j, revealed, flagged):
                                                    #Neighbor cell is hidden, flag neighbor
                                                    flagged.add((row+i, col+j))
                                                    players_turn = True
                                                    cell_flagged = True
                                                    break
                                        if cell_flagged:
                                            break
                        if found:
                            break
                    if found:
                        break
            
            if not found and ai_level == 'hard':
                #1-2-1 pattern rule
                found = False
                for row in range(board_rows):
                    for col in range(board_columns):
                        if grid[row][col] == 2: #Identified revealed cell with 2
                            if row-1 >= 0 and row+1 < board_rows and col-1 >= 0 and col+1 < board_columns:  #2 cell is not on the edge
                                if (grid[row-1][col] == 1 and grid[row+1][col] == 1) or (grid[row][col-1] == 1 and grid[row][col+1] == 1): #Found 1-2-1 pattern
                                    if is_hidden(row-1, col-1, revealed, flagged) and is_hidden(row+1, col-1, revealed, flagged) and is_hidden(row-1, col+1, revealed, flagged) and is_hidden(row+1, col+1, revealed, flagged): #All corners are hidden
                                        if (grid[row-1][col] == 1 and grid[row+1][col] == 1):   #Pattern is across rows
                                            if is_hidden(row, col-1, revealed, flagged):
                                                if grid[row][col-1] == -1:
                                                    revealed.add((row, col-1))
                                                    game_over = True
                                                else:
                                                    new_reveals = flood_fill(grid, row, col-1)
                                                    revealed.update(new_reveals)
                                                    
                                                    # Check for win condition
                                                    total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                                    if len(revealed) == total_safe_cells:
                                                        game_won = True
                                                        game_over = True
                                                found = True
                                                players_turn = True
                                            elif is_hidden(row, col+1, revealed, flagged):
                                                if grid[row][col+1] == -1:
                                                    revealed.add((row, col+1))
                                                    game_over = True
                                                else:
                                                    new_reveals = flood_fill(grid, row, col+1)
                                                    revealed.update(new_reveals)
                                                    
                                                    # Check for win condition
                                                    total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                                    if len(revealed) == total_safe_cells:
                                                        game_won = True
                                                        game_over = True
                                                found = True
                                                players_turn = True
                                        elif (grid[row][col-1] == 1 and grid[row][col+1] == 1):   #Pattern is across cols
                                            if is_hidden(row-1, col, revealed, flagged):
                                                if grid[row-1][col] == -1:
                                                    revealed.add((row-1, col))
                                                    game_over = True
                                                else:
                                                    new_reveals = flood_fill(grid, row-1, col)
                                                    revealed.update(new_reveals)
                                                    
                                                    # Check for win condition
                                                    total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                                    if len(revealed) == total_safe_cells:
                                                        game_won = True
                                                        game_over = True
                                                found = True
                                                players_turn = True
                                            elif is_hidden(row+1, col, revealed, flagged):
                                                if grid[row+1][col] == -1:
                                                    revealed.add((row+1, col))
                                                    game_over = True
                                                else:
                                                    new_reveals = flood_fill(grid, row+1, col)
                                                    revealed.update(new_reveals)
                                                    
                                                    # Check for win condition
                                                    total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                                    if len(revealed) == total_safe_cells:
                                                        game_won = True
                                                        game_over = True
                                                found = True
                                                players_turn = True
                                    elif (row-1, col-1) in revealed:    #Cell offset by -1, -1 is revealed, cell on opposite side of pattern must be bomb
                                        if (grid[row-1][col] == 1 and grid[row+1][col] == 1) and is_hidden(row-1, col+1, revealed, flagged):   #Pattern is across rows and opposite cell is hidden
                                            flagged.add((row-1, col+1))
                                            found = True
                                            players_turn = True
                                        elif (grid[row][col-1] == 1 and grid[row][col+1] == 1) and is_hidden(row+1, col-1, revealed, flagged):   #Pattern is across cols and opposite cell is hidden
                                            flagged.add((row+1, col-1))
                                            found = True
                                            players_turn = True
                                    elif (row+1, col-1) in revealed:    #Cell offset by +1, -1 is revealed, cell on opposite side of pattern must be bomb
                                        if (grid[row-1][col] == 1 and grid[row+1][col] == 1) and is_hidden(row+1, col+1, revealed, flagged):   #Pattern is across rows and opposite cell is hidden
                                            flagged.add((row+1, col+1))
                                            found = True
                                            players_turn = True
                                        elif (grid[row][col-1] == 1 and grid[row][col+1] == 1) and is_hidden(row-1, col-1, revealed, flagged):   #Pattern is across cols and opposite cell is hidden
                                            flagged.add((row-1, col-1))
                                            found = True
                                            players_turn = True
                                    elif (row-1, col+1) in revealed:    #Cell offset by -1, +1 is revealed, cell on opposite side of pattern must be bomb
                                        if (grid[row-1][col] == 1 and grid[row+1][col] == 1) and is_hidden(row-1, col-1, revealed, flagged):   #Pattern is across rows and opposite cell is hidden
                                            flagged.add((row-1, col-1))
                                            found = True
                                            players_turn = True
                                        elif (grid[row][col-1] == 1 and grid[row][col+1] == 1) and is_hidden(row+1, col+1, revealed, flagged):   #Pattern is across cols and opposite cell is hidden
                                            flagged.add((row+1, col+1))
                                            found = True
                                            players_turn = True
                                    elif (row+1, col+1) in revealed:    #Cell offset by +1, +1 is revealed, cell on opposite side of pattern must be bomb
                                        if (grid[row-1][col] == 1 and grid[row+1][col] == 1) and is_hidden(row+1, col-1, revealed, flagged):   #Pattern is across rows and opposite cell is hidden
                                            flagged.add((row+1, col-1))
                                            found = True
                                            players_turn = True
                                        elif (grid[row][col-1] == 1 and grid[row][col+1] == 1) and is_hidden(row-1, col+1, revealed, flagged):   #Pattern is across cols and opposite cell is hidden
                                            flagged.add((row-1, col+1))
                                            found = True
                                            players_turn = True
                        if found:
                            break
                    if found:
                        break
                            
            if not found:
                rand_rows = list(range(board_rows))
                random.shuffle(rand_rows)
                rand_cols = list(range(board_columns))
                random.shuffle(rand_cols)
                cell_revealed = False
                for row in rand_rows:
                    for col in rand_cols:
                        if (row, col) not in flagged and (row, col) not in revealed:  # Can't reveal flagged or already revealed cells
                            if first_click:
                                grid, bombs = ensure_safe_start(grid, row, col, bombs)
                                first_click = False
                                game_started = True
                                start_time = time.time()
                            if grid[row][col] == -1:
                                revealed.add((row, col))
                                game_over = True
                            else:
                                new_reveals = flood_fill(grid, row, col)
                                revealed.update(new_reveals)
                                
                                # Check for win condition
                                total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                if len(revealed) == total_safe_cells:
                                    game_won = True
                                    game_over = True
                            players_turn = True
                            cell_revealed = True
                            break
                    if cell_revealed:
                        break



        # --- INPUT (mouse clicks) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Check if clicking on game over popup buttons
                if game_over:
                    play_again_rect, quit_rect = draw_game_over_popup(screen, BOARD_WIDTH, BOARD_HEIGHT, ai_mode, players_turn, game_won)
                    if play_again_rect.collidepoint(mx, my):
                        # Reset game
                        grid = [[0 for _ in range(board_columns)] for _ in range(board_rows)]
                        bombs = generate_bombs(board_rows, board_columns, NUM_BOMBS)
                        for r, c in bombs:
                            grid[r][c] = -1
                        generate_numbers(grid)
                        revealed = set()
                        flagged = set()
                        first_click = True
                        game_over = False
                        game_won = False
                        game_started = False
                        continue
                    elif quit_rect.collidepoint(mx, my):
                        running = False
                        continue
                
                # Game board clicks (only if not game over)
                if not game_over and my > UI_HEIGHT and ai_mode != 'automatic' and players_turn:
                    col = mx // cell_size
                    row = (my - UI_HEIGHT) // cell_size
                    if 0 <= row < board_rows and 0 <= col < board_columns:
                        # Right click for flagging
                        if event.button == 3:  # Right click
                            if (row, col) not in revealed:
                                if (row, col) in flagged:
                                    flagged.remove((row, col))
                                else:
                                    flagged.add((row, col))
                                if ai_mode == 'interactive':
                                    players_turn = False
                        # Left click for revealing
                        elif event.button == 1:  # Left click
                            if (row, col) not in flagged:  # Can't reveal flagged cells
                                if first_click:
                                    grid, bombs = ensure_safe_start(grid, row, col, bombs)
                                    first_click = False
                                    game_started = True
                                    start_time = time.time()
                                if grid[row][col] == -1:
                                    revealed.add((row, col))
                                    game_over = True
                                else:
                                    new_reveals = flood_fill(grid, row, col)
                                    revealed.update(new_reveals)
                                    
                                    # Check for win condition
                                    total_safe_cells = board_rows * board_columns - NUM_BOMBS
                                    if len(revealed) == total_safe_cells:
                                        game_won = True
                                        game_over = True
                                if ai_mode == 'interactive':
                                    players_turn = False

        #draw board
        for row in range(board_rows):
            for col in range(board_columns):
                x = col * cell_size
                y = row * cell_size + UI_HEIGHT  # Offset for UI
                rect = pygame.Rect(x, y, cell_size, cell_size)
                if (row, col) in revealed:
                    if grid[row][col] == -1:
                        pygame.draw.rect(screen, (255, 100, 100), rect)
                        center = rect.center
                        pygame.draw.circle(screen, (0, 0, 0), center, cell_size // 4)
                    else:
                        # safe cell revealed: light gray
                        pygame.draw.rect(screen, (230, 230, 230), rect)
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
                else:
                    # Unrevealed cells - draw as covered
                    pygame.draw.rect(screen, (200, 200, 200), rect)
                    # Draw flag if cell is flagged
                    if (row, col) in flagged:
                        # Draw a simple flag using pygame shapes
                        flag_size = cell_size // 3
                        flag_x = rect.centerx - flag_size // 2
                        flag_y = rect.centery - flag_size // 2
                        
                        # Flag pole (vertical line)
                        pygame.draw.line(screen, (139, 69, 19), 
                                       (flag_x, flag_y), 
                                       (flag_x, flag_y + flag_size), 3)
                        
                        # Flag (triangle)
                        flag_points = [
                            (flag_x, flag_y),
                            (flag_x + flag_size, flag_y + flag_size // 3),
                            (flag_x, flag_y + 2 * flag_size // 3)
                        ]
                        pygame.draw.polygon(screen, (255, 0, 0), flag_points)
                # cell border
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    
        # Draw game over popup if game is over
        if game_over:
            draw_game_over_popup(screen, BOARD_WIDTH, BOARD_HEIGHT, ai_mode, players_turn, game_won)
        #update display
        pygame.display.flip()
    pygame.quit()

main()
