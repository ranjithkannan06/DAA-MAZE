

import sys
import os
import inspect

# -------------------------------------------------------------------------
# SETUP: Add parent directory to path to import game classes
# -------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from game_classes import Maze, GreedyAI, Node
    print("Successfully imported game_classes from parent directory.")
except ImportError as e:
    print(f"Error importing game_classes: {e}")
    print("Ensure this script is run from the 'AI_Search_Algorithms' directory or that the parent directory structure is correct.")
    sys.exit(1)

# -------------------------------------------------------------------------
# TEST FRAME HELPER
# -------------------------------------------------------------------------

def run_custom_algorithm(algorithm_name, heuristic_func=None, compute_path_func=None):
    """
    Runs a simulation using a custom algorithm implementation.
    
    Args:
        algorithm_name (str): Name of the algorithm for display.
        heuristic_func (function, optional): The heuristic function `heuristic(self, node)`.
        compute_path_func (function, optional): The path computation logic `compute_path_best_first(self)`.
    """
    print(f"\n{'='*60}")
    print(f"TESTING ALGORITHM: {algorithm_name}")
    print(f"{'='*60}")

    # 1. Initialize Maze (Use fixed seed for consistent comparisons)
    print("Initializing Maze...")
    maze = Maze(width=21, height=21, seed=42)
    maze.bfs_analysis() # Helper for default metrics
    print("Maze Initialized.")

    # 2. Define Custom AI Subclass
    class CustomAI(GreedyAI):
        def __init__(self, start_node, goal_node, maze):
            # Initialize parent with defaults
            super().__init__(start_node, goal_node, maze, heuristic_type='custom', algorithm_type='custom')
            
    # 3. Inject Custom Methods
    if heuristic_func:
        # Bind the function to the class/instance
        # ensure signature matches: heuristic(self, node)
        CustomAI.heuristic = heuristic_func
        print(f"-> Injected Custom Heuristic: {heuristic_func.__name__}")
        
    if compute_path_func:
        # Bind the function to the class/instance
        # ensure signature matches: compute_path_best_first(self) or similar
        # We override the main compute driver or specific sub-methods depending on what the user provides
        CustomAI.compute_path = compute_path_func
        print(f"-> Injected Custom Path Computation: {compute_path_func.__name__}")

    # 4. Run Simulation
    print("Running Simulation...")
    try:
        ai = CustomAI(maze.start_node, maze.goal_node, maze)
        
        # 5. Report Results
        print("\n" + "-"*30)
        print("PERFORMANCE METRICS")
        print("-" * 30)
        print(f"Success:      {ai.finished and ai.current_node == maze.goal_node}")
        print(f"Total Cost:   {ai.total_cost:.2f}")
        print(f"Steps Taken:  {ai.steps}")
        print(f"Explored:     {ai.metrics.nodes_explored}")
        print(f"Visited:      {ai.metrics.nodes_visited}")
        
        if maze.optimal_path_length:
            efficiency = (maze.optimal_path_length / ai.total_cost) * 100 if ai.total_cost > 0 else 0
            print(f"Efficiency:   {efficiency:.1f}% (vs Optimal)")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Algorithm Failed: {e}")
        import traceback
        traceback.print_exc()

# -------------------------------------------------------------------------
# COLLABORATOR SECTION
# -------------------------------------------------------------------------
# Import your algorithm file here and call run_custom_algorithm()
# Example:
# from GBFS.chebyshev import chebyshev
# run_custom_algorithm(
#     algorithm_name="GBFS Chebyshev",
#     heuristic_func=chebyshev.heuristic,
#     compute_path_func=chebyshev.compute_path_best_first
# )

if __name__ == "__main__":
    print("\nMain Frame Ready. Uncomment imports in the COLLABORATOR SECTION to test algorithms.")
