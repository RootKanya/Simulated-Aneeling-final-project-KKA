import heapq
import random
import math
from typing import List, Tuple, Dict

# Type Aliases for clarity
Position = Tuple[int, int]
Path = List[Position]
Grid = List[List[int]]

# Configuration for Heuristics
ASTEROID_PENALTY = 10  # Cost

# Heuristics and Helpers

def manhattan(a: Position, b: Position) -> int:
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(r: int, c: int, rows: int, cols: int, grid: Grid) -> List[Position]:
    """Returns valid, non-wall neighboring cells."""
    neighbors = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
            neighbors.append((nr, nc))
    return neighbors

def path_cost(path: Path, grid: Grid) -> float:
    """
    Fitness/Cost function for a path.
    Goal: Minimize length and proximity to walls (asteroid areas).
    """
    if not path:
        return float('inf')
    
    cost = 0.0
    cost += len(path) * 1.0  # Base cost

    rows, cols = len(grid), len(grid[0])
    for r, c in path:
        is_near_wall = False
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                is_near_wall = True
                break
        if is_near_wall:
            cost += ASTEROID_PENALTY
            
    return cost

# A* Pathfinding (Baseline)
def astar(start: Position, goal: Position, grid: Grid) -> Path:
    """A* implementation - kept as a reliable baseline."""
    if start == goal: return [start]
    
    rows, cols = len(grid), len(grid[0])
    def h(n): return manhattan(n, goal)
    
    open_heap: List[Tuple[float, Position]] = [(h(start), start)] 
    gscore: Dict[Position, float] = {start: 0.0}
    came_from: Dict[Position, Position] = {}

    while open_heap:
        f, current = heapq.heappop(open_heap)
        
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        r, c = current
        for neighbor in get_neighbors(r, c, rows, cols, grid):
            tentative_g = gscore[current] + path_cost([current, neighbor], grid) 
            
            if tentative_g < gscore.get(neighbor, float('inf')):
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g
                f = tentative_g + h(neighbor)
                heapq.heappush(open_heap, (f, neighbor))
                
    return []

# Genetic Algorithm (GA)

POPULATION_SIZE = 50
MAX_GENERATIONS = 10
MUTATION_RATE = 0.1
MAX_PATH_LENGTH = 150

def generate_random_path(start: Position, goal: Position, grid: Grid) -> Path:
    """Generates a random, valid path up to MAX_PATH_LENGTH."""
    path = [start]
    rows, cols = len(grid), len(grid[0])
    for _ in range(MAX_PATH_LENGTH - 1):
        r, c = path[-1]
        neighbors = get_neighbors(r, c, rows, cols, grid)
        if not neighbors:
            break
        
        best_neighbor = min(neighbors, key=lambda n: manhattan(n, goal))
        
        if random.random() < 0.7:
             next_pos = best_neighbor
        else:
            next_pos = random.choice(neighbors)
            
        path.append(next_pos)
        if next_pos == goal:
            break
            
    return path

def mutate(path: Path, grid: Grid, start: Position, goal: Position) -> Path:
    """Randomly changes a segment of the path."""
    if len(path) < 3: return path
    
    cut1 = random.randint(1, len(path) - 2)
    cut2 = random.randint(cut1, len(path) - 1)
    
    new_path = path[:cut1]
    
    mid_start = path[cut1]
    mid_goal = path[cut2] if cut2 < len(path) else goal
    
    temp_path = astar(mid_start, mid_goal, grid) 
    
    if len(temp_path) > 1:
        new_path.extend(temp_path[1:])
        
    if cut2 < len(path):
        new_path.extend(path[cut2 + 1:])
    
    return new_path

def crossover(parent1: Path, parent2: Path) -> Path:
    """
    Creates a new path by combining parts of two parent paths.
    Finds the first common position and uses the first part of P1 and the second part of P2.
    """
    p2_set = set(parent2)
    crossover_point_idx = -1
    
    for i, pos in enumerate(parent1):
        if pos in p2_set:
            crossover_point_idx = i
            break
            
    if crossover_point_idx == -1:

        return parent1 if path_cost(parent1, None) <= path_cost(parent2, None) else parent2
        
    child = parent1[:crossover_point_idx + 1] 
    

    p2_idx = parent2.index(child[-1])
    child.extend(parent2[p2_idx + 1:])
    
    return child


