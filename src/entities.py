from typing import Tuple, List, Dict
import random
from pathfinders import manhattan, astar, path_cost 

Position = Tuple[int, int]
Path = List[Position]
Grid = List[List[int]]

# Configuration
ROWS = 17
COLS = 19
CELL = 28
PIXEL_SPEED = 6

def sign(x):
    return 0 if x == 0 else (1 if x > 0 else -1)

class Entity:
    def __init__(self, r: int, c: int, color: str):
        self.r = r
        self.c = c
        self.px = c * CELL
        self.py = r * CELL
        self.color = color
        
    def cell_pos(self) -> Position: return (self.r, self.c)
    def set_cell(self, r: int, c: int):
        self.r = r; self.c = c; self.px = c * CELL; self.py = r * CELL

class Spacecraft(Entity):
    """Represents the Spacecraft (formerly Pacman)."""
    def __init__(self, r: int, c: int):
        super().__init__(r, c, "yellow")
        self.dir = (0, 0)       
        self.next_dir = (0, 0)  
        self.path: Path = []  
        self.path_idx = 0     
        self.moving_to_next = False 
        self.mouth_open = True
        self.mouth_timer = 0
        
    def set_dir(self, dr: int, dc: int):
        self.next_dir = (dr, dc)
        
    def at_center(self) -> bool: return (self.px == self.c * CELL and self.py == self.r * CELL)
    
    def set_path(self, new_path: Path):
        """Sets the path for the spacecraft to follow."""
        self.path = new_path
        self.path_idx = 0
        
    def update(self, grid: Grid):
        target_r, target_c = self.r, self.c
        
        if self.at_center():
            if self.path and self.path_idx + 1 < len(self.path):
                self.path_idx += 1
                target_r, target_c = self.path[self.path_idx]
                
                if 0 <= target_r < ROWS and 0 <= target_c < COLS and grid[target_r][target_c] != 1:
                    dr, dc = target_r - self.r, target_c - self.c
                    self.dir = (dr, dc)
                    self.r, self.c = target_r, target_c
                    self.moving_to_next = True
                else:
                    self.path = []
                    self.moving_to_next = False
            else:
                self.moving_to_next = False
                dr, dc = self.next_dir
                nr, nc = self.r + dr, self.c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != 1:
                    self.r, self.c = nr, nc
                    self.dir = self.next_dir
                    self.moving_to_next = True
                else:
                    self.dir = (0, 0)
                    
        target_px = self.c * CELL
        target_py = self.r * CELL
        dx = target_px - self.px; dy = target_py - self.py
        
        if abs(dx) <= PIXEL_SPEED: self.px = target_px
        else: self.px += PIXEL_SPEED * sign(dx)
        
        if abs(dy) <= PIXEL_SPEED: self.py = target_py
        else: self.py += PIXEL_SPEED * sign(dy)

class Asteroid(Entity):
    """Represents an Asteroid (formerly Ghost)."""
    def __init__(self, r: int, c: int, color: str="red", kind: str="static"):
        super().__init__(r, c, color)
        self.kind = kind
        self.last_move_tick = 0 
        
    def _pixel_move_towards_cell(self):
        step = max(1, PIXEL_SPEED // 3)
        target_px = self.c * CELL
        target_py = self.r * CELL
        dx = target_px - self.px; dy = target_py - self.py
        
        if abs(dx) <= step: self.px = target_px
        else: self.px += step * sign(dx)
        
        if abs(dy) <= step: self.py = target_py
        else: self.py += step * sign(dy)

    def _random_step(self, grid: Grid):
        moves = []
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != 1:
                moves.append((nr, nc))
        if moves:
            nr, nc = random.choice(moves)
            self.r, self.c = nr, nc

    def update(self, grid: Grid, tick_count: int):
        if self.kind == "wanderer":
            interval = 2
            if (tick_count - self.last_move_tick) >= interval and self.at_center():
                self._random_step(grid)
                self.last_move_tick = tick_count
        
        self._pixel_move_towards_cell()

    def at_center(self) -> bool: return (self.px == self.c * CELL and self.py == self.r * CELL)