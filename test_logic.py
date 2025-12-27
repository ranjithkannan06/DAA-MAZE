from maze import MazeGenerator
from ai import GreedyAI

def test_maze_and_ai():
    print("Testing Maze Generation...")
    width, height = 15, 15
    maze_gen = MazeGenerator(width, height)
    graph = maze_gen.generate()
    
    # Check if start and goal are in graph
    assert maze_gen.start_pos in graph.nodes
    assert maze_gen.goal_pos in graph.nodes
    print(f"Maze generated with {len(graph.nodes)} path nodes.")

    print("\nTesting Greedy AI...")
    ai = GreedyAI(graph, maze_gen.start_pos, maze_gen.goal_pos)
    
    max_steps = 1000
    steps = 0
    while not ai.finished and steps < max_steps:
        ai.step()
        steps += 1
    
    metrics = ai.get_metrics()
    print(f"AI finished in {steps} steps.")
    print(f"Metrics: {metrics}")
    
    if ai.current_pos == maze_gen.goal_pos:
        print("SUCCESS: AI reached the goal.")
    else:
        print("FAILURE: AI did not reach the goal.")

if __name__ == "__main__":
    test_maze_and_ai()
