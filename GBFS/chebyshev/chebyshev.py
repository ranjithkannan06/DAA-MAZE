import math
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from game_classes import GreedyAI

class ChebyshevAI(GreedyAI):
    def __init__(self, start_node, goal_node, maze):
        super().__init__(start_node, goal_node, maze, heuristic_type='chebyshev', algorithm_type='best_first')

    def heuristic(self, node):
        return max(abs(node.r - self.goal_node.r), abs(node.c - self.goal_node.c))
