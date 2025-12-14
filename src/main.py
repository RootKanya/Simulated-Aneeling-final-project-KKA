import tkinter as tk
import sys
from pathlib import Path
from typing import List, Tuple
import time

from entities import Spacecraft, Asteroid, manhattan, CELL, ROWS, COLS, PIXEL_SPEED
from pathfinders import PATHFINDERS, Path, Grid, Position, path_cost

# Configuration 
TICK_MS = 28
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

TARGET_POS = (1, COLS - 2)

# Algorithm Selection
DEFAULT_ALGO = "A*"
ALGO_RECALC_INTERVAL = 100

MAP_LAYOUT = [
    "1111111111111111111",
    "1.G.........11...E1", 
    "1.111.11111.11.11.1",
    "1.....1.....1.....1",
    "1.11.111.111.1111.1",
    "1..................1",
    "1.111.111 111.1111.1",
    "1    1.1     1.1   1",
    "11111.1 11111 1.1111",
    "1.......1...1......1",
    "1.11111.11111.11111.1",
    "1..................1",
    "1.111.11111.111.111.1",
    "1...1.....P.....1...1",
    "1111.1.11111.1...1111",
    "1.....1...G.........1",
    "1111111111111111111",
]

# Helpers
def clamp_map(layout: List[str]) -> Tuple[Grid, Position, Position, List[Position]]:
    """Converts layout to grid and finds entity start positions."""
    grid: Grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    start_pos: Position = (0, 0)
    target_pos: Position = TARGET_POS
    asteroid_positions: List[Position] = []

    for r in range(min(ROWS, len(layout))):
        row = layout[r]
        for c in range(min(COLS, len(row))):
            ch = row[c]
            if ch == "1":
                grid[r][c] = 1
            elif ch == "P": 
                grid[r][c] = 2 
                start_pos = (r, c)
            elif ch == "E": 
                grid[r][c] = 0
                target_pos = (r, c)
            elif ch in ("G", "g"): 
                 grid[r][c] = 0
                 asteroid_positions.append((r, c))
            elif ch == ".": 
                grid[r][c] = 2
            elif ch == " ": 
                grid[r][c] = 0
            else:
                grid[r][c] = 0
                
    for c in range(COLS): grid[0][c] = 1; grid[ROWS - 1][c] = 1
    for r in range(ROWS): grid[r][0] = 1; grid[r][COLS - 1] = 1
    
    return grid, start_pos, target_pos, asteroid_positions

