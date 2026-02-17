import random
import time
from collections import deque, defaultdict
from game_classes import Maze, Node
from region_logic import RegionLogic

class DynamicMaze(Maze):
    """
    A maze that changes over time (Harry Potter style).
    Implements Tarjan's Algorithm for structural analysis and region-based navigation.
    """
    def __init__(self, grid_layout=None, width=10, height=10, seed=None):
        super().__init__(grid_layout, width, height, seed)
        
        self.articulation_points = set()
        self.regions = {}  # node -> region_id
        self.region_list = [] # List of sets of nodes
        self.region_connectivity = defaultdict(set) # region_id -> set of connected region_ids
        
        self.last_update_time = time.time()
        self.update_interval = 4.0  # Slower updates to allow for animation time
        self.last_event_description = "Maze Stable"
        self.last_event_node = None
        self.pending_changes = []
        self.recent_edge_changes = [] # (node, type, timer) for graph animation
        
        # Initial Analysis
        self.analyze_structure()

    # ... (skipping methods) ...

    def process_updates(self, dt):
        """
        Advances animation timers and applies changes when ready.
        Returns True if a structural change happened (requires re-pathing).
        """
        structure_changed = False
        remaining_changes = []
        
        # Update edge animation timers
        self.recent_edge_changes = [
            (n, t, timer - dt) 
            for n, t, timer in self.recent_edge_changes 
            if timer - dt > 0
        ]
        
        for change in self.pending_changes:
            change['timer'] -= dt
            
            if change['state'] == 'WARNING':
                if change['timer'] <= 0:
                    change['state'] = 'ANIMATING'
                    change['timer'] = change['anim_duration']
                remaining_changes.append(change)
                
            elif change['state'] == 'ANIMATING':
                if change['timer'] <= 0:
                    # Apply Change
                    node = change['node']
                    if change['type'] == 'ADD_WALL':
                        node.type = '#'
                        node.cost = float('inf')
                        # Edge Removed (technically edges to neighbors are removed)
                        self.recent_edge_changes.append((node, 'REMOVE', 1.0)) 
                    elif change['type'] == 'REMOVE_WALL':
                        node.type = '.'
                        node.cost = 1
                        # Edge Added
                        self.recent_edge_changes.append((node, 'ADD', 1.0))
                    
                    structure_changed = True
                else:
                    remaining_changes.append(change)
        
        self.pending_changes = remaining_changes
        
        if structure_changed:
            self.analyze_structure()
            
        return structure_changed

    def is_node_unstable(self, node):
        """Returns True if node is about to become a wall (WARNING phase)."""
        for change in self.pending_changes:
            if change['node'] == node and change['state'] == 'WARNING' and change['type'] in ('ADD_WALL', 'SHIFT'):
                return True
        return False
        
    def analyze_structure(self):
        """Full structural analysis: Articulation Points + Regions"""
        # print("Re-analyzing Maze Structure...")
        self.build_graph() # Rebuild adjacency list first
        
        # Use centralized logic
        self.articulation_points = RegionLogic.compute_articulation_points(self)
        self.regions, self.region_connectivity, self.region_list_map = RegionLogic.compute_regions(self, self.articulation_points)
        
        # Compatibility adapter for existing code that uses list of sets
        self.region_list = []
        # Sort by region ID to ensure consistent order if needed, though region_id is just a key
        sorted_ids = sorted(self.region_list_map.keys())
        for rid in sorted_ids:
            self.region_list.append(set(self.region_list_map[rid]))

        # print(f"Analysis Complete. Found {len(self.articulation_points)} Articulation Points.")

    # find_articulation_points, partition_regions, and build_region_connectivity are now removed 
    # as they are handled by RegionLogic

    def update_structure(self):
        """
        Called every frame. Checks if it's time to queue a dynamic event.
        """
        current_time = time.time()
        if current_time - self.last_update_time > self.update_interval:
            self.queue_dynamic_event()
            self.last_update_time = current_time
            # Randomize next interval (3s to 8s)
            self.update_interval = random.uniform(3.0, 8.0)

    def queue_dynamic_event(self):
        """
        Queues a random wall add/remove/shift event with warning phase.
        """
        event_type = random.choice(['ADD', 'REMOVE', 'SHIFT', 'MASS'])
        width, height = self.width, self.height
        
        # Helper to get valid node
        def get_random_node(type_filter=None):
            for _ in range(10):
                r = random.randint(1, height - 2)
                c = random.randint(1, width - 2)
                node = self.grid[r][c]
                if node in (self.start_node, self.goal_node): continue
                if type_filter and node.type != type_filter: continue
                return node
            return None

        if event_type == 'ADD':
            node = get_random_node('.')
            if node:
                self.schedule_change(node, 'ADD_WALL', "Magic Gathering...", 2.0)
                
        elif event_type == 'REMOVE':
            # Try to find a wall with open neighbors
            for _ in range(10):
                node = get_random_node('#')
                if node:
                    open_neighbors = sum(1 for n in self.get_neighbors(node))
                    if open_neighbors >= 1:
                        self.schedule_change(node, 'REMOVE_WALL', "Ancient Seals Weakening...", 2.0)
                        break
                        
        elif event_type == 'SHIFT':
            # Move a wall to a neighbor
            node = get_random_node('#')
            if node:
                # Find an open neighbor
                neighbors = [n for n in self.get_neighbors(node) if n.type == '.' and n not in (self.start_node, self.goal_node)]
                if neighbors:
                    target = random.choice(neighbors)
                    # Sequence: Remove old wall, Add new wall
                    self.schedule_change(node, 'REMOVE_WALL', "Wall Shifting...", 1.5)
                    self.schedule_change(target, 'ADD_WALL', "Wall Shifting...", 1.5)
                    
        elif event_type == 'MASS':
            # Trigger multiple events
            count = random.randint(2, 4)
            self.last_event_description = "CHAOS SURGE!"
            for _ in range(count):
                if random.random() < 0.5:
                    node = get_random_node('.')
                    if node: self.schedule_change(node, 'ADD_WALL', "Chaos Surge!", 1.0)
                else:
                    node = get_random_node('#')
                    if node: self.schedule_change(node, 'REMOVE_WALL', "Chaos Surge!", 1.0)

    def schedule_change(self, node, type, desc, duration):
        self.pending_changes.append({
            'node': node,
            'type': type,
            'state': 'WARNING',
            'timer': 1.0, # Fast warning (1s)
            'anim_duration': random.uniform(0.5, 1.5), # Fast animation
            'total_duration': duration
        })
        self.last_event_description = desc
        self.last_event_node = node

    def process_updates(self, dt):
        """
        Advances animation timers and applies changes when ready.
        Returns True if a structural change happened (requires re-pathing).
        """
        structure_changed = False
        remaining_changes = []
        
        for change in self.pending_changes:
            change['timer'] -= dt
            
            if change['state'] == 'WARNING':
                if change['timer'] <= 0:
                    change['state'] = 'ANIMATING'
                    change['timer'] = change['anim_duration']
                remaining_changes.append(change)
                
            elif change['state'] == 'ANIMATING':
                if change['timer'] <= 0:
                    # Apply Change
                    node = change['node']
                    if change['type'] == 'ADD_WALL':
                        node.type = '#'
                        node.cost = float('inf')
                    elif change['type'] == 'REMOVE_WALL':
                        node.type = '.'
                        node.cost = 1
                    
                    structure_changed = True
                else:
                    remaining_changes.append(change)
        
        self.pending_changes = remaining_changes
        
        if structure_changed:
            self.analyze_structure()
            
        return structure_changed