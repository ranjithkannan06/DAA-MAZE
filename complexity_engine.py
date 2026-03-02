class ComplexityEngine:
    """
    Core Mathematical scaling system linking DFS runtime to Graph Theory.
    Refactored to distribute logic across 4 team members equally.
    """
    
    def __init__(self, maze, history_metrics):
        self.maze = maze
        self.history_metrics = history_metrics

    # ==== MEMBER 1 SECTION ====
    # Responsibility: Theoretical Complexity Layer
    # ==========================================
    
    def compute_theoretical_complexity(self):
        """Standard DFS Big-O Notation Proof."""
        return "O(V + E)"
        
    def derive_grid_complexity(self):
        """Converts raw DFS theory into physical Grid node scaling."""
        n_val = max(self.maze.width, self.maze.height)
        v = n_val ** 2
        e = 4 * v # Max 4 edges per node in grid graph
        return {
            "n": n_val,
            "v_approx": v,
            "e_approx": e,
            "final_o": "O(n²)"
        }
# ==========================================
# ==== MEMBER 2 SECTION ====
# Responsibility: Empirical Runtime Collection
# ==========================================
    
    def collect_runtime_data(self):
        """Parses the history pipeline to extract pure scaling arrays."""
        steps = []
        runtimes = []
        nodes = []
        
        for m in self.history_metrics:
            steps.append(m['step'])
            runtimes.append(m['runtime'])
            nodes.append(m['nodes'])
            
        return steps, runtimes, nodes
        
    def calculate_growth_curve(self):
        """Computes difference quotients across the runtime dataset."""
        steps, runtimes, nodes = self.collect_runtime_data()
        
        if len(steps) < 2:
            return 0.0
            
        # Delta runtime / Delta step (approximates empirical slope)
        dr = runtimes[-1] - runtimes[0]
        ds = steps[-1] - steps[0]
        
        return dr / ds if ds > 0 else 0.0
        
