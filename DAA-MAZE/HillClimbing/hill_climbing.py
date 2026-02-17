import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from game_classes import GreedyAI

class HillClimbingAI(GreedyAI):
    def __init__(self, start_node, goal_node, maze):
        super().__init__(start_node, goal_node, maze, heuristic_type='euclidean', algorithm_type='hill_climbing')

    def heuristic(self, node):
        # Hill Climbing typically uses Euclidean or Manhattan, let's use Euclidean as default
        return math.sqrt((node.r - self.goal_node.r)**2 + (node.c - self.goal_node.c)**2)
    
    def compute_path(self):
        # Force hill climbing logic
        self.compute_path_hill_climbing()
