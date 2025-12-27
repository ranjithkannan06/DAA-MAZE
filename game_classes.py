import collections
import heapq
from graph import Node as GraphNode
from maze import MazeGenerator
from ai import GreedyAI as CoreGreedyAI

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return not self.elements
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

class Node(GraphNode):
    pass

class Maze:
    def __init__(self, width=21, height=21, seed=None):
        import random
        if seed is not None:
            random.seed(seed)
        self.width = width
        self.height = height
        self.gen = MazeGenerator(width, height)
        self.graph = self.gen.generate()
        self.start_node = self.graph.get_node(*self.gen.start_pos)
        self.goal_node = self.graph.get_node(*self.gen.goal_pos)
        self.optimal_path_length = 0
        self.nodes = self.graph.nodes

    def get_neighbors(self, node):
        # node can be a Node object or a position tuple
        pos = node.pos if hasattr(node, 'pos') else node
        g_node = self.graph.get_node(*pos)
        neighbors = []
        if g_node:
            for n_pos in g_node.neighbors:
                neighbors.append(self.graph.get_node(*n_pos))
        return neighbors

    def bfs_analysis(self):
        # Calculate optimal path length using BFS
        start = self.gen.start_pos
        goal = self.gen.goal_pos
        queue = collections.deque([(start, 0)])
        visited = {start}
        
        while queue:
            curr, dist = queue.popleft()
            if curr == goal:
                self.optimal_path_length = dist
                return dist
            
            node = self.graph.get_node(*curr)
            for neighbor in node.neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        return 0

class Metrics:
    def __init__(self, explored=0, visited=0):
        self.nodes_explored = explored
        self.nodes_visited = visited

class GreedyAI(CoreGreedyAI):
    def __init__(self, start_node, goal_node, maze, heuristic_type='default', algorithm_type='default'):
        # Map nodes back to positions for core logic
        super().__init__(maze.graph, start_node.pos, goal_node.pos)
        self.maze = maze
        self.steps = 0
        self.metrics = Metrics()
        # Note: core step() updates self.nodes_explored/visited
        # We need to sync them to the metrics object if main.py expects that.
        
    def step(self):
        super().step()
        self.steps += 1
        self.metrics.nodes_explored = self.nodes_explored
        self.metrics.nodes_visited = self.nodes_visited

    @property
    def current_node(self):
        return self.graph.get_node(*self.current_pos)
