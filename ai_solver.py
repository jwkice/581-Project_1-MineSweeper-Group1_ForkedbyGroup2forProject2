'''
Module Name: ai_solver.py
Purpose: AI solver logic for Minesweeper
Input(s): None
Output(s): None
Original Author(s): Team 1
Maintainer(s):  Jamie King
                Jacob Kice
                Gunther Luechtefeld
                Joseph Hotze
                Srihari Meyoor
Outside Source(s):  None
Updated Date: 10/05/2025
'''

import random


def hidden_neighbors(row, col, revealed, flagged, board_rows, board_cols):
    """Returns the number of neighboring cells that are not revealed or flagged"""
    hidden = 0
    for i in range(-1, 2):
        if row + i >= 0 and row + i < board_rows:
            for j in range(-1, 2):
                if (col + j >= 0 and col + j < board_cols) and (i != 0 or j != 0):
                    if ((row + i, col + j) not in revealed) and ((row + i, col + j) not in flagged):
                        hidden += 1
    return hidden


def flagged_neighbors(row, col, flagged, board_rows, board_cols):
    """Returns the number of neighboring cells that are flagged"""
    num_flagged = 0
    for i in range(-1, 2):
        if row + i >= 0 and row + i < board_rows:
            for j in range(-1, 2):
                if (col + j >= 0 and col + j < board_cols) and (i != 0 or j != 0):
                    if (row + i, col + j) in flagged:
                        num_flagged += 1
    return num_flagged


def is_hidden(row, col, revealed, flagged):
    """Returns True if the cell is not in revealed or flagged"""
    return ((row, col) not in revealed) and ((row, col) not in flagged)


def try_basic_moves(grid, board_rows, board_cols, revealed, flagged, ai_level):
    """
    Attempts basic AI moves (medium and hard difficulty).
    Returns (found, move_type, row, col) where move_type is 'reveal' or 'flag'
    """
    if ai_level not in ['medium', 'hard']:
        return False, None, None, None
    
    for row in range(board_rows):
        for col in range(board_cols):
            if (row, col) in revealed and hidden_neighbors(row, col, revealed, flagged, board_rows, board_cols) != 0:
                # Check if all remaining hidden neighbors should be revealed
                if grid[row][col] == flagged_neighbors(row, col, flagged, board_rows, board_cols):
                    for i in range(-1, 2):
                        if row + i >= 0 and row + i < board_rows:
                            for j in range(-1, 2):
                                if (col + j >= 0 and col + j < board_cols) and (i != 0 or j != 0):
                                    if is_hidden(row + i, col + j, revealed, flagged):
                                        return True, 'reveal', row + i, col + j
                
                # Check if all remaining hidden neighbors should be flagged
                elif grid[row][col] == (hidden_neighbors(row, col, revealed, flagged, board_rows, board_cols) + 
                                       flagged_neighbors(row, col, flagged, board_rows, board_cols)):
                    for i in range(-1, 2):
                        if row + i >= 0 and row + i < board_rows:
                            for j in range(-1, 2):
                                if (col + j >= 0 and col + j < board_cols) and (i != 0 or j != 0):
                                    if is_hidden(row + i, col + j, revealed, flagged):
                                        return True, 'flag', row + i, col + j
    
    return False, None, None, None


def try_121_pattern(grid, board_rows, board_cols, revealed, flagged):
    """
    Attempts the 1-2-1 pattern move (hard difficulty only).
    Returns (found, move_type, row, col)
    """
    for row in range(board_rows):
        for col in range(board_cols):
            if grid[row][col] == 2 and (row, col) in revealed:
                if row - 1 >= 0 and row + 1 < board_rows and col - 1 >= 0 and col + 1 < board_cols:
                    # Check for 1-2-1 pattern
                    has_row_pattern = (grid[row - 1][col] == 1 and grid[row + 1][col] == 1 and 
                                      (row - 1, col) in revealed and (row + 1, col) in revealed)
                    has_col_pattern = (grid[row][col - 1] == 1 and grid[row][col + 1] == 1 and
                                      (row, col - 1) in revealed and (row, col + 1) in revealed)
                    
                    if has_row_pattern or has_col_pattern:
                        corners_hidden = (is_hidden(row - 1, col - 1, revealed, flagged) and
                                        is_hidden(row + 1, col - 1, revealed, flagged) and
                                        is_hidden(row - 1, col + 1, revealed, flagged) and
                                        is_hidden(row + 1, col + 1, revealed, flagged))
                        
                        if corners_hidden:
                            # Reveal safe cells
                            if has_row_pattern:
                                if is_hidden(row, col - 1, revealed, flagged):
                                    return True, 'reveal', row, col - 1
                                elif is_hidden(row, col + 1, revealed, flagged):
                                    return True, 'reveal', row, col + 1
                            elif has_col_pattern:
                                if is_hidden(row - 1, col, revealed, flagged):
                                    return True, 'reveal', row - 1, col
                                elif is_hidden(row + 1, col, revealed, flagged):
                                    return True, 'reveal', row + 1, col
                        
                        # Check for corner patterns (flag opposite corners)
                        corner_checks = [
                            ((row - 1, col - 1), [(has_row_pattern, row - 1, col + 1), (has_col_pattern, row + 1, col - 1)]),
                            ((row + 1, col - 1), [(has_row_pattern, row + 1, col + 1), (has_col_pattern, row - 1, col - 1)]),
                            ((row - 1, col + 1), [(has_row_pattern, row - 1, col - 1), (has_col_pattern, row + 1, col + 1)]),
                            ((row + 1, col + 1), [(has_row_pattern, row + 1, col - 1), (has_col_pattern, row - 1, col + 1)])
                        ]
                        
                        for corner, flags in corner_checks:
                            if corner in revealed:
                                for pattern, flag_row, flag_col in flags:
                                    if pattern and is_hidden(flag_row, flag_col, revealed, flagged):
                                        return True, 'flag', flag_row, flag_col
    
    return False, None, None, None


def make_random_move(board_rows, board_cols, revealed, flagged):
    """Makes a random move on an unrevealed, unflagged cell"""
    rand_rows = list(range(board_rows))
    random.shuffle(rand_rows)
    rand_cols = list(range(board_cols))
    random.shuffle(rand_cols)
    
    for row in rand_rows:
        for col in rand_cols:
            if (row, col) not in flagged and (row, col) not in revealed:
                return True, row, col
    
    return False, None, None
