import time

class BacktrackingEngine:
    """
    Core DFS Simulation Engine.
    Refactored to distribute architectural logic across 4 team members.
    """
# ==== MEMBER 1 SECTION ====
    # Responsibility: Traversal Architecture
    # ==========================================
    
    def __init__(self, start_node, goal_node, maze):
        self.initialize_engine(start_node, goal_node, maze)
        
    def initialize_engine(self, start_node, goal_node, maze):
        self.maze = maze
        self.start_node = start_node
        self.goal_node = goal_node
        
        # Stack structure: list of (node, parent_node) to trace edges
        self.stack = [(start_node, None)]
        self.visited = set()
        self.current_node = start_node
        self.path = []
        
        # State control
        self.state = "IDLE" # IDLE, FORWARD, DEAD_END, BACKTRACK, FINISHED
        self.decision_log = "Simulation Initialized. Press S to start."
        self.full_exploration_mode = False
        
        # Cross-member tracking setups
        self.frontier_nodes = set()
        self.backtrack_edges = []
        self.forward_edges = []
        self.rejected_edges = set()
        self.rejected_nodes = set()
        
        # Initialize Metrics (Member 4)
        self.start_time = time.time()
        self.step_count = 0
        self.backtrack_count = 0
        self.dead_ends_encountered = 0
        self.history_metrics = []

    def select_next_node(self):
        """Pops the next valid unvisited node from the DFS stack."""
        if not self.stack:
            return None, None
            
        next_node, parent = self.stack.pop()
        return next_node, parent

    def check_goal_reached(self):
        """Checks termination condition against exploration mode."""
        if self.current_node == self.goal_node and not self.full_exploration_mode:
            return True
        return False
