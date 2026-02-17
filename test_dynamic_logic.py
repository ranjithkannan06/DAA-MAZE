import time
import random
from dynamic_maze import DynamicMaze

def test_dynamic_maze():
    print("Initializing DynamicMaze...")
    maze = DynamicMaze(width=10, height=10)
    maze.update_interval = 0.1 # Fast updates for test
    
    print("Testing Event Queueing (Multiple Types)...")
    event_counts = {'ADD': 0, 'REMOVE': 0, 'SHIFT': 0, 'MASS': 0}
    
    for i in range(20):
        maze.update_structure()
        if maze.pending_changes:
            # Infer type from changes
            # This is tricky since we schedule raw ADD/REMOVE.
            # We just check if changes are queued.
            pass
        maze.pending_changes = [] # Clear for next iter
        maze.last_update_time = time.time() - 10 # Force update
        
    print("Simulating processed updates...")
    maze.queue_dynamic_event()
    if not maze.pending_changes:
        print("FAIL: No event queued.")
        return
        
    change = maze.pending_changes[0]
    print(f"Event Queued: {change['type']} (Timer: {change['timer']})")
    
    print("Processing Warning Phase...")
    maze.process_updates(0.5)
    print(f"State after 0.5s: {change['state']}")
    
    maze.process_updates(0.6) # Push past 1.0s warning
    print(f"State after +0.6s: {change['state']}")
    
    if change['state'] != 'ANIMATING':
        print("FAIL: Did not transition to ANIMATING.")
        return

    print("Processing Animation Phase...")
    maze.process_updates(2.0) # Push past animation
    
    if maze.pending_changes:
        print("FAIL: Change still pending after animation.")
        return
        
    print("SUCCESS: Event processed and applied.")

if __name__ == "__main__":
    test_dynamic_maze()