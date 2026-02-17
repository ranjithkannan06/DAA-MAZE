

def compute_path_hill_climbing(self):
    """Pure Greedy - No backtracking, can get stuck"""
    current = self.current_node
    while current != self.goal_node:
        neighbors = self.maze.get_neighbors(current)
        best_neighbor = None
        best_h = float('inf')
        
        # Find best unvisited neighbor
        for neighbor in neighbors:
            if neighbor not in visited:
                h = self.heuristic(neighbor)
                if h < best_h:
                    best_h = h
                    best_neighbor = neighbor
        
        if best_neighbor:
            current = best_neighbor
        else:
            # Dead end - Algorithm Fails
            break
