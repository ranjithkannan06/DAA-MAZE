import heapq
import math
import importlib.util
import os
from config import WEIGHT_NORMAL

class GreedyAI:
    def __init__(self, graph, start_pos, goal_pos, heuristic_type='chebyshev', use_backtracking=True):
        self.graph = graph
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.current_pos = start_pos
        self.heuristic_type = heuristic_type
        self.use_backtracking = use_backtracking
        
        self.path = [start_pos]
        self.visited = {start_pos}
        self.backtrack_count = 0
        self.nodes_explored = 1
        self.nodes_visited = 1
        self.finished = False
        self.failed = False
        self.total_cost = 0
        self.history = [start_pos]
        self.decision_annotations = []

    def get_heuristic(self, pos):
        curr_node = self.graph.get_node(*pos)
        gx, gy = self.goal_pos
        nx, ny = pos
        if self.heuristic_type == 'chebyshev':
            return max(abs(nx - gx), abs(ny - gy))
        elif self.heuristic_type == 'manhattan':
            return abs(nx - gx) + abs(ny - gy)
        elif self.heuristic_type == 'euclidean':
            return math.sqrt((nx - gx)**2 + (ny - gy)**2)
        return 0

    def step(self):
        if self.finished or self.failed:
            return
        current_node = self.graph.get_node(*self.current_pos)
        neighbors = []
        for n_pos, weight in current_node.neighbors.items():
            if n_pos not in self.visited:
                h = self.get_heuristic(n_pos)
                neighbors.append((h, weight, n_pos))
        
        self.decision_annotations = [(h, p) for h, w, p in neighbors]
        if neighbors:
            neighbors.sort()
            h, w, next_pos = neighbors[0]
            self.current_pos = next_pos
            self.path.append(next_pos)
            self.history.append(next_pos)
            self.visited.add(next_pos)
            self.nodes_explored += 1
            self.nodes_visited += 1
            self.total_cost += w
            if self.current_pos == self.goal_pos:
                self.finished = True
        else:
            if self.use_backtracking and len(self.path) > 1:
                self.path.pop()
                self.backtrack_count += 1
                self.current_pos = self.path[-1]
                self.history.append(self.current_pos)
            else:
                self.failed = True
                self.finished = True

    def get_metrics(self):
        return {
            "Algorithm": f"{'GBFS' if self.use_backtracking else 'HillClimb'} ({self.heuristic_type.capitalize()})",
            "Explored": self.nodes_explored,
            "Visited": self.nodes_visited,
            "Cost": int(self.total_cost),
            "Status": "Online" if not self.finished else ("Success" if not self.failed else "Failed")
        }

class ProjectAI:
    """Adapter to use the specific files from the project folders (GBFS, hill_climbing.py)"""
    def __init__(self, maze, start_node, goal_node, algo_type='chebyshev', is_hill_climbing=False):
        self.maze = maze # Assumes a maze object with get_neighbors
        self.current_node = start_node
        self.goal_node = goal_node
        self.heuristic_type = algo_type
        self.is_hill_climbing = is_hill_climbing
        
        self.path = []
        self.history = [start_node.pos]
        self.current_pos = start_node.pos
        self.step_idx = 0
        self.total_cost = 0
        self.finished = False
        self.failed = False
        self.nodes_explored = 0
        self.nodes_visited = 0
        self.decision_annotations = []
        
        # Injected methods will be set here
        self.heuristic_func = None
        self.search_func = None
        
        self._load_logic()
        self._calculate_full_path()

    def _load_logic(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if self.is_hill_climbing:
            path = os.path.join(base_dir, "hill_climbing.py")
            spec = importlib.util.spec_from_file_location("hill_logic", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.search_func = mod.compute_path_hill_climbing
            # Hill climbing snippet uses self.heuristic
            self.heuristic_func = lambda node: GreedyAI.get_heuristic(self, node.pos)
        else:
            # Map type to file
            f_map = {
                'chebyshev': os.path.join(base_dir, "GBFS", "chebyshev", "chebyshev", "chebyshev.py"),
                'manhattan': os.path.join(base_dir, "GBFS", "chebyshev", "Manhattan", "manhattan.py"),
                'euclidean': os.path.join(base_dir, "GBFS", "chebyshev", "euclidian", "euclidian.py")
            }
            path = f_map.get(self.heuristic_type)
            if path and os.path.exists(path):
                spec = importlib.util.spec_from_file_location("gbfs_logic", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.heuristic_func = mod.heuristic
                self.search_func = mod.compute_path_best_first

    def heuristic(self, node):
        return self.heuristic_func(self, node, self.heuristic_type)

    def _calculate_full_path(self):
        if not self.search_func:
            return
        
        from game_classes import PriorityQueue
        
        if self.is_hill_climbing:
            # Re-implement hill_climbing.py logic with path capture
            current = self.current_node
            self.path = [current.pos]
            visited = {current}
            while current != self.goal_node:
                neighbors = self.maze.get_neighbors(current)
                best_neighbor = None
                best_h = float('inf')
                for neighbor in neighbors:
                    if neighbor not in visited:
                        h = self.heuristic(neighbor)
                        if h < best_h:
                            best_h = h
                            best_neighbor = neighbor
                if best_neighbor:
                    current = best_neighbor
                    self.path.append(current.pos)
                    visited.add(current)
                else:
                    self.failed = True
                    break
        else:
            # GBFS Logic from project files
            frontier = PriorityQueue()
            frontier.put(self.current_node, 0)
            came_from = {self.current_node: None}
            found = False
            while not frontier.empty():
                current = frontier.get()
                self.nodes_explored += 1
                if current == self.goal_node:
                    found = True
                    break
                for neighbor in self.maze.get_neighbors(current):
                    if neighbor not in came_from:
                        priority = self.heuristic(neighbor)
                        frontier.put(neighbor, priority)
                        came_from[neighbor] = current
            if found:
                curr = self.goal_node
                tmp_path = []
                while curr:
                    tmp_path.append(curr.pos)
                    curr = came_from[curr]
                tmp_path.reverse()
                self.path = tmp_path
            else:
                self.failed = True
        
        if self.path:
            self.nodes_visited = len(self.path)

    def step(self):
        if self.finished or self.failed:
            return
        if self.step_idx < len(self.path) - 1:
            self.step_idx += 1
            next_pos = self.path[self.step_idx]
            node = self.maze.graph.get_node(*next_pos)
            self.total_cost += node.weight
            self.current_pos = next_pos
            self.history.append(next_pos)
            if self.current_pos == self.goal_node.pos:
                self.finished = True
        else:
            self.finished = True

    def get_metrics(self):
        return {
            "Algorithm": f"DIR.{self.heuristic_type.upper() if not self.is_hill_climbing else 'HILL_CLIMB'}",
            "Search": "Global (GBFS Folder)" if not self.is_hill_climbing else "Local (HillClimb.py)",
            "Path Length": len(self.path) - 1,
            "Total Cost": int(self.total_cost),
            "Status": "Success" if self.finished and not self.failed else ("Failed" if self.failed else "Running")
        }
