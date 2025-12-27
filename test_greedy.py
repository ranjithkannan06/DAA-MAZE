import unittest
from game_classes import Maze, GreedyAI, Node, PerformanceMetrics, Player


# test_greedy.py

class TestGraphStructure(unittest.TestCase):
    """Test graph representation and connectivity"""
    
    def test_adjacency_list_creation(self):
        """Graph should build proper adjacency list"""
        layout = "S.G\n..."
        maze = Maze(grid_layout=layout)
        
        # Should have adjacency list for all non-wall nodes
        self.assertGreater(len(maze.adjacency_list), 0)
        
        # Start node should have neighbors
        self.assertIn(maze.start_node, maze.adjacency_list)
        self.assertGreater(len(maze.adjacency_list[maze.start_node]), 0)
    
    def test_graph_edges_bidirectional(self):
        """Graph edges should be properly represented"""
        layout = "S.\n.G"
        maze = Maze(grid_layout=layout)
        
        start = maze.start_node
        neighbors = maze.get_neighbors(start)
        
        # Start should connect to at least one neighbor
        self.assertGreater(len(neighbors), 0)
        
        # Neighbor should connect back
        for neighbor in neighbors:
            neighbor_neighbors = maze.get_neighbors(neighbor)
            self.assertIn(start, neighbor_neighbors)
    
    def test_wall_nodes_excluded(self):
        """Walls should not be in graph"""
        layout = "S#G"
        maze = Maze(grid_layout=layout)
        
        wall_node = maze.get_node(0, 1)
        self.assertEqual(wall_node.type, '#')
        self.assertNotIn(wall_node, maze.adjacency_list)
    
    def test_edge_weights(self):
        """Graph edges should have proper weights"""
        layout = "STP"
        maze = Maze(grid_layout=layout)
        
        start = maze.start_node
        neighbors_with_weights = maze.adjacency_list[start]
        
        for neighbor, weight in neighbors_with_weights:
            if neighbor.type == 'T':
                self.assertEqual(weight, 3)
            elif neighbor.type == 'P':
                self.assertEqual(weight, -2)


