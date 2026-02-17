import random
import heapq
import math
from collections import deque, defaultdict
from region_logic import RegionLogic

# ... (rest of imports)

# ... (skip to DynamicMaze class definition if possible, or just add methods)
# Since I can't skip easily without context, I will target the imports first, then use a separate call for DynamicMaze if needed.
# Actually I'll just do the import at top and then I'll use a second tool call for the class update to be safe.


class PriorityQueue:
    def __init__(self):
        self.elements = []
        self.count = 0 
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        # Use count as tie-breaker to avoid comparing items directly if priorities match
        heapq.heappush(self.elements, (priority, self.count, item))
        self.count += 1
    
    def get(self):
        return heapq.heappop(self.elements)[2]

# game_classes.py

class Node:
    """Graph node with enhanced tracking for algorithm analysis"""
    def __init__(self, r, c, node_type='.', cost=1):
        self.r = r
        self.c = c
        self.type = node_type  # '.', '#', 'T', 'P', 'S', 'G'
        self.cost = cost
        self.visited_by_player = False
        self.visited_by_ai = False
        
        # Enhanced tracking for graph visualization
        self.explored_by_ai = False  # Considered but not visited
        self.times_evaluated = 0  # How many times AI evaluated this node
        self.heuristic_value = None  # Last calculated heuristic
        
    def __repr__(self):
        return f"Node({self.r}, {self.c}, {self.type})"
    
    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return self.r == other.r and self.c == other.c
    
    def __hash__(self):
        return hash((self.r, self.c))

    def __lt__(self, other):
        return self.cost < other.cost


class PerformanceMetrics:
    """Track algorithm performance for educational analysis"""
    def __init__(self):
        self.nodes_explored = 0  # Nodes added to consideration
        self.nodes_visited = 0  # Nodes actually moved to
        self.backtrack_count = 0
        self.dead_ends_hit = 0
        self.traps_triggered = 0
        self.powerups_collected = 0
        self.evaluation_history = []  # List of (node, heuristic_value)
        
    def record_evaluation(self, node, heuristic_val):
        """Record when AI evaluates a node"""
        self.nodes_explored += 1
        node.explored_by_ai = True
        node.times_evaluated += 1
        node.heuristic_value = heuristic_val
        self.evaluation_history.append((node, heuristic_val))
    
    def record_visit(self, node):
        """Record actual movement to node"""
        self.nodes_visited += 1
        node.visited_by_ai = True
    
    def record_backtrack(self):
        self.backtrack_count += 1
    
    def record_dead_end(self):
        self.dead_ends_hit += 1
    
    def get_efficiency_ratio(self, optimal_path_length):
        """Calculate how efficient the path was vs optimal"""
        if optimal_path_length == 0:
            return 0.0
        return optimal_path_length / max(self.nodes_visited, 1)
    
    def get_exploration_ratio(self, total_nodes):
        """Percentage of graph explored"""
        return (self.nodes_explored / total_nodes) * 100


