"""
Main game loop for Minesweeper
"""
import os
import pygame
import time
from constants import *
from grid import generate_bombs, generate_numbers, ensure_safe_start, flood_fill
from ai_solver import try_basic_moves, try_121_pattern, make_random_move
from ui import draw_game_over_popup, draw_board, draw_ui, options


def get_game_settings():
    """Get game settings from user input"""
    print("===== MINESWEEPER =====\n-----------\n Settings |\n-----------\n ")
    board_rows = int(input("Rows? "))
    board_columns = int(input("Columns? "))
    num_bombs = int(input("Bombs? "))
    
    # Calculate cell size
    if board_rows < board_columns:
        cell_size = (BOARD_WIDTH - UI_HEIGHT) // board_columns
    else:
        cell_size = (BOARD_HEIGHT - UI_HEIGHT) // board_rows
    
    # AI settings
    ai_mode = 'off'
    ai_level = 'easy'
    
    ai_bool_query = input("AI? (on/off): ").lower()
    if ai_bool_query == 'on':
        ai_type_query = input("Interactive or Automatic? (interactive/automatic): ").lower()
        ai_level_query = input("AI Difficulty? (easy/medium/hard): ").lower()
        
        ai_mode = 'interactive' if ai_type_query == 'interactive' else 'automatic'
        
        if ai_level_query == 'hard':
            ai_level = 'hard'
        elif ai_level_query == 'medium':
            ai_level = 'medium'
        else:
            ai_level = 'easy'
    
    return board_rows, board_columns, num_bombs, cell_size, ai_mode, ai_level


def initialize_game(board_rows, board_columns, num_bombs):
    """Initialize a new game"""
    grid = [[0 for _ in range(board_columns)] for _ in range(board_rows)]
    bombs = generate_bombs(board_rows, board_columns, num_bombs)
    
    for r, c in bombs:
        grid[r][c] = -1
    generate_numbers(grid)
    
    return grid, bombs


def handle_ai_move(grid, board_rows, board_columns, revealed, flagged, bombs, 
                   ai_level, first_click, game_started, start_time):
    """Execute AI move and return updated game state"""
    time.sleep(1)
    
    # Try basic moves (medium/hard)
    found, move_type, row, col = try_basic_moves(grid, board_rows, board_columns, 
                                                  revealed, flagged, ai_level)
    
    # Try 1-2-1 pattern (hard only)
    if not found and ai_level == 'hard':
        found, move_type, row, col = try_121_pattern(grid, board_rows, board_columns, 
                                                      revealed, flagged)
    
    # Make random move if no pattern found
    if not found:
        found, row, col = make_random_move(board_rows, board_columns, revealed, flagged)
        move_type = 'reveal'
    
    if found:
        if move_type == 'flag':
            flagged.add((row, col))
        elif move_type == 'reveal':
            if first_click:
                grid, bombs = ensure_safe_start(grid, row, col, bombs)
                first_click = False
                game_started = True
                start_time = time.time()
            
            if grid[row][col] == -1:
                revealed.add((row, col))
                return grid, bombs, revealed, flagged, first_click, game_started, start_time, True, False
            else:
                new_reveals = flood_fill(grid, row, col)
                revealed.update(new_reveals)
                
                total_safe_cells = board_rows * board_columns - len(bombs)
                if len(revealed) == total_safe_cells:
                    return grid, bombs, revealed, flagged, first_click, game_started, start_time, True, True
    
    return grid, bombs, revealed, flagged, first_click, game_started, start_time, False, False


def handle_player_click(event, mx, my, cell_size, board_rows, board_columns, grid, 
                       revealed, flagged, bombs, first_click, game_started, start_time):
    """Handle player mouse click"""
    game_over = False
    game_won = False
    
    if my > UI_HEIGHT:
        col = mx // cell_size
        row = (my - UI_HEIGHT) // cell_size
        
        if 0 <= row < board_rows and 0 <= col < board_columns:
            # Right click for flagging
            if event.button == 3:
                if (row, col) not in revealed:
                    if (row, col) in flagged:
                        flagged.remove((row, col))
                    else:
                        flagged.add((row, col))
            
            # Left click for revealing
            elif event.button == 1:
                if (row, col) not in flagged:
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
                        
                        total_safe_cells = board_rows * board_columns - len(bombs)
                        if len(revealed) == total_safe_cells:
                            game_won = True
                            game_over = True
    
    return grid, bombs, revealed, flagged, first_click, game_started, start_time, game_over, game_won


def main():
    pygame.init()
    os.system('clear' if os.name != 'nt' else 'cls')
    
    # Get game settings
    
    # Initialize pygame
    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    pygame.display.set_caption("Minesweeper")

    board_rows, board_columns, num_bombs, ai_mode, ai_level = options(screen)

    if board_rows < board_columns:
        cell_size = (BOARD_WIDTH - UI_HEIGHT) // board_columns
    else:
        cell_size = (BOARD_HEIGHT - UI_HEIGHT) // board_rows

    pygame.font.init()
    font = pygame.font.Font(None, cell_size // 2)
    
    # Initialize game
    grid, bombs = initialize_game(board_rows, board_columns, num_bombs)
    
    print(f"💣 Bombs placed: {len(bombs)} / {num_bombs}  ✅  Grid: {board_rows}x{board_columns} 🧩")
    
    # Game state
    revealed = set()
    flagged = set()
    first_click = True
    running = True
    game_over = False
    game_won = False
    start_time = time.time()
    game_started = False
    players_turn = True
    
    while running:
        screen.fill(COLOR_WHITE)
        
        # Calculate elapsed time
        elapsed_time = int(time.time() - start_time) if game_started and not game_over else 0
        
        # Draw UI
        draw_ui(screen, elapsed_time, num_bombs, len(flagged), game_started, game_over)
        
        # AI move logic
        if not game_over and (ai_mode == 'automatic' or (ai_mode == 'interactive' and not players_turn)):
            result = handle_ai_move(grid, board_rows, board_columns, revealed, flagged, bombs,
                                   ai_level, first_click, game_started, start_time)
            grid, bombs, revealed, flagged, first_click, game_started, start_time, game_over, game_won = result
            players_turn = True
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Handle game over popup clicks
                if game_over:
                    play_again_rect, quit_rect = draw_game_over_popup(screen, BOARD_WIDTH, BOARD_HEIGHT, 
                                                                       ai_mode, players_turn, game_won)
                    if play_again_rect.collidepoint(mx, my):
                        # Reset game
                        grid, bombs = initialize_game(board_rows, board_columns, num_bombs)
                        revealed = set()
                        flagged = set()
                        first_click = True
                        game_over = False
                        game_won = False
                        game_started = False
                        players_turn = True
                        continue
                    elif quit_rect.collidepoint(mx, my):
                        running = False
                        continue
                
                # Handle game board clicks (only if not game over and player's turn)
                if not game_over and ai_mode != 'automatic' and players_turn:
                    result = handle_player_click(event, mx, my, cell_size, board_rows, board_columns,
                                                grid, revealed, flagged, bombs, first_click, 
                                                game_started, start_time)
                    grid, bombs, revealed, flagged, first_click, game_started, start_time, game_over, game_won = result
                    
                    if ai_mode == 'interactive':
                        players_turn = False
        
        # Draw board
        draw_board(screen, grid, board_rows, board_columns, cell_size, revealed, flagged, font)
        
        # Draw game over popup if game is over
        if game_over:
            draw_game_over_popup(screen, BOARD_WIDTH, BOARD_HEIGHT, ai_mode, players_turn, game_won)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()
