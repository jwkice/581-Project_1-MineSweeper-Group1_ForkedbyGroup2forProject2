"""
UI rendering functions for Minesweeper
"""
import pygame
from constants import *


def draw_game_over_popup(screen, width, height, ai_mode, players_turn, game_won=False):
    """Draw a game over popup with play again and quit buttons"""
    # Semi-transparent overlay
    overlay = pygame.Surface((width, height))
    overlay.set_alpha(128)
    overlay.fill(COLOR_BLACK)
    screen.blit(overlay, (0, 0))
    
    # Popup background
    popup_width = 300
    popup_height = 200
    popup_x = (width - popup_width) // 2
    popup_y = (height - popup_height) // 2
    
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    pygame.draw.rect(screen, COLOR_WHITE, popup_rect)
    pygame.draw.rect(screen, COLOR_BLACK, popup_rect, 3)
    
    # Title
    title_font = pygame.font.Font(None, 36)
    if ai_mode == 'interactive':
        if game_won:
            title_text = 'You Won!' if not players_turn else 'Computer Won!'
        else:
            title_text = 'Game Over! You Lost!' if not players_turn else 'Game Over! Computer Lost!'
    elif ai_mode == 'automatic':
        title_text = "Computer Won!" if game_won else "Game Over!"
    else:
        title_text = "You Won!" if game_won else "Game Over!"
    
    title_color = COLOR_DARK_GREEN if game_won else COLOR_RED
    title_surface = title_font.render(title_text, True, title_color)
    title_rect = title_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 50))
    screen.blit(title_surface, title_rect)
    
    # Buttons
    button_font = pygame.font.Font(None, 24)
    
    # Play Again button
    play_again_rect = pygame.Rect(popup_x + 20, popup_y + 100, 100, 40)
    pygame.draw.rect(screen, COLOR_GREEN, play_again_rect)
    pygame.draw.rect(screen, COLOR_BLACK, play_again_rect, 2)
    play_again_text = button_font.render("Play Again", True, COLOR_WHITE)
    play_again_text_rect = play_again_text.get_rect(center=play_again_rect.center)
    screen.blit(play_again_text, play_again_text_rect)
    
    # Quit button
    quit_rect = pygame.Rect(popup_x + 180, popup_y + 100, 100, 40)
    pygame.draw.rect(screen, COLOR_DARK_RED, quit_rect)
    pygame.draw.rect(screen, COLOR_BLACK, quit_rect, 2)
    quit_text = button_font.render("Quit", True, COLOR_WHITE)
    quit_text_rect = quit_text.get_rect(center=quit_rect.center)
    screen.blit(quit_text, quit_text_rect)
    
    return play_again_rect, quit_rect


def draw_board(screen, grid, board_rows, board_cols, cell_size, revealed, flagged, font):
    """Draw the minesweeper board"""
    for row in range(board_rows):
        for col in range(board_cols):
            x = col * cell_size
            y = row * cell_size + UI_HEIGHT
            rect = pygame.Rect(x, y, cell_size, cell_size)
            
            if (row, col) in revealed:
                if grid[row][col] == -1:
                    # Bomb cell
                    pygame.draw.rect(screen, COLOR_BOMB_RED, rect)
                    center = rect.center
                    pygame.draw.circle(screen, COLOR_BLACK, center, cell_size // 4)
                else:
                    # Safe cell revealed
                    pygame.draw.rect(screen, COLOR_LIGHT_GRAY, rect)
                    number = grid[row][col]
                    if number > 0:
                        color = NUMBER_COLORS.get(number, COLOR_BLACK)
                        text_surface = font.render(str(number), True, color)
                        text_rect = text_surface.get_rect(center=rect.center)
                        screen.blit(text_surface, text_rect)
            else:
                # Unrevealed cells
                pygame.draw.rect(screen, COLOR_GRAY, rect)
                
                # Draw flag if cell is flagged
                if (row, col) in flagged:
                    flag_size = cell_size // 3
                    flag_x = rect.centerx - flag_size // 2
                    flag_y = rect.centery - flag_size // 2
                    
                    # Flag pole
                    pygame.draw.line(screen, COLOR_BROWN, 
                                   (flag_x, flag_y), 
                                   (flag_x, flag_y + flag_size), 3)
                    
                    # Flag triangle
                    flag_points = [
                        (flag_x, flag_y),
                        (flag_x + flag_size, flag_y + flag_size // 3),
                        (flag_x, flag_y + 2 * flag_size // 3)
                    ]
                    pygame.draw.polygon(screen, COLOR_RED, flag_points)
            
            # Cell border
            pygame.draw.rect(screen, COLOR_BLACK, rect, 1)


def draw_ui(screen, elapsed_time, num_bombs, num_flagged, game_started, game_over):
    """Draw the UI elements (title, timer, bomb count)"""
    # Title
    title_font = pygame.font.Font(None, 48)
    title_surface = title_font.render("MINESWEEPER", True, COLOR_BLACK)
    title_rect = title_surface.get_rect(center=(BOARD_WIDTH // 2, 30))
    screen.blit(title_surface, title_rect)
    
    # Timer
    if game_started and not game_over:
        timer_font = pygame.font.Font(None, 24)
        timer_surface = timer_font.render(f"Time: {elapsed_time}s", True, COLOR_BLACK)
        screen.blit(timer_surface, (10, 60))
    
    # Bomb count
    bomb_font = pygame.font.Font(None, 24)
    remaining_bombs = num_bombs - num_flagged
    bomb_surface = bomb_font.render(f"Bombs: {remaining_bombs}", True, COLOR_BLACK)
    screen.blit(bomb_surface, (BOARD_WIDTH - 100, 60))