class Maze:
    """Graph-based maze with enhanced features"""
    def __init__(self, grid_layout=None, width=10, height=10, seed=None):
        self.grid = []
        self.start_node = None
        self.goal_node = None
        self.width = 0
        self.height = 0
        self.seed = seed or random.randint(0, 999999)
        
        # Graph structure representation
        self.adjacency_list = {}  # node -> [(neighbor, edge_weight)]
        
        if grid_layout:
            self.parse_layout(grid_layout)
        else:
            random.seed(self.seed)
            self.generate_random(width, height)
        
        self.build_graph()
        self.optimal_path_length = self.calculate_optimal_path()
    
    def parse_layout(self, layout_str):
        """Parse string layout into graph nodes"""
        lines = layout_str.strip().split('\n')
        self.height = len(lines)
        self.width = len(lines[0])
        
        for r, line in enumerate(lines):
            row = []
            for c, char in enumerate(line.strip()):
                cost = 1
                if char == 'T': cost = 3
                elif char == 'P': cost = -2
                elif char == '#': cost = float('inf')
                
                node = Node(r, c, char, cost)
                row.append(node)
                
                if char == 'S':
                    self.start_node = node
                    node.cost = 0
                elif char == 'G':
                    self.goal_node = node
            self.grid.append(row)
    
    def generate_random(self, width, height):
        """Generate random maze using DFS (creates graph structure)"""
        self.width = width
        self.height = height
        
        # Initialize all walls
        self.grid = []
        for r in range(height):
            row = []
            for c in range(width):
                node = Node(r, c, '#', float('inf'))
                row.append(node)
            self.grid.append(row)
        
        # DFS maze generation (creates graph paths)
        stack = [(0, 0)]
        visited = set([(0, 0)])
        self.grid[0][0].type = '.'
        self.grid[0][0].cost = 1
        
        while stack:
            current_r, current_c = stack[-1]
            
            directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            random.shuffle(directions)
            
            found_next = False
            for dr, dc in directions:
                nr, nc = current_r + dr, current_c + dc
                if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in visited:
                    # Carve path (create graph edge)
                    wall_r, wall_c = current_r + dr // 2, current_c + dc // 2
                    self.grid[wall_r][wall_c].type = '.'
                    self.grid[wall_r][wall_c].cost = 1
                    self.grid[nr][nc].type = '.'
                    self.grid[nr][nc].cost = 1
                    
                    visited.add((nr, nc))
                    stack.append((nr, nc))
                    found_next = True
                    break
            
            if not found_next:
                stack.pop()
        
        # Set start and goal
        self.start_node = self.grid[0][0]
        self.start_node.type = 'S'
        self.start_node.cost = 0
        
        self.goal_node = self.grid[height-1][width-1]
        self.goal_node.type = 'G'
        self.goal_node.cost = 1
        
        # Ensure goal is reachable
        if self.goal_node.type == '#':
            self.goal_node.type = 'G'
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = height-1+dr, width-1+dc
                if 0 <= nr < height and 0 <= nc < width:
                    self.grid[nr][nc].type = '.'
                    self.grid[nr][nc].cost = 1
        
                # Add loops (increase graph connectivity)
        for r in range(1, height-1):
            for c in range(1, width-1):
                # Increased loop probability to 10% to create more cycles
                # This reduces the number of Articulation Points, making them more significant
                if self.grid[r][c].type == '#' and random.random() < 0.10:
                    open_neighbors = sum(1 for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]
                                       if self.grid[r+dr][c+dc].type != '#')
                    if open_neighbors >= 2:
                        self.grid[r][c].type = '.'
                        self.grid[r][c].cost = 1
        
        # Add traps and powerups (weighted graph edges)
        for r in range(height):
            for c in range(width):
                node = self.grid[r][c]
                if node.type == '.' and (r,c) != (0,0) and (r,c) != (height-1, width-1):
                    rand = random.random()
                    if rand < 0.06:
                        node.type = 'T'
                        node.cost = 3
                    elif rand < 0.10:
                        node.type = 'P'
                        node.cost = -2
    
    def build_graph(self):
        """Build explicit adjacency list representation of the graph"""
        self.adjacency_list = {}
        
        for r in range(self.height):
            for c in range(self.width):
                node = self.grid[r][c]
                if node.type == '#':
                    continue
                
                neighbors = self.get_neighbors(node)
                self.adjacency_list[node] = [(neighbor, neighbor.cost) for neighbor in neighbors]
    
    def get_node(self, r, c):
        """Get node at grid position"""
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.grid[r][c]
        return None
    
    def get_neighbors(self, node):
        """Get all neighbors (graph adjacency)"""
        neighbors = []
        # 8 directions for richer graph connectivity
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinals
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
        ]
        
        for dr, dc in directions:
            nr, nc = node.r + dr, node.c + dc
            neighbor = self.get_node(nr, nc)
            if neighbor and neighbor.type != '#':
                neighbors.append(neighbor)
        return neighbors
    
    def heuristic(self, node, heuristic_type='euclidean'):
        """Calculate heuristic for greedy algorithm"""
        # Enforce Euclidean only
        return math.sqrt((node.r - self.goal_node.r)**2 + (node.c - self.goal_node.c)**2)
    
    def calculate_optimal_path(self):
        """Calculate optimal path length using BFS (unweighted graph)"""
        if not self.start_node or not self.goal_node:
            return 0
        
        queue = deque([(self.start_node, 0)])
        visited = {self.start_node}
        
        while queue:
            node, dist = queue.popleft()
            
            if node == self.goal_node:
                return dist
            
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return float('inf')  # No path exists
    
    def bfs_analysis(self):
        """BFS for Structural Analysis (Distance Map)"""
        if not self.goal_node: return
        
        self.bfs_map = {}
        self.max_bfs_distance = 0
        
        queue = deque([(self.goal_node, 0)])
        self.bfs_map[self.goal_node] = 0
        
        while queue:
            node, dist = queue.popleft()
            self.max_bfs_distance = max(self.max_bfs_distance, dist)
            
            for neighbor in self.get_neighbors(node):
                if neighbor not in self.bfs_map:
                    self.bfs_map[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))

    def generate_heuristic_map(self):
        """Generate Euclidean Distance Map for visualization"""
        if not self.goal_node: return
        
        self.heuristic_map = {}
        self.max_heuristic_dist = 0
        
        for r in range(self.height):
            for c in range(self.width):
                node = self.grid[r][c]
                if node.type != '#':
                    dist = math.sqrt((node.r - self.goal_node.r)**2 + (node.c - self.goal_node.c)**2)
                    self.heuristic_map[node] = dist
                    self.max_heuristic_dist = max(self.max_heuristic_dist, dist)

    def a_star_optimal(self):
        """A* for Optimal Reference Cost"""
        if not self.start_node or not self.goal_node: return 0
        
        frontier = PriorityQueue()
        frontier.put(self.start_node, 0)
        
        cost_so_far = {}
        cost_so_far[self.start_node] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == self.goal_node:
                break
            
            for neighbor in self.get_neighbors(current):
                # Calculate edge cost
                edge_cost = 1
                if abs(current.r - neighbor.r) + abs(current.c - neighbor.c) == 2:
                    edge_cost = 1.414
                
                penalty = 0
                if neighbor.type == 'T': penalty = 3
                elif neighbor.type == 'P': penalty = -2
                
                # Prevent negative edge weights to avoid infinite loops (Negative Cycles)
                new_cost = cost_so_far[current] + max(0.1, edge_cost + penalty)
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor)
                    frontier.put(neighbor, priority)
        
        return cost_so_far.get(self.goal_node, 0)

    def get_total_walkable_nodes(self):
        """Count total nodes in graph (excluding walls)"""
        return sum(1 for r in range(self.height) for c in range(self.width) 
                  if self.grid[r][c].type != '#')

    
    def get_movement_target(self, node, direction):
        """Standard grid movement (default)"""
        nr = node.r + direction[0]
        nc = node.c + direction[1]
        return self.get_node(nr, nc)


