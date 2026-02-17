import math
from config import WEIGHT_NORMAL

class Node:
    def __init__(self, x, y, weight=WEIGHT_NORMAL):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.weight = weight
        self.heuristic = 0
        self.neighbors = {}  # (nx, ny): weight
        self.parent = None
        self.visited = False
        self.is_trap = False
        self.is_powerup = False
        
    @property
    def r(self): return self.y
    @property
    def c(self): return self.x

    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def reset(self):
        self.heuristic = 0
        self.parent = None
        self.visited = False

class Graph:
    def __init__(self):
        self.nodes = {}  # (x, y): Node

    def add_node(self, x, y, weight=WEIGHT_NORMAL):
        if (x, y) not in self.nodes:
            self.nodes[(x, y)] = Node(x, y, weight)
        return self.nodes[(x, y)]

    def add_edge(self, pos1, pos2, weight=None):
        if pos1 in self.nodes and pos2 in self.nodes:
            n1 = self.nodes[pos1]
            n2 = self.nodes[pos2]
            w = weight if weight is not None else n2.weight
            n1.neighbors[pos2] = w

    def get_node(self, x, y):
        return self.nodes.get((x, y))

    def calculate_heuristics(self, goal_pos):
        gx, gy = goal_pos
        for pos, node in self.nodes.items():
            nx, ny = pos
            # Use Chebyshev distance for 8-directional movement
            # D * max(abs(dx), abs(dy))
            node.heuristic = max(abs(nx - gx), abs(ny - gy))

    def reset_nodes(self):
        for node in self.nodes.values():
            node.reset()