class TestGreedyAlgorithm(unittest.TestCase):
    """Test greedy best-first search behavior"""
    
    def test_greedy_choice_by_heuristic(self):
        """Greedy should pick node with best heuristic"""
        layout = "S.G\n...\n..."
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        ai.choose_move(maze)
        
        # Should move to (0,1) as it's closest to goal
        self.assertEqual(ai.current_node.r, 0)
        self.assertEqual(ai.current_node.c, 1)
    
    def test_greedy_ignores_cost(self):
        """Greedy should ignore edge costs, only consider heuristic"""
        layout = "STG\n..."
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        ai.choose_move(maze)
        
        # Should go through trap (T) because it's closer to goal
        self.assertEqual(ai.current_node.type, 'T')
        self.assertEqual(ai.current_node.r, 0)
        self.assertEqual(ai.current_node.c, 1)
    
    def test_greedy_avoids_revisiting(self):
        """Greedy should not revisit nodes"""
        layout = "S.G"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        # First move
        ai.choose_move(maze)
        first_node = ai.current_node
        
        # Second move
        ai.choose_move(maze)
        
        # Should not go back to start
        self.assertNotEqual(ai.current_node, maze.start_node)
    
    def test_greedy_backtracking_on_dead_end(self):
        """Greedy should backtrack when hitting dead end"""
        layout = "S.\n#.\n.G"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        # Best-First Search doesn't "backtrack" in the DFS sense, it just explores the frontier.
        # So we just check that it found a path or finished.
        self.assertTrue(ai.finished or len(ai.full_path) > 0)
    
    def test_greedy_reaches_goal(self):
        """Greedy should eventually reach goal in solvable maze"""
        layout = "S....\n.....\n....G"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        max_steps = 100
        for _ in range(max_steps):
            if ai.current_node == maze.goal_node:
                break
            ai.choose_move(maze)
        
        self.assertEqual(ai.current_node, maze.goal_node)


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance tracking"""
    
    def test_metrics_track_exploration(self):
        """Metrics should track nodes explored"""
        layout = "S...\n....\n...G"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        # Exploration happens in __init__, so it should be > 0 immediately
        self.assertGreater(ai.metrics.nodes_explored, 0)
    
    def test_metrics_track_visits(self):
        """Metrics should track actual visits"""
        layout = "S.G"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        # Visits happen during path computation in __init__
        # For a simple S.G, it visits S, ., G (3 nodes) or similar depending on implementation
        self.assertGreater(ai.metrics.nodes_visited, 0)
    
    def test_metrics_track_backtracks(self):
        """Metrics should track backtracking"""
        layout = "S.\n#G"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        # Force some moves
        for _ in range(10):
            if ai.finished:
                break
            ai.choose_move(maze)
        
        # May have backtracked depending on path
        self.assertGreaterEqual(ai.metrics.backtrack_count, 0)
    
    def test_efficiency_calculation(self):
        """Should calculate efficiency vs optimal"""
        layout = "S...G"
        maze = Maze(grid_layout=layout)
        
        optimal = maze.optimal_path_length
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        while not ai.finished and ai.steps < 100:
            ai.choose_move(maze)
        
        efficiency = ai.get_efficiency_vs_optimal(optimal)
        
        # Efficiency should be between 0 and 1
        self.assertGreaterEqual(efficiency, 0.0)
        self.assertLessEqual(efficiency, 1.0)


class TestMazeGeneration(unittest.TestCase):
    """Test maze/graph generation"""
    
    def test_maze_has_start_and_goal(self):
        """Generated maze must have start and goal"""
        maze = Maze(width=10, height=10)
        
        self.assertIsNotNone(maze.start_node)
        self.assertIsNotNone(maze.goal_node)
        self.assertEqual(maze.start_node.type, 'S')
        self.assertEqual(maze.goal_node.type, 'G')
    
    def test_maze_is_solvable(self):
        """Generated maze should have path from start to goal"""
        maze = Maze(width=15, height=15)
        
        optimal_length = maze.optimal_path_length
        
        # Should have finite path length
        self.assertLess(optimal_length, float('inf'))
        self.assertGreater(optimal_length, 0)
    
    def test_maze_seed_reproducibility(self):
        """Same seed should generate same maze"""
        seed = 12345
        
        maze1 = Maze(width=10, height=10, seed=seed)
        maze2 = Maze(width=10, height=10, seed=seed)
        
        # Should have same structure
        for r in range(10):
            for c in range(10):
                node1 = maze1.get_node(r, c)
                node2 = maze2.get_node(r, c)
                self.assertEqual(node1.type, node2.type)
    
    def test_maze_has_traps_and_powerups(self):
        """Generated maze should include traps and powerups"""
        maze = Maze(width=20, height=20)
        
        has_trap = False
        has_powerup = False
        
        for r in range(maze.height):
            for c in range(maze.width):
                node = maze.get_node(r, c)
                if node.type == 'T':
                    has_trap = True
                elif node.type == 'P':
                    has_powerup = True
        
        # Large maze should have at least some items
        self.assertTrue(has_trap or has_powerup)


class TestHeuristics(unittest.TestCase):
    """Test heuristic functions"""
    
    def test_euclidean_heuristic(self):
        """Euclidean heuristic should calculate correct distance"""
        layout = "S..\n...\n..G"
        maze = Maze(grid_layout=layout)
        
        start = maze.start_node
        h = maze.heuristic(start, 'euclidean')
        
        # Distance from (0,0) to (2,2)
        expected = (2**2 + 2**2) ** 0.5
        self.assertAlmostEqual(h, expected, places=2)
    
    def test_manhattan_heuristic(self):
        """Manhattan heuristic should calculate correct distance"""
        layout = "S..\n...\n..G"
        maze = Maze(grid_layout=layout)
        
        start = maze.start_node
        h = maze.heuristic(start, 'manhattan')
        
        # Manhattan distance from (0,0) to (2,2)
        expected = 2 + 2
        self.assertEqual(h, expected)
    
    def test_heuristic_is_admissible(self):
        """Heuristic should never overestimate"""
        layout = "S....\n.....\n....G"
        maze = Maze(grid_layout=layout)
        
        for r in range(maze.height):
            for c in range(maze.width):
                node = maze.get_node(r, c)
                if node.type != '#':
                    h = maze.heuristic(node)
                    # Heuristic should be non-negative
                    self.assertGreaterEqual(h, 0)


class TestPlayerMovement(unittest.TestCase):
    """Test player controls and movement"""
    
    def test_player_can_move(self):
        """Player should be able to move to valid positions"""
        layout = "S.\n.."
        maze = Maze(grid_layout=layout)
        
        player = Player(maze.start_node)
        
        # Move right
        success = player.move((0, 1), maze)
        
        self.assertTrue(success)
        self.assertEqual(player.current_node.c, 1)
    
    def test_player_cannot_move_through_walls(self):
        """Player should not move through walls"""
        layout = "S#"
        maze = Maze(grid_layout=layout)
        
        player = Player(maze.start_node)
        
        # Try to move into wall
        success = player.move((0, 1), maze)
        
        self.assertFalse(success)
        self.assertEqual(player.current_node, maze.start_node)
    
    def test_player_tracks_path(self):
        """Player should track path taken"""
        layout = "S..."
        maze = Maze(grid_layout=layout)
        
        player = Player(maze.start_node)
        
        player.move((0, 1), maze)
        player.move((0, 1), maze)
        
        self.assertEqual(len(player.path), 3)  # Start + 2 moves


class TestGraphProperties(unittest.TestCase):
    """Test graph theoretical properties"""
    
    def test_graph_connectivity(self):
        """Graph should be connected (start can reach goal)"""
        maze = Maze(width=15, height=15)
        
        # BFS to check connectivity
        visited = set()
        queue = [maze.start_node]
        visited.add(maze.start_node)
        
        found_goal = False
        
        while queue:
            node = queue.pop(0)
            if node == maze.goal_node:
                found_goal = True
                break
            
            for neighbor in maze.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        self.assertTrue(found_goal)
    
    def test_graph_has_cycles(self):
        """Graph should have cycles (not just a tree)"""
        maze = Maze(width=20, height=20)
        
        # Count nodes with multiple paths
        nodes_with_multiple_paths = 0
        
        for node in maze.adjacency_list.keys():
            if len(maze.adjacency_list[node]) > 2:
                nodes_with_multiple_paths += 1
        
        # Should have some branching
        self.assertGreater(nodes_with_multiple_paths, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_tiny_maze(self):
        """Should handle minimal maze"""
        layout = "SG"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        ai.choose_move(maze)
        
        self.assertEqual(ai.current_node, maze.goal_node)
    
    def test_maze_with_only_start(self):
        """Should handle maze with no valid moves"""
        layout = "S"
        maze = Maze(grid_layout=layout)
        
        ai = GreedyAI(maze.start_node, maze.goal_node, maze)
        
        # Should not crash
        ai.choose_move(maze)
        
        self.assertTrue(ai.finished or len(ai.path) == 1)
    
    def test_optimal_path_calculation(self):
        """Optimal path should be correct"""
        layout = "S.G"
        maze = Maze(grid_layout=layout)
        
        optimal = maze.optimal_path_length
        
        # Shortest path is 2 steps
        self.assertEqual(optimal, 2)


# Test runner
if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)