class Player:
    """Human player with enhanced tracking"""
    def __init__(self, start_node):
        self.current_node = start_node
        self.total_cost = 0
        self.steps = 0
        self.traps_triggered = 0
        self.powerups_collected = 0
        self.path = [start_node]
        self.finished = False
        self.visited_positions = {(start_node.r, start_node.c)}
    
    def move(self, direction, maze):
        """Move in graph (traverse edge)"""
        # Support both standard grid and dynamic maze movement
        if hasattr(maze, 'get_movement_target'):
            target = maze.get_movement_target(self.current_node, direction)
        else:
            # Fallback for old implementations
            nr = self.current_node.r + direction[0]
            nc = self.current_node.c + direction[1]
            target = maze.get_node(nr, nc)
        
        if target and target.type != '#':
            self.current_node = target
            self.current_node.visited_by_player = True
            self.steps += 1
            self.path.append(target)
            self.visited_positions.add((target.r, target.c))
            return True
        return False






class HuffmanNode:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
        
    def __lt__(self, other):
        return self.freq < other.freq

class Huffman:
    def __init__(self):
        self.codes = {}

    def build_tree(self, text):
        if not text: return None
        
        freqs = {}
        for char in text:
            freqs[char] = freqs.get(char, 0) + 1
            
        pq = []
        for char, freq in freqs.items():
            heapq.heappush(pq, HuffmanNode(char, freq))
            
        while len(pq) > 1:
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            parent = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(pq, parent)
            
        root = heapq.heappop(pq)
        self.generate_codes(root, "")
        return root

    def generate_codes(self, node, code):
        if not node: return
        if not node.left and not node.right:
            self.codes[node.char] = code
            return
        self.generate_codes(node.left, code + "0")
        self.generate_codes(node.right, code + "1")

    def encode(self, text):
        self.codes = {}
        self.build_tree(text)
        return "".join([self.codes[c] for c in text])
    
    def get_stats(self, text):
        if not text: return {"original_bits": 0, "compressed_bits": 0, "ratio": 0}
        encoded = self.encode(text)
        original_bits = len(text) * 8
        compressed_bits = len(encoded)
        ratio = ((1 - compressed_bits / original_bits) * 100) if original_bits > 0 else 0
        return {"original_bits": original_bits, "compressed_bits": compressed_bits, "ratio": round(ratio, 1)}