def genetic_algorithm(start: Position, goal: Position, grid: Grid) -> Path:
    """Genetic Algorithm to find the optimal path."""
    rows, cols = len(grid), len(grid[0])
    
    population: List[Path] = []
    for _ in range(POPULATION_SIZE):
        population.append(generate_random_path(start, goal, grid))

    for generation in range(MAX_GENERATIONS):

        scored_population = [(path_cost(p, grid) + manhattan(p[-1], goal) * 50, p) for p in population]
        scored_population.sort(key=lambda x: x[0])
        
        best_cost, best_path = scored_population[0]
        if best_path and best_path[-1] == goal and best_cost < 1000:
            return best_path 
            
        new_population: List[Path] = [p for _, p in scored_population[:POPULATION_SIZE // 10]]

        while len(new_population) < POPULATION_SIZE:
            candidates = random.choices(scored_population, k=4)
            parent1 = min(candidates[:2], key=lambda x: x[0])[1]
            parent2 = min(candidates[2:], key=lambda x: x[0])[1]

            child = crossover(parent1, parent2)

            if random.random() < MUTATION_RATE:
                child = mutate(child, grid, start, goal)
            
            validated_path: Path = [child[0]]
            for i in range(1, len(child)):
                current = validated_path[-1]
                next_node = child[i]
                
                if manhattan(current, next_node) == 1 and grid[next_node[0]][next_node[1]] != 1:
                    validated_path.append(next_node)
                else:

                    bridge = astar(current, next_node, grid)
                    if len(bridge) > 1:
                        validated_path.extend(bridge[1:])
                    else:

                        break
                        
            new_population.append(validated_path)
            
        population = new_population

    return scored_population[0][1] if scored_population[0][1] and scored_population[0][1][-1] == goal else []

# Simulated Annealing (SA)

INITIAL_TEMPERATURE = 1000.0
COOLING_RATE = 0.99
MAX_ITERATIONS = 500

def generate_neighbor_path(path: Path, grid: Grid, start: Position, goal: Position) -> Path:
    """Generates a neighboring solution by mutating the current path."""
    if len(path) < 2: return generate_random_path(start, goal, grid)
    
    rows, cols = len(grid), len(grid[0])

    idx = random.randint(1, len(path) - 2)
    r, c = path[idx]

    new_r, new_c = r, c

    for _ in range(3):
        dr, dc = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        pr, pc = r + dr, c + dc
        if 0 <= pr < rows and 0 <= pc < cols and grid[pr][pc] != 1:
            new_r, new_c = pr, pc
            break
            
    if (new_r, new_c) == (r, c):
        return path 

    new_path = path[:idx] 
    
    bridge_to_new = astar(new_path[-1], (new_r, new_c), grid)
    if len(bridge_to_new) > 1:
        new_path.extend(bridge_to_new[1:])
    else:
        return path

    if idx + 1 < len(path):
        next_node = path[idx + 1]
        bridge_to_next = astar(new_path[-1], next_node, grid)
        if len(bridge_to_next) > 1:
            new_path.extend(bridge_to_next[1:])
        else:
            bridge_to_goal = astar(new_path[-1], goal, grid)
            if len(bridge_to_goal) > 1:
                new_path.extend(bridge_to_goal[1:])
            else:
                return path 
    else:
        bridge_to_goal = astar(new_path[-1], goal, grid)
        if len(bridge_to_goal) > 1:
            new_path.extend(bridge_to_goal[1:])
            
    return new_path

def simulated_annealing(start: Position, goal: Position, grid: Grid) -> Path:
    """Simulated Annealing to find the optimal path."""
    
    current_solution: Path = astar(start, goal, grid) 
    if not current_solution: 
        current_solution = generate_random_path(start, goal, grid)
        if not current_solution: return []
        
    best_solution: Path = current_solution
    T = INITIAL_TEMPERATURE
    
    for iteration in range(MAX_ITERATIONS):

        if T < 1.0: break 
        
        new_solution = generate_neighbor_path(current_solution, grid, start, goal)
        
        current_cost = path_cost(current_solution, grid)
        new_cost = path_cost(new_solution, grid)
        
        delta_E = new_cost - current_cost
        
        if delta_E < 0:
            current_solution = new_solution
        else:
            try:
                prob = math.exp(-delta_E / T)
            except OverflowError:
                prob = 0.0
                
            if random.random() < prob:
                current_solution = new_solution
        
        if path_cost(current_solution, grid) < path_cost(best_solution, grid):
            best_solution = current_solution
          
        T *= COOLING_RATE
        
    return best_solution if best_solution[-1] == goal else []

PATHFINDERS = {
    "A*": astar,
    "GA": genetic_algorithm,
    "SA": simulated_annealing
}