class Game:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Space Navigator (SA/GA Edition)")
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#050510")
        self.canvas.pack(side="left")

        # Control Panel
        control_frame = tk.Frame(root, width=150, height=HEIGHT)
        control_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        tk.Label(control_frame, text="Pathfinding Algo:").pack(pady=(0, 5))
        self.algo_var = tk.StringVar(value=DEFAULT_ALGO)
        for name in PATHFINDERS.keys():
            rb = tk.Radiobutton(control_frame, text=name, variable=self.algo_var, value=name, command=self.reset_path_and_stats)
            rb.pack(anchor="w")
        
        tk.Button(control_frame, text="Recalculate Path", command=self.recalculate_path).pack(pady=(15, 5))
        
        self.stats_lbl = tk.Label(control_frame, justify=tk.LEFT, text="")
        self.stats_lbl.pack(pady=(15, 5), anchor="w")
        
        tk.Button(control_frame, text="Restart", command=self.restart).pack(pady=(100, 5))
        
        self.grid: Grid = []
        self.start_pos: Position = (0, 0)
        self.target_pos: Position = TARGET_POS
        self.asteroid_positions: List[Position] = []
        self.pac: Spacecraft = Spacecraft(0, 0)
        self.ghosts: List[Asteroid] = []
        
        self.score = 0
        self.running = True
        self.paused = False
        self.tick_count = 0
        self.path_stats = {'calls': 0, 'last_ms': 0.0, 'sum_ms': 0.0, 'length': 0, 'cost': 0.0}

        self.setup_game()
        self.loop()

    def setup_game(self):
        self.grid, self.start_pos, self.target_pos, self.asteroid_positions = clamp_map(MAP_LAYOUT)
        
        self.pac = Spacecraft(*self.start_pos)
        self.pac.color = "#00FFFF" 
        
        self.ghosts = [Asteroid(r, c, color="#888888", kind="static") for r, c in self.asteroid_positions]
        
        
        if len(self.ghosts) >= 1:
            self.ghosts[0].color = "#AA5555" 
            self.ghosts[0].kind = "wanderer"
            
        self.pac.px = self.pac.c * CELL; self.pac.py = self.pac.r * CELL
        for g in self.ghosts: g.px = g.c * CELL; g.py = g.r * CELL
        
        self.recalculate_path()

    def reset_path_and_stats(self):
        self.pac.path = []
        self.pac.path_idx = 0
        self.path_stats = {'calls': 0, 'last_ms': 0.0, 'sum_ms': 0.0, 'length': 0, 'cost': 0.0}
        self.recalculate_path()
        
    def recalculate_path(self):
        start_time = time.perf_counter()
        algo_name = self.algo_var.get()
        pathfinder_func = PATHFINDERS.get(algo_name, PATHFINDERS["A*"])
        
        new_path: Path = pathfinder_func(self.pac.cell_pos(), self.target_pos, self.grid)
        
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        self.pac.set_path(new_path)
        
        self.path_stats['calls'] += 1
        self.path_stats['last_ms'] = elapsed_time
        self.path_stats['sum_ms'] += elapsed_time
        self.path_stats['length'] = len(new_path)
        self.path_stats['cost'] = path_cost(new_path, self.grid) if new_path else float('inf')

    def toggle_pause(self):
        self.paused = not self.paused

    def quit_clean(self):
        try: self.root.destroy()
        except Exception: pass
        sys.exit(0)

    def on_keypress(self, event):
        k = event.keysym
        if k == "Left": self.pac.set_dir(0, -1)
        elif k == "Right": self.pac.set_dir(0, 1)
        elif k == "Up": self.pac.set_dir(-1, 0)
        elif k == "Down": self.pac.set_dir(1, 0)
        elif k in ("p","P"): self.toggle_pause()
        elif k == "Escape": self.quit_clean()
        elif k in ("r","R"): self.restart()

    def loop(self):
        if not self.running: return
        if not self.paused: self.tick()
        self.draw()
        self.root.after(TICK_MS, self.loop)

    def tick(self):
        self.tick_count += 1
        
        if self.tick_count % ALGO_RECALC_INTERVAL == 0 and self.algo_var.get() in ["GA", "SA"]:
             self.recalculate_path()
        
        self.pac.update(self.grid)
        
        if self.pac.at_center() and self.grid[self.pac.r][self.pac.c] == 2:
            self.grid[self.pac.r][self.pac.c] = 0
            self.score += 10
            
        for g in self.ghosts:
            g.update(self.grid, self.tick_count)
            
        for g in self.ghosts:
            dx = g.px - self.pac.px; dy = g.py - self.pac.py
            if dx*dx + dy*dy <= (CELL*0.8)**2:
                self.game_over(False)
                return
                
        if self.pac.cell_pos() == self.target_pos:
            self.game_over(True)
            return

    def draw(self):
        self.canvas.delete("all")
        
        for r in range(ROWS):
            for c in range(COLS):
                x0 = c * CELL; y0 = r * CELL
                val = self.grid[r][c]
                
                if (r, c) == self.target_pos:
                    self.canvas.create_rectangle(x0, y0, x0+CELL, y0+CELL, fill="#004400", outline="") 
                    self.canvas.create_text(x0+CELL//2, y0+CELL//2, text="EXIT", fill="#00FF00", font=("Arial", 8, "bold"))
                elif val == 1:
                    self.canvas.create_rectangle(x0, y0, x0+CELL, y0+CELL, fill="#111122", outline="#222244")
                elif val == 2:
                    self.canvas.create_oval(x0 + CELL*0.45, y0 + CELL*0.45, x0 + CELL*0.55, y0 + CELL*0.55, fill="white", outline="")
        
        if self.pac.path:
            for i, (r, c) in enumerate(self.pac.path):
                x = c * CELL + CELL // 2
                y = r * CELL + CELL // 2
                color = "#FFFF00" if i >= self.pac.path_idx else "#333300"
                if i >= self.pac.path_idx:
                    self.canvas.create_oval(x-1, y-1, x+1, y+1, fill=color, outline="")
                
        for g in self.ghosts:
            self.draw_asteroid(g)
            
        self.draw_spacecraft()

        self.draw_hud()

    def draw_hud(self):
        avg_ms = (self.path_stats['sum_ms'] / self.path_stats['calls']) if self.path_stats['calls'] else 0.0
        hud_text = (
            f"Score: {self.score}\n"
            f"Algorithm: {self.algo_var.get()}\n"
            f"Path Len: {self.path_stats['length']}\n"
            f"Path Cost: {self.path_stats['cost']:.2f}\n"
            f"AI Calls: {self.path_stats['calls']}\n"
            f"Last Calc: {self.path_stats['last_ms']:.2f} ms\n"
            f"Avg Calc: {avg_ms:.2f} ms"
        )
        self.stats_lbl.config(text=hud_text)

    def draw_spacecraft(self):
        """Draws a triangular spacecraft pointing in the movement direction."""
        cx = self.pac.px + CELL//2
        cy = self.pac.py + CELL//2
        size = CELL // 2 - 2
        
        dr, dc = self.pac.dir
        if (dr, dc) == (0, 0):
            dr, dc = 0, 1

        
        angle = 0
        if (dr, dc) == (0, -1): angle = 180  # Left
        elif (dr, dc) == (0, 1): angle = 0   # Right
        elif (dr, dc) == (-1, 0): angle = 90 # Up
        elif (dr, dc) == (1, 0): angle = 270 # Down

        import math
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        def rotate(x, y):
            return 0, 0 

        pts = []
        flame_pts = []
        
        s = size
        w = size * 0.7 # width
        
        if (dr, dc) == (0, 1): # Right
            pts = [cx+s, cy, cx-s, cy-w, cx-s, cy+w]
            flame_pts = [cx-s, cy-w/2, cx-s-6, cy, cx-s, cy+w/2]
        elif (dr, dc) == (0, -1): # Left
            pts = [cx-s, cy, cx+s, cy-w, cx+s, cy+w]
            flame_pts = [cx+s, cy-w/2, cx+s+6, cy, cx+s, cy+w/2]
        elif (dr, dc) == (1, 0): # Down
            pts = [cx, cy+s, cx-w, cy-s, cx+w, cy-s]
            flame_pts = [cx-w/2, cy-s, cx, cy-s-6, cx+w/2, cy-s]
        elif (dr, dc) == (-1, 0): # Up
            pts = [cx, cy-s, cx-w, cy+s, cx+w, cy+s]
            flame_pts = [cx-w/2, cy+s, cx, cy+s+6, cx+w/2, cy+s]
            
        if self.pac.mouth_open:
             self.canvas.create_polygon(flame_pts, fill="orange", outline="")

        # Draw Ship Body
        self.canvas.create_polygon(pts, fill=self.pac.color, outline="white", width=1)
        
        # Draw Cockpit (Center dot)
        self.canvas.create_oval(cx-2, cy-2, cx+2, cy+2, fill="black")

    def draw_asteroid(self, g: Asteroid):
        """Draws an asteroid as two separate jagged rock pieces."""
        x = g.px
        y = g.py
        
        p1_x = x + 4
        p1_y = y + 4
        rock1_pts = [
            p1_x+2, p1_y, 
            p1_x+10, p1_y+2, 
            p1_x+8, p1_y+10, 
            p1_x, p1_y+8
        ]
        self.canvas.create_polygon(rock1_pts, fill=g.color, outline="#333333", width=1)
        
        p2_x = x + 14
        p2_y = y + 14
        rock2_pts = [
            p2_x+2, p2_y, 
            p2_x+10, p2_y-2, 
            p2_x+12, p2_y+8, 
            p2_x+4, p2_y+10
        ]
        self.canvas.create_polygon(rock2_pts, fill=g.color, outline="#333333", width=1)

    def game_over(self, won: bool):
        self.running = False
        msg = "TARGET REACHED! (Optimal Path Found)" if won else "CRASHED! (Asteroid Collision)"
        popup = tk.Toplevel(self.root)
        popup.title("Mission Complete/Failed")
        w, h = 400, 200
        sx, sy = self.root.winfo_x(), self.root.winfo_y()
        popup.geometry(f"{w}x{h}+{sx + WIDTH//2 - w//2}+{sy + HEIGHT//2 - h//2}")
        lbl = tk.Label(popup, text=msg, font=("Arial", 16, "bold"))
        lbl.pack(pady=(18,8))
        score_lbl = tk.Label(popup, text=f"Final Score: {self.score}", font=("Arial", 12))
        score_lbl.pack(pady=(0,12))
        btn_frame = tk.Frame(popup); btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Restart", width=12, command=lambda: self._restart_from_popup(popup)).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Close", width=12, command=self.quit_clean).grid(row=0, column=1, padx=8)
        popup.transient(self.root); popup.grab_set(); self.root.wait_window(popup)

    def _restart_from_popup(self, popup):
        popup.destroy(); self.restart()

    def restart(self):
        self.score = 0; self.running = True; self.paused = False; self.tick_count = 0
        self.path_stats = {'calls': 0, 'last_ms': 0.0, 'sum_ms': 0.0, 'length': 0, 'cost': 0.0}
        self.setup_game()
        self.loop()

# Main
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    game = Game(root)
    root.bind("<KeyPress>", game.on_keypress)
    root.mainloop()