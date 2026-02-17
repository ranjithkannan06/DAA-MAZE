import pygame
import time

class TarjanVisualizer:
    def __init__(self, maze):
        self.maze = maze
        self.reset()
        
    def reset(self):
        self.visited = set()
        self.discovery_time = {}
        self.low_link = {}
        self.parent = {}
        self.articulation_points = set()
        self.time = 0
        self.stack = [] # For DFS logic
        self.path_stack = [] # For visual path
        
        # Generator for step-by-step execution
        self.generator = self.run_tarjan()
        self.finished = False
        self.current_node = None
        self.status_text = "Starting Tarjan's Algorithm..."
        
    def run_tarjan(self):
        # Scan entire grid to ensure we cover all disconnected components
        height, width = self.maze.height, self.maze.width
        
        for r in range(height):
            for c in range(width):
                start_node = self.maze.grid[r][c]
                if start_node.type == '#' or start_node in self.visited:
                    continue
                    
                # New Component Found
                self.visited.add(start_node)
                self.discovery_time[start_node] = self.low_link[start_node] = self.time
                self.time += 1
                self.path_stack.append(start_node)
                
                # Stack for iterative DFS: (u, parent, neighbors_iterator)
                stack = [(start_node, None, iter(self.maze.get_neighbors(start_node)))]
                children = 0 # Child count for the current component root
                
                yield "VISIT", start_node
                
                while stack:
                    u, p, neighbors = stack[-1]
                    self.current_node = u
                    
                    try:
                        v = next(neighbors)
                        
                        if v == p:
                            continue
                        
                        if v in self.visited:
                            # Back-edge
                            self.low_link[u] = min(self.low_link[u], self.discovery_time[v])
                            yield "BACK_EDGE", v
                        else:
                            # Tree-edge
                            self.parent[v] = u
                            self.visited.add(v)
                            self.discovery_time[v] = self.low_link[v] = self.time
                            self.time += 1
                            self.path_stack.append(v)
                            
                            # Increment root children count if u is root
                            if u == start_node:
                                children += 1
                                
                            yield "VISIT", v
                            stack.append((v, u, iter(self.maze.get_neighbors(v))))
                    
                    except StopIteration:
                        # Finished processing u
                        stack.pop()
                        if self.path_stack: self.path_stack.pop()
                        
                        if p is not None:
                            # Propagate low_link up
                            self.low_link[p] = min(self.low_link[p], self.low_link[u])
                            
                            # Check AP condition for p
                            if self.low_link[u] >= self.discovery_time[p]:
                                # p is an AP unless it's root (handled separately)
                                if p != start_node:
                                    self.articulation_points.add(p)
                                    yield "FOUND_AP", p
                            
                            yield "BACKTRACK", p
                
                # Component Root Logic
                if children > 1:
                    self.articulation_points.add(start_node)
                    yield "FOUND_AP", start_node

        self.finished = True
        yield "DONE", None

    def step(self):
        if self.finished: return
        try:
            event, node = next(self.generator)
            if event == "VISIT":
                self.status_text = f"Visiting ({node.r}, {node.c})"
            elif event == "BACK_EDGE":
                pass # Too fast
            elif event == "FOUND_AP":
                self.status_text = f"Articulation Point Correctly Identified! ({node.r}, {node.c})"
            elif event == "BACKTRACK":
                pass
            elif event == "DONE":
                self.status_text = f"Tarjan's Complete. Found {len(self.articulation_points)} APs."
        except StopIteration:
            self.finished = True

    def draw(self, screen, TILE_SIZE, OFFSET_Y, font):
        # Draw all visited grid
        for node in self.visited:
            rect = pygame.Rect(node.c*TILE_SIZE, node.r*TILE_SIZE+OFFSET_Y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (50, 50, 60), rect) # Gray visited
            
        # Draw Stack Path (Current DFS branch)
        if len(self.path_stack) > 1:
            points = [(n.c * TILE_SIZE + TILE_SIZE//2, n.r * TILE_SIZE + TILE_SIZE//2 + OFFSET_Y) for n in self.path_stack]
            pygame.draw.lines(screen, (0, 100, 255), False, points, 3)

        # Draw Current Node
        if self.current_node:
            rect = pygame.Rect(self.current_node.c*TILE_SIZE, self.current_node.r*TILE_SIZE+OFFSET_Y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (0, 255, 255), rect, 3) # Cyan Highlight

        # Draw Articulation Points
        for node in self.articulation_points:
            cx, cy = node.c * TILE_SIZE + TILE_SIZE//2, node.r * TILE_SIZE + TILE_SIZE//2 + OFFSET_Y
            pygame.draw.circle(screen, (255, 0, 0), (cx, cy), TILE_SIZE//3)
            
        # Draw Status
        txt = font.render(self.status_text, True, (255, 255, 255))
        screen.blit(txt, (20, 10))


class RegionVisualizer:
    def __init__(self, maze, articulation_points):
        self.maze = maze
        self.articulation_points = articulation_points
        self.reset()
        
    def reset(self):
        self.regions = {} # node -> region_id
        self.regions_by_id = {} # region_id -> list[mode]
        self.region_colors = {} # region_id -> color_index
        self.region_graph = {} # region_id -> set(connected_region_ids)
        self.ap_connections = {ap: set() for ap in self.articulation_points} # ap -> set(region_ids)
        
        self.region_id = 0
        self.visited = set() # Standard visited for flood fill
        
        self.generator = self.run_flood_fill()
        self.finished = False
        self.status_text = "Starting Region Partitioning..."

    def run_flood_fill(self):
        # Iterate all nodes to ensure full partition
        height, width = self.maze.height, self.maze.width
        
        # High Contrast Color Palette (Green, Purple, Cyan, Yellow, Blue...)
        colors = [
            (0, 255, 0),    # Green
            (160, 32, 240), # Purple
            (0, 255, 255),  # Cyan
            (255, 255, 0),  # Yellow
            (0, 0, 255),    # Blue
            (255, 0, 0),    # Red (Reserved for APs, but used here for variety if needed, preferably skip)
            (255, 0, 255),  # Magenta
            (255, 165, 0),  # Orange
            (0, 128, 0),    # Dark Green
            (75, 0, 130),   # Indigo
        ]
        
        # We process every single non-wall, non-AP node
        for r in range(height):
            for c in range(width):
                node = self.maze.grid[r][c]
                
                # IF node is Wall OR already visited OR is an Articulation Point: Skip
                if node.type == '#' or node in self.visited or node in self.articulation_points:
                    continue
                    
                # === START NEW REGION ===
                self.region_id += 1
                self.region_graph[self.region_id] = set()
                self.region_colors[self.region_id] = (self.region_id - 1) % len(colors)
                self.regions_by_id[self.region_id] = []
                
                yield "NEW_REGION", (node, self.region_id)
                
                queue = [node]
                self.visited.add(node)
                self.regions[node] = self.region_id
                self.regions_by_id[self.region_id].append(node)
                
                while queue:
                    u = queue.pop(0)
                    
                    for v in self.maze.get_neighbors(u):
                        if v.type == '#': continue
                        
                        # CRITICAL: If neighbor is AP, it is a BRIDGE.
                        # Do NOT add to queue (do not cross).
                        # Just record the connection.
                        if v in self.articulation_points:
                            self.ap_connections[v].add(self.region_id)
                            continue
                            
                        # Standard Flood Fill
                        if v not in self.visited:
                            self.visited.add(v)
                            self.regions[v] = self.region_id
                            self.regions_by_id[self.region_id].append(v)
                            queue.append(v)
                            yield "FILL", v
                            
        # Post-Processing: Build Region Graph (Region <-> Region)
        # Two regions are connected if they both touch the SAME AP.
        for ap, rids in self.ap_connections.items():
            rids_list = list(rids)
            for i in range(len(rids_list)):
                for j in range(i+1, len(rids_list)):
                    r1, r2 = rids_list[i], rids_list[j]
                    self.region_graph[r1].add(r2)
                    self.region_graph[r2].add(r1)

        self.finished = True
        yield "DONE", None

    def step(self):
        if self.finished: return
        try:
            event, data = next(self.generator)
            if event == "NEW_REGION":
                node, rid = data
                self.status_text = f"Partitioning Zone {rid}..."
            elif event == "FILL":
                pass # Too fast to update text every tile
            elif event == "DONE":
                self.status_text = "Region Partition Complete. Generating Graph..."
        except StopIteration:
            self.finished = True

    def draw(self, screen, TILE_SIZE, OFFSET_Y, font):
        colors = [
            (0, 255, 0),    # Green
            (160, 32, 240), # Purple
            (0, 255, 255),  # Cyan
            (255, 255, 0),  # Yellow
            (0, 0, 255),    # Blue
            (255, 0, 0),    # Red
            (255, 0, 255),  # Magenta
            (255, 165, 0),  # Orange
            (0, 128, 0),    # Dark Green
            (75, 0, 130),   # Indigo
        ]
        
        # 1. Draw Regions
        for node, rid in self.regions.items():
            color_idx = self.region_colors.get(rid, 0)
            color = colors[color_idx]
            
            x, y = node.c * TILE_SIZE, node.r * TILE_SIZE + OFFSET_Y
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            
            # Solid color with transparency
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((*color, 150)) 
            screen.blit(s, rect)
            
        # 2. Draw Region Graph (White Lines)
        centroids = {}
        for rid, node_list in self.regions_by_id.items():
            if not node_list: continue
            avg_r = sum(n.r for n in node_list) / len(node_list)
            avg_c = sum(n.c for n in node_list) / len(node_list)
            centroids[rid] = (
                avg_c * TILE_SIZE + TILE_SIZE//2, 
                avg_r * TILE_SIZE + TILE_SIZE//2 + OFFSET_Y
            )
        
        # Connections
        for r1, connected_rids in self.region_graph.items():
            if r1 not in centroids: continue
            for r2 in connected_rids:
                if r2 in centroids and r1 < r2: # Draw once
                    pygame.draw.line(screen, (255, 255, 255), centroids[r1], centroids[r2], 2)

        # 3. Draw Articulation Points (Red Diamonds)
        for node in self.articulation_points:
             cx, cy = node.c * TILE_SIZE + TILE_SIZE//2, node.r * TILE_SIZE + TILE_SIZE//2 + OFFSET_Y
             
             # Diamond Shape
             pts = [
                 (cx, cy - TILE_SIZE//2.5),
                 (cx + TILE_SIZE//2.5, cy),
                 (cx, cy + TILE_SIZE//2.5),
                 (cx - TILE_SIZE//2.5, cy)
             ]
             pygame.draw.polygon(screen, (255, 0, 0), pts) # Red Fill
             pygame.draw.polygon(screen, (255, 255, 255), pts, 1) # White Border
             
        txt = font.render(self.status_text, True, (255, 255, 255))
        screen.blit(txt, (20, 40))


class ConquerVisualizer:
    def __init__(self, maze, hierarchical_ai_class):
        self.maze = maze
        self.HierarchicalAI = hierarchical_ai_class
        self.reset()
        
    def reset(self):
        self.start_node = self.maze.start_node
        self.goal_node = self.maze.goal_node
        self.agent = self.HierarchicalAI(self.start_node, self.goal_node, self.maze)
        self.status_text = "Starting High-Level Conquest..."
        self.finished = False
        self.plan_visible = False
        self.current_step_idx = 0
        self.plan_path = []
        
        self.generator = self.run_conquer()
        
    def run_conquer(self):
        # 1. Build Graph
        yield "BUILDING_GRAPH", None
        # Force re-analysis ensuring regions exist
        from region_logic import RegionLogic
        self.maze.articulation_points = RegionLogic.compute_articulation_points(self.maze)
        self.maze.regions, self.maze.region_connectivity, self.maze.regions_by_id = RegionLogic.compute_regions(self.maze, self.maze.articulation_points)
        
        self.agent.compute_path() # This builds the high-level plan
        self.plan_path = self.agent.high_level_plan
        
        yield "GRAPH_BUILT", len(self.plan_path)
        
        if not self.plan_path:
            yield "NO_PLAN", None
            return

        # 2. Animate Plan Step-by-Step
        for i, item in enumerate(self.plan_path):
            self.current_step_idx = i
            yield "PLAN_STEP", item
            # time.sleep(0.5) # Handled by main loop stepping
        
        self.finished = True
        yield "DONE", None
        
    def step(self):
        if self.finished: return
        try:
            event, data = next(self.generator)
            if event == "BUILDING_GRAPH":
                self.status_text = "Building Augmented Graph (Regions + Bridges)..."
            elif event == "GRAPH_BUILT":
                self.status_text = f"High-Level Plan Found! {data} Steps."
                self.plan_visible = True
            elif event == "PLAN_STEP":
                self.status_text = f"Conquering Step {self.current_step_idx+1}/{len(self.plan_path)}: {data}"
            elif event == "NO_PLAN":
                self.status_text = "No High-Level Plan Possible."
                self.finished = True
            elif event == "DONE":
                self.status_text = "Conquer Phase Complete. Ready to execute."
        except StopIteration:
            self.finished = True

    def draw(self, screen, TILE_SIZE, OFFSET_Y, font):
        # Match RegionVisualizer Palette
        colors = [
            (0, 255, 0),    # Green
            (160, 32, 240), # Purple
            (0, 255, 255),  # Cyan
            (255, 255, 0),  # Yellow
            (0, 0, 255),    # Blue
            (255, 0, 0),    # Red
            (255, 0, 255),  # Magenta
            (255, 165, 0),  # Orange
            (0, 128, 0),    # Dark Green
            (75, 0, 130),   # Indigo
        ]
        
        # 1. Draw Background Regions (Dimmed)
        if hasattr(self.maze, 'regions'):
            for node, rid in self.maze.regions.items():
                # Default dim
                alpha = 40 
                # Check if in plan
                is_in_plan = False
                if self.plan_path:
                    for item in self.plan_path:
                         if isinstance(item, int) and item == rid: is_in_plan = True
                         elif isinstance(item, str) and item == f"R_{rid}": is_in_plan = True
                
                if is_in_plan: alpha = 150 # Highlight plan regions
                
                color_idx = (rid - 1) % len(colors)
                color = colors[color_idx]
                
                rect = pygame.Rect(node.c * TILE_SIZE, node.r * TILE_SIZE + OFFSET_Y, TILE_SIZE, TILE_SIZE)
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                s.fill((*color, alpha))
                screen.blit(s, rect)

        # 2. Draw Region Graph Layers
        centroids = {}
        if hasattr(self.maze, 'regions_by_id'):
            for rid, nodes in self.maze.regions_by_id.items():
                if not nodes: continue
                r = sum(n.r for n in nodes)/len(nodes)
                c = sum(n.c for n in nodes)/len(nodes)
                centroids[f'R_{rid}'] = (c * TILE_SIZE + TILE_SIZE//2, r * TILE_SIZE + OFFSET_Y + TILE_SIZE//2)
                
                # Draw Centroid Dot
                # pygame.draw.circle(screen, (255, 255, 255), (int(centroids[f'R_{rid}'][0]), int(centroids[f'R_{rid}'][1])), 2)

        # 3. Draw The Plan Path
        if self.plan_visible and self.plan_path:
            plan_points = []
            
            # Helper to get pos
            def get_pos(item):
                if isinstance(item, str) and item.startswith("R_"):
                    if item in centroids: return centroids[item]
                elif hasattr(item, 'r'):
                    return (item.c * TILE_SIZE + TILE_SIZE//2, item.r * TILE_SIZE + OFFSET_Y + TILE_SIZE//2)
                return None

            # Add Start Node Connection
            start_pos = (self.start_node.c * TILE_SIZE + TILE_SIZE//2, self.start_node.r * TILE_SIZE + OFFSET_Y + TILE_SIZE//2)
            plan_points.append(start_pos)
            
            for item in self.plan_path:
                p = get_pos(item)
                if p: plan_points.append(p)
                
            # Add Goal Node Connection
            goal_pos = (self.goal_node.c * TILE_SIZE + TILE_SIZE//2, self.goal_node.r * TILE_SIZE + OFFSET_Y + TILE_SIZE//2)
            plan_points.append(goal_pos)
            
            # Draw Path Lines
            if len(plan_points) > 1:
                pygame.draw.lines(screen, (0, 255, 255), False, [(int(p[0]), int(p[1])) for p in plan_points], 5)

            # Draw Steps & Start/Goal
            # Start
            pygame.draw.circle(screen, (0, 255, 0), (int(start_pos[0]), int(start_pos[1])), 10)
            
            # Plan Nodes
            for idx, item in enumerate(self.plan_path):
                pos = get_pos(item)
                color = (200, 200, 200)
                radius = 6
                
                if isinstance(item, str): # Region
                     color = (255, 255, 255)
                else: # AP
                     color = (255, 0, 0)
                     
                if pos:
                    if idx == self.current_step_idx:
                        pygame.draw.circle(screen, (255, 255, 0), (int(pos[0]), int(pos[1])), radius + 4, 2)
                    pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), radius)

            # Goal
            pygame.draw.circle(screen, (0, 0, 255), (int(goal_pos[0]), int(goal_pos[1])), 10)

        txt = font.render(self.status_text, True, (255, 255, 255))
        screen.blit(txt, (20, 60))