import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from dynamic_maze import DynamicMaze
from game_classes import HierarchicalAI, Node

def test_hierarchical_ai():
    print("Initializing Dynamic Maze (15x15)...")
    # Use specific seed for reproducibility if needed, but random is fine for robustness check
    maze = DynamicMaze(width=15, height=15, seed=42) 
    
    print(f"Start: {maze.start_node}, Goal: {maze.goal_node}")
    
    # Ensure maze analysis is done
    maze.analyze_structure()
    print(f"Regions found: {len(maze.region_list_map)}")
    print(f"Articulation Points: {len(maze.articulation_points)}")
    
    # Initialize AI
    ai = HierarchicalAI(maze.start_node, maze.goal_node, maze)
    
    start_region = maze.regions.get(maze.start_node)
    goal_region = maze.regions.get(maze.goal_node)
    print(f"Start Region: {start_region}, Goal Region: {goal_region}")
    print(f"Region Connectivity Keys: {list(maze.region_connectivity.keys())}")
    print(f"Full Connectivity: {dict(maze.region_connectivity)}")
    
    # Check for AP-AP connections
    ap_ap_links = 0
    for ap in maze.articulation_points:
        for neighbor in maze.get_neighbors(ap):
            if neighbor in maze.articulation_points:
                ap_ap_links += 1
    print(f"AP-AP Connections found: {ap_ap_links}")
    
    print("Running Compute Path...")
    ai.compute_path()
    
    if ai.full_path:
        print("Path found!")
        print(f"Path Length: {len(ai.full_path)}")
        print(f"Cost: {ai.solution_cost}")
        
        # Verify connectivity
        curr = ai.path[0]
        for i, node in enumerate(ai.full_path):
            if abs(curr.r - node.r) + abs(curr.c - node.c) > 2: # Allow diagonals (dist=2)
                print(f"ERROR: Discontinuity at index {i}: {curr} -> {node}")
                return
            curr = node
            
        print("Path connectivity verified.")
        
        # Verify Goal
        if ai.full_path[-1] == maze.goal_node:
            print("Path reaches goal.")
        else:
            print(f"ERROR: Path ends at {ai.full_path[-1]}, expected {maze.goal_node}")
            
    else:
        print("No path found.")
        # It's possible for random maze to be disconnected, but DynamicMaze usually ensures start/goal are capable of connecting or assumes so. 
        # Standard Maze generation guarantees start/goal connection.

if __name__ == "__main__":
    test_hierarchical_ai()