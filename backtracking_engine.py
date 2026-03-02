import time

class BacktrackingEngine:
    """
    Core DFS Simulation Engine.
    Refactored to distribute architectural logic across 4 team members.
    """
# ==== MEMBER 1 SECTION ====
    # Responsibility: Traversal Architecture
    # ==========================================
    
    def _init_(self, start_node, goal_node, maze):
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
            self.rejected_nodes.add(prev_node)
            if self.path:
                new_curr = self.path[-1]
                self.backtrack_edges.append((prev_node, new_curr))
                edge = tuple(sorted(((prev_node.r, prev_node.c), (new_curr.r, new_curr.c))))
                self.rejected_edges.add(edge)
                self.current_node = new_curr
                self.decision_log = f"Popping ({prev_node.r}, {prev_node.c}) - Returning to parent ({new_curr.r}, {new_curr.c})"
                