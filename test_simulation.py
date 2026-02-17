import unittest
from game_classes import Maze, GreedyAI

class TestSimulation(unittest.TestCase):
    def setUp(self):
        # Create a fixed maze where different heuristics might choose different paths
        # S . . . G
        # . # # # .
        # . . . . .
        layout = """
S...G
.###.
.....
"""
        self.maze = Maze(grid_layout=layout.strip())

    def test_heuristics_run(self):
        """Verify all heuristics run without error"""
        heuristics = ['euclidean', 'manhattan', 'chebyshev']
        for h in heuristics:
            ai = GreedyAI(self.maze.start_node, self.maze.goal_node, self.maze, heuristic_type=h)
            self.assertTrue(len(ai.full_path) > 0, f"Heuristic {h} failed to find path")

    def test_hill_climbing_vs_best_first(self):
        """Verify Hill Climbing behaves differently (or at least runs)"""
        ai_bf = GreedyAI(self.maze.start_node, self.maze.goal_node, self.maze, algorithm_type='best_first')
        ai_hc = GreedyAI(self.maze.start_node, self.maze.goal_node, self.maze, algorithm_type='hill_climbing')
        
        self.assertTrue(ai_bf.finished or len(ai_bf.full_path) > 0)
        # Hill climbing might fail or succeed, but it should run
        print(f"Best First Path: {len(ai_bf.full_path)}")
        print(f"Hill Climbing Path: {len(ai_hc.full_path)}")

    def test_optimal_algorithms(self):
        """Verify A* and Dijkstra find the same optimal path length"""
        # Create a maze where path cost matters (traps)
        # S . . G
        # . T T .
        # . . . .
        layout = """
S..G
.TT.
....
"""
        maze = Maze(grid_layout=layout.strip())
        
        ai_astar = GreedyAI(maze.start_node, maze.goal_node, maze, algorithm_type='a_star')
        ai_dijkstra = GreedyAI(maze.start_node, maze.goal_node, maze, algorithm_type='dijkstra')
        ai_greedy = GreedyAI(maze.start_node, maze.goal_node, maze, algorithm_type='best_first')
        
        # A* and Dijkstra should be optimal
        self.assertEqual(ai_astar.total_cost, ai_dijkstra.total_cost)
        
        # Greedy might take the trap path (shorter distance but higher cost)
        # S->(0,1)->(0,2)->G (Cost: 1+1+1 = 3)
        # S->(1,0)->(1,1)[T]->(1,2)[T]->(1,3)->G (Cost: 1+4+4+1 = 10)
        # Actually Euclidean heuristic will likely guide it along the top row (0,1) is dist 2, (1,0) is dist 2.23
        # So greedy might actually be optimal here.
        # Let's just check they run and produce valid paths.
        self.assertTrue(len(ai_astar.full_path) > 0)
        self.assertTrue(len(ai_dijkstra.full_path) > 0)
        
        # Verify costs are calculated (should be > 0)
        self.assertGreater(ai_astar.solution_cost, 0)
        self.assertGreater(ai_dijkstra.solution_cost, 0)
        
        print(f"A* Cost: {ai_astar.solution_cost}")
        print(f"Dijkstra Cost: {ai_dijkstra.solution_cost}")
        print(f"Greedy Cost: {ai_greedy.solution_cost}")

if __name__ == '__main__':
    unittest.main()