class GreedyAI:
    """Greedy Best-First Search AI with enhanced metrics"""
    def __init__(self, start_node, goal_node, maze, heuristic_type='euclidean', algorithm_type='best_first'):
        self.current_node = start_node
        self.goal_node = goal_node
        self.maze = maze
        self.heuristic_type = heuristic_type
        self.algorithm_type = algorithm_type
        
        self.total_cost = 0
        self.steps = 0
        self.solution_cost = 0
        self.solution_steps = 0
        self.path = [start_node]
        self.finished = False
        self.full_path = []
        self.path_index = 0
        self.action_log = ""
        
        # Enhanced metrics
        self.metrics = PerformanceMetrics()
        self.visited_nodes = set() # For visualization
        self.compute_path()
        
    def heuristic(self, node):
        return self.maze.heuristic(node, self.heuristic_type)

    def compute_path(self):
        # Reset path tracking when re-calculating (crucial for dynamic updates)
        self.path_index = 0
        self.finished = False
        
        if self.algorithm_type == 'hill_climbing':
            self.compute_path_hill_climbing()
        else:
            self.compute_path_best_first()

    def compute_path_best_first(self):
        frontier = PriorityQueue()
        frontier.put(self.current_node, 0)
        
        came_from = {}
        cost_so_far = {} # For A* and Dijkstra
        
        came_from[self.current_node] = None
        cost_so_far[self.current_node] = 0
        
        self.visited_nodes.add(self.current_node)
        
        current = None
        
        while not frontier.empty():
            current = frontier.get()
            self.visited_nodes.add(current) # Track visited
            self.metrics.record_visit(current)
            
            if current == self.goal_node:
                break
            
            for neighbor in self.maze.get_neighbors(current):
                # Calculate new cost (g_score)
                # Edge weight logic (1 for normal, 1.414 for diagonal, + penalties)
                edge_cost = 1
                if abs(current.r - neighbor.r) + abs(current.c - neighbor.c) == 2:
                    edge_cost = 1.414
                
                # Note: In the game loop, penalties are applied on move. 
                # For pathfinding, we should consider them if we want "aware" algorithms like A*
                # But Greedy usually ignores them. 
                # Let's make A* and Dijkstra aware of costs (Traps/Powerups)
                penalty = 0
                if neighbor.type == 'T': penalty = 3
                elif neighbor.type == 'P': penalty = -2
                
                # Dynamic Logic: Avoid Unstable Nodes (Warning Phase)
                if hasattr(self.maze, 'is_node_unstable') and self.maze.is_node_unstable(neighbor):
                    penalty += 50 # High penalty to discourage use unless necessary

                # Prevent negative edges for Dijkstra/A* stability
                step_cost = max(0.1, edge_cost + penalty)
                new_cost = cost_so_far[current] + step_cost
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    
                    # Priority Calculation
                    priority = 0
                    if self.algorithm_type == 'dijkstra':
                        priority = new_cost
                    elif self.algorithm_type == 'a_star':
                        priority = new_cost + self.heuristic(neighbor)
                    else: # Greedy Best-First
                        priority = self.heuristic(neighbor)
                    
                    self.metrics.record_evaluation(neighbor, priority)
                    frontier.put(neighbor, priority)
                    came_from[neighbor] = current
        
        if current == self.goal_node:
            path = []
            curr = self.goal_node
            while curr != self.current_node:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            self.full_path = path
            self.calculate_path_stats()
        else:
            print(f"No path found for AI ({self.algorithm_type})")
            self.finished = True # Prevent infinite wait

    def compute_path_hill_climbing(self):
        """Pure Greedy (Hill Climbing) - No backtracking, can get stuck"""
        current = self.current_node
        path = []
        visited = {current}
        
        while current != self.goal_node:
            self.visited_nodes.add(current)
            self.metrics.record_visit(current)
            
            neighbors = self.maze.get_neighbors(current)
            best_neighbor = None
            best_h = float('inf')
            
            # Find best unvisited neighbor
            for neighbor in neighbors:
                if neighbor not in visited:
                    h = self.heuristic(neighbor)
                    self.metrics.record_evaluation(neighbor, h)
                    if h < best_h:
                        best_h = h
                        best_neighbor = neighbor
            
            if best_neighbor:
                path.append(best_neighbor)
                visited.add(best_neighbor)
                current = best_neighbor
            else:
                # Dead end - Algorithm Fails (No Backtracking)
                self.metrics.record_dead_end()
                print(f"Hill Climbing stuck at {current}")
                break
                
        # Always set the path found so far, even if incomplete
        self.full_path = path
        

        if current == self.goal_node:
            self.calculate_path_stats()
        else:
            # Do NOT set finished=True here. Let the AI walk the partial path first.
            # self.finished = True 
            pass

    def calculate_path_stats(self):
        """Pre-calculate cost and steps for the found path"""
        self.solution_steps = len(self.full_path)
        self.solution_cost = 0
        
        current = self.path[0] # Start node
        for next_node in self.full_path:
            move_cost = 1
            if abs(current.r - next_node.r) + abs(current.c - next_node.c) == 2:
                move_cost = 1.414
            
            penalty = 0
            if next_node.type == 'T': penalty = 3
            elif next_node.type == 'P': penalty = -2
            
            self.solution_cost += move_cost + penalty
            current = next_node

    def choose_move(self, maze):
        if self.finished: return

        if self.path_index < len(self.full_path):
            next_node = self.full_path[self.path_index]
            
            # Calculate cost
            move_cost = 1
            if abs(self.current_node.r - next_node.r) + abs(self.current_node.c - next_node.c) == 2:
                move_cost = 1.414
            
            penalty = 0
            if next_node.type == 'T': penalty = 3
            elif next_node.type == 'P': penalty = -2
            
            # Log Action
            if penalty == 3: self.action_log += "T"
            elif penalty == -2: self.action_log += "P"
            else: self.action_log += "M"
            
            self.current_node = next_node
            self.path.append(next_node)
            self.steps += 1
            self.total_cost += move_cost + penalty
            self.path_index += 1
            
            if self.current_node == self.goal_node:
                self.finished = True
        else:
            # End of path but not at goal
            print(f"DEBUG: End of path. Finished={self.finished}, Current={self.current_node}, Goal={self.goal_node}")
            if not self.finished and self.current_node != self.goal_node:
                 error_msg = f"CRITICAL ERROR: AI stuck at {self.current_node}. Backtracking required to solve this maze!"
                 print(error_msg)
                 raise RuntimeError(error_msg)
            self.finished = True
    
    def get_efficiency_vs_optimal(self, optimal_cost):
        if self.total_cost == 0: return 0
        return optimal_cost / self.total_cost
