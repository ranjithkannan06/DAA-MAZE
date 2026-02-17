import math
import random
from collections import deque

class CircularNode:
    """Node in a polar coordinate system with edge-based walls."""
    def __init__(self, ring, sector, cost=1):
        self.r = ring    # Ring Index (0=Center, 1=Inner... N-1=Outer)
        self.c = sector  # Sector Index (0..Sectors-1)
        self.cost = cost
        self.type = '.' # Default type (for compatibility with existing rendering checks)
        
        # Walls: True = blocked, False = open
        # 'cw': Wall between (r, c) and (r, (c+1)%S)
        # 'in': Wall between (r, c) and (r-1, any aligned) - Owned by Outer Ring logic
        self.walls = {'cw': True, 'in': True}
        
        # DP State Visualization
        self.dp_cost = float('inf')
        self.best_action = None 
        
        # Compatibility Attributes
        self.times_evaluated = 0
        self.visited_by_ai = False
        self.visited_by_player = False
        self.neighbors = {} 

    def __repr__(self):
        return f"Node(R{self.r}, S{self.c})"

    def __lt__(self, other):
        return self.dp_cost < other.dp_cost

class RingConfig:
    def __init__(self, sectors, speed):
        self.sectors = sectors
        self.speed = speed # Sectors per second (float)

