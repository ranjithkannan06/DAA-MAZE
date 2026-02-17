import math
import sys
import os

# Add parent directory to path to import game_classes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from game_classes import GreedyAI

class EuclideanAI(GreedyAI):
    def __init__(self, start_node, goal_node, maze):
        super().__init__(start_node, goal_node, maze, heuristic_type='euclidean', algorithm_type='best_first')

    def heuristic(self, node):
        return math.sqrt((node.r - self.goal_node.r)**2 + (node.c - self.goal_node.c)**2)