# ==========================================
# ==== MEMBER 2 SECTION ====
# Responsibility: State Machine & Dead-End Control
# ==========================================
    
    def step(self):
        """Main tick cycle moving the state machine forward one frame."""
        if self.state == "FINISHED":
            return
            
        # 1. Handle Backtrack UI transitions
        if self.state == "DEAD_END":
            self.change_state("BACKTRACK")
            self.record_backtrack_event() # Call Member 4
            if not self.stack:
                self.decision_log = "Search Exhausted. No path found."
                self.change_state("FINISHED")
            else:
                self.decision_log = "Dead End Reached. Backtracking..."
            return
            
        if self.state == "BACKTRACK":
            self.handle_backtrack_transition()
            return

        # 2. Main Logic Step
        if self.state == "FORWARD" or self.state == "IDLE":
            self.current_node, parent = self.select_next_node() # Call Member 1
            
            if not self.current_node:
                self.decision_log = "Full Graph Exploration Complete." if self.full_exploration_mode else "Stack Empty: No Path Found."
                self.change_state("FINISHED")
                return
                
            if self.current_node in self.visited:
                self.decision_log = f"Skipping visited node ({self.current_node.r}, {self.current_node.c})"
                self.change_state("FORWARD")
                return

            self.visited.add(self.current_node)
            self.path.append(self.current_node)
            if parent:
                self.forward_edges.append((parent, self.current_node))
                
            if self.check_goal_reached(): # Call Member 1
                self.decision_log = "Goal Reached!"
                self.change_state("FINISHED")
                
                # Force one final metric update to capture the finished state
                self.update_metrics()
                return
                
            # 3. Explore Neighbors & Dead Ends
            valid_neighbors = self.detect_dead_end()
            
            if not valid_neighbors:
                self.change_state("DEAD_END")
                self.dead_ends_encountered += 1
                self.decision_log = "Dead End Reached. Backtracking..."
            else:
                self.change_state("FORWARD")
                self.decision_log = f"Moving to ({self.current_node.r}, {self.current_node.c})"
                
                # Call Member 3 to organize the stack injection
                self.adjust_exploration_order(valid_neighbors)
                
        # 4. Finalize Step Metrics Snapshot (Member 4)
        self.update_metrics()
        
    def change_state(self, new_state):
        self.state = new_state

    def detect_dead_end(self):
        """Returns valid neighbors, or empty list if dead end."""
        neighbors = self.maze.get_neighbors(self.current_node)
        return [n for n in neighbors if n not in self.visited and n.type != '#']

    def handle_backtrack_transition(self):
        """Safely pops the backtracking path visually until finding the next valid branch."""
        if not self.stack:
            self.change_state("FINISHED")
            self.decision_log = "Full Graph Exploration Complete." if self.full_exploration_mode else "Stack Empty: No Path Found."
            return
            
        next_target, target_parent = self.stack[-1]
        if not self.path or self.path[-1] == target_parent:
            self.change_state("FORWARD")
            r, c = (target_parent.r, target_parent.c) if target_parent else (self.start_node.r, self.start_node.c)
            self.decision_log = f"Exploring new branch from ({r}, {c})"
        else:
            prev_node = self.path.pop()
            self.backtrack_count += 1  # Increment ONLY on actual reverse traversal
            self.rejected_nodes.add(prev_node)
            if self.path:
                new_curr = self.path[-1]
                self.backtrack_edges.append((prev_node, new_curr))
                edge = tuple(sorted(((prev_node.r, prev_node.c), (new_curr.r, new_curr.c))))
                self.rejected_edges.add(edge)
                self.current_node = new_curr
                self.decision_log = f"Popping ({prev_node.r}, {prev_node.c}) - Returning to parent ({new_curr.r}, {new_curr.c})"
    
  # ==========================================
    # ==== MEMBER 3 SECTION ====
    # Responsibility: Behavior Optimization & Heuristics
    # ==========================================

    def compute_branch_priority(self, n):
        """Computes priority value. Used for injecting backtracking intensity."""
        return self.maze.heuristic(n, 'manhattan')

    def adjust_exploration_order(self, valid_neighbors):
        """Prioritizes neighbor exploration order based on required depth intensity."""
        self.frontier_nodes = set()
        
        # Inject branch logic to guarantee deep false trees are traversed
        should_reverse = self.control_dead_end_density()
            
        valid_neighbors.sort(key=self.compute_branch_priority, reverse=should_reverse)
        
        for neighbor in valid_neighbors:
            self.frontier_nodes.add(neighbor)
            self.stack.append((neighbor, self.current_node))
            
    def control_dead_end_density(self):
        """Forces true DFS to run into dead ends by prioritizing nodes farthest from the goal."""
        # Standard greedy moves towards the goal. Inverse moves away into dead zones first.
        is_backtracking_maze = getattr(self.maze, 'maze_type', None) == "BACKTRACKING"
        # Return True for standard (greedy sort puts lowest at the end of the stack to be popped first).
        # Return False to invert the stack logic, plunging the AI into the deepest dead ends first.
        return False if is_backtracking_maze else True





    # ==========================================
    # ==== MEMBER 4 SECTION ====
    # Responsibility: Metrics Collection
    # ==========================================

    def update_metrics(self):
        """Records runtime scaling analytics per step."""
        self.step_count += 1
        runtime_ms = (time.time() - self.start_time) * 1000
        
        # Check active edge for complexity viz tracking
        current_edge = None
        if self.state == "BACKTRACK" and self.backtrack_edges:
           current_edge = self.backtrack_edges[-1]
        
        snapshot = {
            "step": self.step_count,
            "runtime": runtime_ms,
            "nodes": len(self.visited),
            "backtracks": self.backtrack_count,
            "stack_depth": len(self.stack),
            "state": self.state,
            "edge": current_edge
        }
        self.history_metrics.append(snapshot)

    def record_backtrack_event(self):
        """Called when a dead end is logged, but actual backtrack count happens during pop."""
        pass

    def get_final_statistics(self):
        """Computes terminal graph search efficiency."""
        explored = len(self.visited)
        efficiency = 0
        if explored > 0:
            opt = getattr(self.maze, 'optimal_path_length', 1)
            efficiency = min(100, (opt / explored) * 100)
            
        return {
            "backtracks": self.backtrack_count,
            "dead_ends": self.dead_ends_encountered,
            "explored": explored,
            "efficiency": f"{efficiency:.1f}%"
        }