class HierarchicalAI(GreedyAI):
    """
    Divide & Conquer AI: Plans path via Regions/Islands first, then navigates locally.
    Uses an Augmented Graph (Regions + Articulation Points) to handle complex connectivity.
    """
    def __init__(self, start_node, goal_node, maze):
        super().__init__(start_node, goal_node, maze, algorithm_type='hierarchical')
        self.algorithm_name = "Divide & Conquer (Hierarchical)"
        self.high_level_plan = [] # List of (RegionID or AP-Node)
        self.waypoints = [] # List of physical Nodes to visit

    def compute_path(self):
        self.metrics = PerformanceMetrics()
        self.visited_nodes = set()
        self.path_index = 0
        self.finished = False
        self.high_level_plan = []
        self.waypoints = []
        
        # 1. Structural Check & Lazy Initialization
        if not hasattr(self.maze, 'regions') or not self.maze.regions:
            # Maze hasn't been analyzed (e.g., Standard Maze). Analyze it now!
            # print("HierarchicalAI: Performing Lazy Structural Analysis...")
            self.maze.build_graph() # Ensure adjacency list is fresh
            
            # Compute and attach to maze instance so Visualization can read it
            self.maze.articulation_points = RegionLogic.compute_articulation_points(self.maze)
            self.maze.regions, self.maze.region_connectivity, _ = RegionLogic.compute_regions(self.maze, self.maze.articulation_points)
            
        if not self.maze.regions:
             print("Maze has no regions (single component?). Falling back to A*.")
             self.algorithm_type = 'a_star'
             self.compute_path_best_first() # Fallback
             return

        # 2. Build High-Level Graph
        # Nodes: "R_{id}" for regions, and Node objects for APs
        self.high_level_graph = self.build_augmented_graph()

        # 3. Identify Start and Goal Graph Nodes
        start_id = self.get_graph_id(self.current_node)
        goal_id = self.get_graph_id(self.goal_node)
        
        print(f"DEBUG PATH: StartID={start_id}, GoalID={goal_id}")

        if not start_id or not goal_id:
             print(f"Start/Goal mapping failed. Start={start_id}, Goal={goal_id}. Fallback.")
             self.algorithm_type = 'a_star'
             self.compute_path_best_first()
             return

        # 4. High-Level Pathfinding (BFS)
        hl_path = self.find_high_level_path(start_id, goal_id)
        
        if not hl_path:
             print("No high-level path found on Augmented Graph! Fallback to A*.")
             self.algorithm_type = 'a_star'
             self.compute_path_best_first()
             return
             
        self.high_level_plan = hl_path
        print(f"DEBUG PATH: Plan Found! Length={len(hl_path)}")

        # 5. Low-Level Path Construction (Stitching)
        full_path_nodes = []
        current_node = self.current_node
        
        # Iterate through path to identify physical waypoints (APs)
        # We skip Region IDs as they are just traversal mediums
        waypoints = []
        for i in range(1, len(hl_path)):
            node = hl_path[i]
            if isinstance(node, Node): # It's an AP
                waypoints.append(node)
        
        waypoints.append(self.goal_node)
        self.waypoints = waypoints
        
        for next_wp in waypoints:
            # Pathfind to Next Waypoint (using A*)
            segment = self.get_path_segment(current_node, next_wp)
            if not segment:
                print(f"Error: Could not reach waypoint {next_wp} from {current_node}")
                return
                
            full_path_nodes.extend(segment[:-1]) # Exclude last to avoid duplication
            current_node = next_wp
            
        # Add final node
        full_path_nodes.append(self.goal_node)
        self.full_path = full_path_nodes
        self.calculate_path_stats()

    def get_graph_id(self, node):
        """Map a physical node to a High-Level Graph Node (RegionID-Str or AP-Node)"""
        if node in self.maze.articulation_points:
            return node
        elif node in self.maze.regions:
            return f"R_{self.maze.regions[node]}"
        return None

    def build_augmented_graph(self):
        graph = defaultdict(set)
        
        # Add AP connections
        for ap in self.maze.articulation_points:
            # 1. Check neighbors for Regions
            # 2. Check neighbors for other APs
            
            seen_regions = set()
            for neighbor in self.maze.get_neighbors(ap):
                if neighbor in self.maze.articulation_points:
                    # AP <-> AP
                    graph[ap].add(neighbor)
                    graph[neighbor].add(ap)
                elif neighbor in self.maze.regions:
                    # AP <-> Region
                    rid = f"R_{self.maze.regions[neighbor]}"
                    if rid not in seen_regions:
                        graph[ap].add(rid)
                        graph[rid].add(ap)
                        seen_regions.add(rid)
                        
        return graph

    def find_high_level_path(self, start_id, goal_id):
        """BFS on Augmented Graph"""
        queue = deque([(start_id, [start_id])])
        visited = {start_id}
        
        while queue:
            curr, path = queue.popleft()
            
            if curr == goal_id:
                return path
            
            for neighbor in self.high_level_graph[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    def get_path_segment(self, start, end):
        """Local A* search between two nodes"""
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while not frontier.empty():
            current = frontier.get()
            self.metrics.record_evaluation(current, 0) # Log for viz
            
            if current == end:
                break
            
            for neighbor in self.maze.get_neighbors(current):
                # Standard cost + penalties
                penalty = 0
                if neighbor.type == 'T': penalty = 3
                elif neighbor.type == 'P': penalty = -2
                
                new_cost = cost_so_far[current] + max(0.1, 1 + penalty)
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic_dist(neighbor, end)
                    frontier.put(neighbor, priority)
                    came_from[neighbor] = current
        
        if end not in came_from: return None
        
        # Reconstruct
        path = []
        curr = end
        while curr != start:
            path.append(curr)
            curr = came_from[curr]
        path.append(start)
        path.reverse()
        return path

    def heuristic_dist(self, a, b):
        return math.sqrt((a.r - b.r)**2 + (a.c - b.c)**2)
