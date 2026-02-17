import sys
import unittest
from game_classes import Maze, Node
from region_logic import RegionLogic

class TestRegionLogic(unittest.TestCase):
    def setUp(self):
        # Create a simple maze with a known articulation point
        # #######
        # #...#.#  <- Region 1
        # #.#.#.#
        # #.A...#  <- A is Articulation Point (3,2) connecting left and right
        # #######
        
        # Actually let's manually construct a grid where (2,2) is an AP
        # 01234
        # ..... 0
        # .###. 1
        # ..A.. 2  <- A(2,2)
        # .###. 3
        # ..... 4
        
        # If A is removed, top and bottom are disconnected (if we block sides)
        
        self.maze = Maze(width=10, height=10)
        # Clear maze to empty
        for r in range(10):
            for c in range(10):
                self.maze.grid[r][c].type = '.'
                
        # Build 2 rooms connected by a single corridor
        # Room 1: (1,1) to (3,3)
        # Room 2: (1,7) to (3,9)
        # Corridor: (2,4), (2,5), (2,6)
        
        # Block everything
        for r in range(10):
            for c in range(10):
                self.maze.grid[r][c].type = '#'
                
        # Room 1
        for r in range(1, 4):
            for c in range(1, 4):
                self.maze.grid[r][c].type = '.'
                
        # Room 2
        for r in range(1, 4):
            for c in range(7, 10):
                self.maze.grid[r][c].type = '.'
                
        # Corridor
        self.maze.grid[2][4].type = '.'
        self.maze.grid[2][5].type = '.'
        self.maze.grid[2][6].type = '.'
        
        # So structure is:
        # ##########
        # #...###...#
        # #...-.-...#  <- Corridor at 2,4 - 2,5 - 2,6
        # #...###...#
        # ##########
        
        # Bridges should be at (2,4) and (2,6) potentially, or any node on the single path.
        # Ideally, removing (2,5) splits the graph. So (2,5) is an AP.
        
    def test_articulation_points(self):
        aps = RegionLogic.compute_articulation_points(self.maze)
        print(f"\nFound {len(aps)} APs: {[ (n.r, n.c) for n in aps ]}")
        
        # (2,5) must be an AP
        ap_node = self.maze.grid[2][5]
        self.assertIn(ap_node, aps, "Middle of corridor (2,5) should be an AP")
        
        # (2,4) and (2,6) might also be APs depending on definition (yes they are)
        
    def test_region_partition(self):
        aps = RegionLogic.compute_articulation_points(self.maze)
        regions_map, region_graph, regions_by_id = RegionLogic.compute_regions(self.maze, aps)
        
        print(f"Found {len(regions_by_id)} Regions.")
        for rid, nodes in regions_by_id.items():
            print(f"Region {rid}: {len(nodes)} nodes")
            
        # We expect at least 2 regions (Room 1 and Room 2), maybe 3 if the corridor splits
        # If (2,5) is AP and barrier:
        # Room 1 + (2,4) = Region A
        # Room 2 + (2,6) = Region B
        # (2,5) is barrier.
        
        self.assertGreater(len(regions_by_id), 1, "Maze should be split into multiple regions!")
        
if __name__ == '__main__':
    unittest.main()