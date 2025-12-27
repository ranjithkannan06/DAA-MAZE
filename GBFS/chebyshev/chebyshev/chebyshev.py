# =====================================
# Contributor Name: Lalith
# Topic: GBFS – Chebyshev
# File: GBFS/chebyshev/chebyshev.py
# =====================================

import math
from game_classes import PriorityQueue

def heuristic(self, node, heuristic_type='euclidean'):
    if heuristic_type == 'euclidean':
        return math.sqrt((node.r - self.goal_node.r)**2 + (node.c - self.goal_node.c)**2)
    elif heuristic_type == 'manhattan':
        return abs(node.r - self.goal_node.r) + abs(node.c - self.goal_node.c)
    elif heuristic_type == 'chebyshev':
        return max(abs(node.r - self.goal_node.r), abs(node.c - self.goal_node.c))
    return 0

def compute_path_best_first(self):
    frontier = PriorityQueue()
    frontier.put(self.current_node, 0)
    
    came_from = {}
    came_from[self.current_node] = None
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == self.goal_node:
            break
        
        for neighbor in self.maze.get_neighbors(current):
            if neighbor not in came_from:
                # Greedy: priority = heuristic(n)
                priority = self.heuristic(neighbor)
                frontier.put(neighbor, priority)
                came_from[neighbor] = current