class CircularMaze:
    """
    Rotating Circular Labyrinth with independent ring physics.
    Uses Recursive Backtracker for guaranteed connectivity.
    """
    def __init__(self, num_rings=6, sectors=24):
        self.num_rings = num_rings
        self.sectors_per_ring = sectors
        
        self.rings = []
        self.grid = [] # [ring][sector] -> Node
        self.offsets = [0.0] * num_rings 
        
        # Speeds: Alternating directions and varying magnitudes
        self.ring_configs = []
        for i in range(num_rings):
            speed = 0.0
            if i > 0: # Center is static
                # Outer rings move faster? Or inner? Let's mix.
                # Alternating CW/CCW
                direction = 1 if i % 2 == 0 else -1
                speed = (0.05 + (i * 0.02)) * direction 
            self.ring_configs.append(RingConfig(sectors, speed))
            
        self.generate_grid()
        self.generate_maze_structure()
        
        # Center is a single special node (not part of grid)
        self.center_node = CircularNode(0, 0)
        self.center_node.type = 'G'
        
        # Start at Outer Ring, sector 0
        self.start_node = self.grid[num_rings-1][0]
        self.start_node.type = 'S'
        self.goal_node = self.center_node  # Center is the goal
        self.optimal_path_length = 0
        
        # Compatibility
        self.width = sectors
        self.height = num_rings
        
    def generate_grid(self):
        """Generate polar grid. Ring 0 is special center node, rings 1...N-1 are in grid."""
        self.grid = []
        for r in range(self.num_rings):
            row = []
            for s in range(self.sectors_per_ring):
                node = CircularNode(r, s)
                row.append(node)
            self.grid.append(row)

    def generate_maze_structure(self):
        """
        Recursive Backtracker to generate valid labyrinth.
        Starts from Center (0,0) and carves out.
        """
        # Reset walls to all True (already default)
        
        stack = []
        visited = set()
        
        # Start from ring 1 (first actual ring, since ring 0 is single center node)
        start_sector = random.randint(0, self.sectors_per_ring - 1)
        start = self.grid[1][start_sector]
        visited.add((1, start_sector))
        stack.append(start)
        
        while stack:
            current = stack[-1]
            r, c = current.r, current.c
            
            # Get unvisited neighbors (static connectivity for generation)
            # We assume static alignment (offset=0) for generation
            candidates = []
            
            # 1. CW
            n_cw = self.grid[r][(c + 1) % self.sectors_per_ring]
            if (n_cw.r, n_cw.c) not in visited:
                candidates.append(('cw', n_cw))
                
            # 2. CCW
            n_ccw = self.grid[r][(c - 1) % self.sectors_per_ring]
            if (n_ccw.r, n_ccw.c) not in visited:
                candidates.append(('ccw', n_ccw))
                
            # 3. Out (r -> r+1)
            if r < self.num_rings - 1:
                n_out = self.grid[r+1][c] # Assume aligned at start
                if (n_out.r, n_out.c) not in visited:
                    candidates.append(('out', n_out))
                    
            # 4. In (r -> r-1) - stop at ring 1 (center is separate node)
            if r > 1:
                n_in = self.grid[r-1][c] # Assume aligned at start
                if (n_in.r, n_in.c) not in visited:
                    candidates.append(('in', n_in))
            
            if candidates:
                # Choose random neighbor
                direction, next_node = random.choice(candidates)
                
                # Remove wall
                if direction == 'cw':
                    current.walls['cw'] = False # Wall is on current (r,c) facing CW
                elif direction == 'ccw':
                    next_node.walls['cw'] = False # Wall is on neighbor (r, c-1) facing CW
                elif direction == 'in':
                    current.walls['in'] = False # Wall on current (r,c) facing In
                elif direction == 'out':
                    next_node.walls['in'] = False # Wall on neighbor (r+1, c) facing In
                
                visited.add((next_node.r, next_node.c))
                stack.append(next_node)
            else:
                stack.pop()
                
        # Create entry points to center from ring 1
        # Open at least one 'in' wall on ring 1 to allow access to center
        num_entries = random.randint(1, min(3, self.sectors_per_ring // 4))  # 1-3 entries
        entry_sectors = random.sample(range(self.sectors_per_ring), num_entries)
        for sector in entry_sectors:
            self.grid[1][sector].walls['in'] = False  # Open path to center
        
        # Open the 'in' wall for center to ensure it's accessible from any angle?
        # Actually recursive backtracker guarantees one path. 
        # But rotation might break it?
        # If we carve based on static alignment, rotation effectively "shifts" the maze.
        # Since r=0 is static and r=1 rotates, the connection (1, s) -> (0, 0)
        # depends on alignment.
        # Ideally, center (0,0) should be open from all sides or have no 'in' walls on ring 1?
        # Let's keep it simple: generation guarantees distinct structure.
        
        # Post-processing: Add some loops (remove random walls)
        # to make it less of a perfect tree and more of a maze with options
        for _ in range(int(self.num_rings * self.sectors_per_ring * 0.1)):
            r = random.randint(0, self.num_rings - 1)
            c = random.randint(0, self.sectors_per_ring - 1)
            node = self.grid[r][c]
            # Randomly open a wall
            if random.random() > 0.5:
                node.walls['cw'] = False
            elif r > 0 and random.random() > 0.5:
                node.walls['in'] = False

    def update(self, dt):
        """Update rotation physics"""
        for i in range(1, self.num_rings): # Skip center
            speed = self.ring_configs[i].speed
            self.offsets[i] = (self.offsets[i] + speed * dt) % self.sectors_per_ring

    def get_node(self, r, c):
        if 0 <= r < self.num_rings:
            return self.grid[r][c % self.sectors_per_ring]
        return None

    def get_weighted_neighbors(self, node, future_time=0.0):
        """
        Get valid moves based on Walls and Dynamic Alignment.
        """
        neighbors = []
        r, c = node.r, node.c
        S = self.sectors_per_ring
        current_node = self.grid[r][c]
        
        # 1. Intra-Ring (CW/CCW)
        # Check walls['cw'] of current and neighbor
        
        # CW Neighbor (r, c+1)
        # Path exists if current.walls['cw'] is False
        if not current_node.walls['cw']:
            n_cw = self.grid[r][(c + 1) % S]
            neighbors.append((n_cw, 1))
            
        # CCW Neighbor (r, c-1)
        # Path exists if neighbor.walls['cw'] is False
        n_ccw = self.grid[r][(c - 1) % S]
        if not n_ccw.walls['cw']:
            neighbors.append((n_ccw, 1))
            
        # 2. Inter-Ring (In/Out)
        # Depends on Alignment + Walls['in']
        
        # Inner (r -> r-1)
        if r > 0:
            # We want to move from (r, c) to (r-1, ?).
            # This is blocked if current_node.walls['in'] is True.
            # CRITICAL: walls['in'] rotates with the ring!
            # But 'node' is the logical grid slot. 
            # So if self.grid[r][c] has a wall, it rotates with sector c.
            
            if not current_node.walls['in']:
                if r == 1:
                    # Ring 1 connects directly to center (single node)
                    neighbors.append((self.center_node, 1))
                else:
                    # Wall is open. Now check alignment.
                    # Global Angle R = (c + offset_r)
                    # Global Angle R-1 = (s_in + offset_r-1)
                    
                    off_r = (self.offsets[r] + self.ring_configs[r].speed * future_time)
                    global_angle_r = (c + off_r) % S
                    
                    off_inner = (self.offsets[r-1] + self.ring_configs[r-1].speed * future_time)
                    
                    s_in_float = (global_angle_r - off_inner) % S
                    s_in = round(s_in_float) % S
                    
                    diff = abs(s_in - s_in_float)
                    if diff > 0.5: diff = 1.0 - diff 
                    
                    if diff < 0.4: # Aligned
                        target = self.grid[r-1][s_in]
                        neighbors.append((target, 1))

        # Outer (r -> r+1)
        if r < self.num_rings - 1:
            # We want to move from (r, c) to (r+1, ?).
            # This depends on the TARGET's 'in' wall.
            # We need to find which sector on r+1 is aligned with us.
            
            off_r = (self.offsets[r] + self.ring_configs[r].speed * future_time)
            global_angle_r = (c + off_r) % S
            
            off_outer = (self.offsets[r+1] + self.ring_configs[r+1].speed * future_time)
            
            s_out_float = (global_angle_r - off_outer) % S
            s_out = round(s_out_float) % S
            
            diff = abs(s_out - s_out_float)
            if diff > 0.5: diff = 1.0 - diff
            
            if diff < 0.4:
                 target = self.grid[r+1][s_out]
                 # Valid if target does NOT have an inner wall
                 if not target.walls['in']:
                     neighbors.append((target, 1))

        return neighbors

    def get_neighbors(self, node):
        weighted = self.get_weighted_neighbors(node, future_time=0.0)
        return [n for n, cost in weighted]

    def get_movement_target(self, node, direction):
        dr, dc = direction
        target_r = node.r + dr
        
        # Intra-ring
        if dr == 0:
            target_c = (node.c + dc) % self.sectors_per_ring
            target = self.grid[node.r][target_c]
            
            # check connectivity using get_neighbors logic 
            # (simpler: just check if target is in neighbors)
            # This handles the wall checks
            nbs = self.get_neighbors(node)
            if target in nbs:
                return target
            return None
            
        # Inter-ring
        neighbors = self.get_weighted_neighbors(node)
        for n, cost in neighbors:
            if n.r == target_r:
                return n
        return None

    def run_dp(self):
        """Time-Expanded DP (Optimized)"""
        T = 15 
        values = {}
        
        # Base cases
        for t in range(T + 1):
             for s in range(self.sectors_per_ring):
                 values[(t, 0, s)] = 0
        
        # Fill heuristic
        for r in range(1, self.num_rings):
            for s in range(self.sectors_per_ring):
                values[(T, r, s)] = r * 2
                
        # Backwards Induction
        for t in range(T - 1, -1, -1):
            for r in range(1, self.num_rings):
                for s in range(self.sectors_per_ring):
                    node = self.grid[r][s]
                    
                    wait_cost = 1 + values.get((t+1, r, s), float('inf'))
                    
                    move_costs = []
                    for neigh, cost in self.get_weighted_neighbors(node, future_time=t*1.0):
                         val = cost + values.get((t+1, neigh.r, neigh.c), float('inf'))
                         move_costs.append(val)
                    
                    best = min(wait_cost, min(move_costs) if move_costs else float('inf'))
                    values[(t, r, s)] = best
                    
        for r in range(self.num_rings):
            for s in range(self.sectors_per_ring):
                self.grid[r][s].dp_cost = values.get((0, r, s), float('inf'))
                
    # Compatibility Methods
    def bfs_analysis(self): pass
    def generate_heuristic_map(self): pass
    def a_star_optimal(self):
        """Return DP cost from start"""
        # Run DP once to populate
        self.run_dp()
        self.optimal_path_length = self.start_node.dp_cost
        return self.optimal_path_length

    def get_screen_pos(self, node, screen_size):
        """
        Convert logical Node(r, c) to screen coordinates (x, y).
        Aligns perfectly with draw_circular_maze.
        """
        w, h = screen_size
        cx, cy = w // 2, h // 2 + 30 
        
        # Consistent radius calculation with draw_circular_maze
        max_radius = min(w, h) // 2 - 50
        num_rings = self.num_rings
        ring_step = max_radius // (num_rings + 0.5)
        
        pr, pc = node.r, node.c
        S = self.sectors_per_ring
        
        # Calculate Angle
        # Player rotates with the ring!
        angle_step = 360 / S
        
        # Current ring offset (in sectors)
        offset_sectors = self.offsets[pr]
        
        # Total angle in degrees (0 is Top for calculation here? or follow draw logic?)
        # Main.py logic:
        # start_deg = -90 + (s * angle_step) + (offset * angle_step)
        # center of sector = start_deg + angle_step/2
        
        sector_center_deg = -90 + (pc * angle_step) + (offset_sectors * angle_step) + (angle_step / 2)
        p_rad = math.radians(sector_center_deg)
        
        # Radius: Center of the ring band
        p_dist = (pr * ring_step) + (ring_step / 2)
        
        px = cx + math.cos(p_rad) * p_dist
        py = cy + math.sin(p_rad) * p_dist
        
        return int(px), int(py)
