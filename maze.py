import random
from graph import Graph
from config import WEIGHT_NORMAL, WEIGHT_TRAP, WEIGHT_POWERUP

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]  # 1 is wall, 0 is path
        self.graph = Graph()
        self.start_pos = (1, 1)
        self.goal_pos = (width - 2, height - 2)

    def generate(self):
        # Using iterative DFS for maze generation
        stack = [self.start_pos]
        self.grid[self.start_pos[1]][self.start_pos[0]] = 0
        
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                nx, ny = cx + dx, cy + dy
                if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny))
            
            if neighbors:
                nx, ny = random.choice(neighbors)
                self.grid[ny][nx] = 0
                self.grid[cy + (ny - cy) // 2][cx + (nx - cx) // 2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # Build Graph
        self.build_graph()
        self.add_traps_and_powerups()
        self.graph.calculate_heuristics(self.goal_pos)
        return self.graph

    def build_graph(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 0:
                    self.graph.add_node(x, y)

        # Add edges (8-directional)
        for (x, y), node in self.graph.nodes.items():
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self.graph.nodes:
                    # Diagonal weights handled as distance 1 for simplicity in this grid-based chebyshev heuristic
                    # But could be sqrt(2). Using 1 as per requirements for 8-directional graph connectivity.
                    self.graph.add_edge((x, y), (nx, ny))

    def add_traps_and_powerups(self):
        path_nodes = list(self.graph.nodes.keys())
        path_nodes.remove(self.start_pos)
        path_nodes.remove(self.goal_pos)
        
        num_traps = int(len(path_nodes) * 0.1)
        num_powerups = int(len(path_nodes) * 0.05)
        
        trap_positions = random.sample(path_nodes, num_traps)
        for pos in trap_positions:
            node = self.graph.nodes[pos]
            node.weight = WEIGHT_TRAP
            node.is_trap = True
            path_nodes.remove(pos)
            
        powerup_positions = random.sample(path_nodes, num_powerups)
        for pos in powerup_positions:
            node = self.graph.nodes[pos]
            node.weight = WEIGHT_POWERUP
            node.is_powerup = True
