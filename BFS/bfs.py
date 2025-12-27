import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from game_classes import GreedyAI

class BFSAI(GreedyAI):
    def __init__(self, start_node, goal_node, maze):
        super().__init__(start_node, goal_node, maze, heuristic_type='euclidean', algorithm_type='bfs')

    def compute_path(self):
        # BFS Implementation
        queue = deque([self.current_node])
        visited = {self.current_node}
        came_from = {self.current_node: None}
        
        self.visited_nodes.add(self.current_node)
        
        current = None
        while queue:
            current = queue.popleft()
            self.visited_nodes.add(current)
            self.metrics.record_visit(current)
            
            if current == self.goal_node:
                break
            
            for neighbor in self.maze.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
                    self.metrics.record_evaluation(neighbor, 0)
        
        if current == self.goal_node:
            self.reconstruct_path(came_from, current)
        else:
            print("BFS failed to find path")
            self.finished = True

    def reconstruct_path(self, came_from, current):
        path = []
        while current != self.current_node:
            path.append(current)
            current = came_from[current]
        path.reverse()
        self.full_path = path
        self.calculate_path_stats()
