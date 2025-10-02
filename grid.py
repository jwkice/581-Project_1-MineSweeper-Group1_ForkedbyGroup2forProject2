"""
Grid generation and manipulation for Minesweeper
"""
import random
from constants import DIRECTIONS


def generate_bombs(rows, cols, bomb_count):
    """
    Returns a set of (row, col) positions for bombs.
    Clamps bomb_count to the number of cells.
    """
    total = rows * cols
    bomb_count = max(0, min(bomb_count, total))
    choices = random.sample(range(total), bomb_count)
    return {(i // cols, i % cols) for i in choices}


def generate_numbers(grid):
    """
    Fill in the grid with numbers based on how many bombs it's near
    """
    rows = len(grid)
    cols = len(grid[0])
    
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != -1:
                bomb_count = 0
                for di, dj in DIRECTIONS:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if grid[ni][nj] == -1:
                            bomb_count += 1
                grid[i][j] = bomb_count


def ensure_safe_start(grid, start_row, start_col, bomb_positions):
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
        
        generate_numbers(grid)
        return grid, new_bomb_positions
    
    return grid, bomb_positions


def flood_fill(grid, start_row, start_col):
    """
    Floodfill algorithm that reveals cells with 0 bombs around them,
    and stops at cells with numbers.
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
            for dr, dc in DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < rows and 0 <= new_col < cols and
                    (new_row, new_col) not in to_reveal):
                    to_visit.append((new_row, new_col))
    
    return to_reveal
