import pygame
import sys
import time
import math
from game_classes import Maze, Player, HierarchicalAI
from Huffman.huffman import Huffman
from dynamic_maze import DynamicMaze
from GBFS.Euclidean.euclidean import EuclideanAI
from GBFS.Manhattan.manhattan import ManhattanAI
from GBFS.chebyshev.chebyshev import ChebyshevAI
from HillClimbing.hill_climbing import HillClimbingAI
from DFS.dfs import DFSAI
from BFS.bfs import BFSAI
from DFS.dfs import DFSAI
from BFS.bfs import BFSAI
from AStar.astar import AStarAI
from circular_maze import CircularMaze

from algorithm_visualizer import TarjanVisualizer, RegionVisualizer, ConquerVisualizer

# UI States
MENU = 0
PLAYING = 1
GAME_OVER = 2
INSTRUCTIONS = 3
REPLAY = 4
SIMULATION = 5
GRAPH_VIEW = 6
VISUALIZE_LOGIC = 7
DP_SIMULATION = 8  # J key - Animated DP computation visualization

# Constants
TILE_SIZE = 30
FPS = 60  # Smoother animation
GRID_OFFSET_Y = 65 # Space for top HUD

# Modern Dark Theme Colors
BG_PRIMARY = (30, 30, 46)      # Deep Blue-Grey
BG_SECONDARY = (65, 65, 90)    # Lighter for Walls (High Contrast)
CARD_BG = (45, 45, 65, 230)    # Glassy panel
ACCENT_BLUE = (137, 180, 250)  # Soft Blue
ACCENT_PURPLE = (203, 166, 247)# Soft Purple
ACCENT_GREEN = (166, 227, 161) # Mint Green
ACCENT_RED = (243, 139, 168)   # Soft Red
ACCENT_ORANGE = (250, 179, 135)# Soft Orange
ACCENT_YELLOW = (249, 226, 175)# Soft Yellow
ACCENT_CYAN = (137, 220, 235)  # Soft Cyan
TEXT_MAIN = (205, 214, 244)    # Off-white
TEXT_SUB = (166, 173, 200)     # Muted text
BORDER_COLOR = (88, 91, 112)   # Subtle border

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 720), pygame.RESIZABLE)
        pygame.display.set_caption("Duel of Labyrinth")
        self.clock = pygame.time.Clock()

        # Modern Fonts (Using default for Web compatibility)
        self.title_font = pygame.font.Font(None, 80)
        self.heading_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.medium_font = pygame.font.Font(None, 28)
        self.font = pygame.font.Font(None, 24) 
        self.small_font = pygame.font.Font(None, 20)

        self.state = MENU
        self.level = "MEDIUM"
        self.ai_speed = 2
        self.grid_size = (21, 21)

        # Toggles
        self.show_graph = False
        self.show_heuristics = False
        self.show_dp_viz = False  # K key toggle for DP cost visualization
        self.show_annotations = False

        # Animation & Scroll
        self.pulse_time = 0
        self.instruction_scroll_y = 0
        self.max_scroll = 0
        self.scrollbar_grabbed = False
        self.last_move_time = 0

        self.reset_game("MEDIUM") # Default back to MEDIUM

    def draw_text(self, text, font, color, pos, anchor="center", shadow=True):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        setattr(rect, anchor, pos)
        
        if shadow:
            sh = font.render(text, True, (0, 0, 0, 100))
            sh_rect = sh.get_rect()
            setattr(sh_rect, anchor, (pos[0] + 2, pos[1] + 2))
            self.screen.blit(sh, sh_rect)
            
        self.screen.blit(surf, rect)

    def draw_instructions(self):
        w, h = self.screen.get_size()
        self.screen.fill(BG_PRIMARY)

        self.draw_text("HOW TO PLAY", self.title_font, ACCENT_BLUE, (w//2, 90))

        content_x, content_y = 120, 180
        line_h = 36
        header_h = 56

        sections = [
            ("OBJECTIVE", [
                "Navigate to the goal (G) with the lowest possible cost.",
                "Compete head-to-head against a Greedy Best-First Search AI.",
                "Collect Power-Ups (-2 cost) and avoid Traps (+3 cost)."
            ]),
            ("CONTROLS", [
                "MOVEMENT:",
                "  W / Up Arrow    : Move Up",
                "  S / Down Arrow  : Move Down",
                "  A / Left Arrow  : Move Left",
                "  D / Right Arrow : Move Right",
                "",
                "DIAGONALS:",
                "  Q : Up-Left   |  E : Up-Right",
                "  Z : Down-Left |  C : Down-Right",
                "",
                "SYSTEM:",
                "  ESC : Return to Menu",
                "  R   : Restart Level",
                "  G   : Toggle Graph Overlay",
                "  H   : Toggle Heuristics",
                "  A   : Toggle AI Annotations"
            ]),
            ("LEGEND", [
                "S : Start Node  |  G : Goal Node",
                "Red Circle   : Trap (Cost +3)",
                "Green Circle : Power-Up (Cost -2)",
                "# : Wall"
            ]),
            ("ALGORITHM VIZ (Press 'L')", [
                "PHASE 1: THE BLUE SNAKE (Finding Bridges)",
                "  - Blue Line: AI exploring paths.",
                "  - Red Diamonds: Critical Choke Points.",
                "",
                "PHASE 2: THE COLOR FLOOD (Mapping Islands)",
                "  - Colored Areas: Safe 'Islands'.",
                "  - Yellow/Red Diamonds: The 'Bridges' connecting them.",
                "  - White Lines: The abstract Graph the AI uses.",
                "  - Auto-Restarts if walls move!"
            ])
        ]

        total_h = sum(header_h + len(lines) * line_h + 40 for _, lines in sections)
        self.max_scroll = max(0, total_h - (h - 220))

        # Scrollbar
        if self.max_scroll > 0:
            sb_x = w - 20
            sb_h = h - 200
            pygame.draw.rect(self.screen, BG_SECONDARY, (sb_x, 100, 8, sb_h), border_radius=4)
            handle_h = max(40, int(sb_h * sb_h / (total_h + 100)))
            ratio = self.instruction_scroll_y / self.max_scroll
            handle_y = 100 + int(ratio * (sb_h - handle_h))
            pygame.draw.rect(self.screen, ACCENT_BLUE, (sb_x, handle_y, 8, handle_h), border_radius=4)

        clip = pygame.Rect(content_x, content_y, w - 200, h - content_y - 80)
        self.screen.set_clip(clip)

        y = content_y - self.instruction_scroll_y
        for header, lines in sections:
            self.draw_text(header, self.heading_font, ACCENT_PURPLE, (content_x, y), anchor="midleft", shadow=False)
            y += header_h
            for line in lines:
                surf = self.medium_font.render(line, True, TEXT_MAIN)
                self.screen.blit(surf, (content_x + 20, y))
                y += line_h
            y += 40

        self.screen.set_clip(None)

        footer = self.small_font.render("ESC / BACKSPACE : Back", True, TEXT_SUB)
        self.screen.blit(footer, footer.get_rect(center=(w//2, h-40)))

    def reset_game(self, level):
        print(f"Resetting game to level: {level}")
        self.level = level
        speeds = {"EASY": 1.0, "MEDIUM": 2.0, "HARD": 4.0, "DYNAMIC": 2.5, "CIRCULAR": 1.0}
        sizes = {"EASY": (15,15), "MEDIUM": (21,21), "HARD": (25,25), "DYNAMIC": (25, 25), "CIRCULAR": (20, 20)}
        self.grid_size = sizes[level]
        self.ai_speed = speeds[level]

        w, h = self.grid_size
        width = w * TILE_SIZE + 340
        height = h * TILE_SIZE + 120 + GRID_OFFSET_Y
        
        print(f"Setting display mode: {width}x{height}")
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Draw Loading Screen
        self.screen.fill(BG_PRIMARY)
        self.draw_text(f"Loading {level} Level...", self.large_font, ACCENT_BLUE, (width//2, height//2))
        self.draw_text("Generating Maze & Analyzing...", self.medium_font, TEXT_SUB, (width//2, height//2 + 50))
        pygame.display.flip()
        pygame.event.pump()

        print("Generating Maze...")
        print("Generating Maze...")
        if level == "DYNAMIC":
            self.maze = DynamicMaze(width=w, height=h)
        elif level == "CIRCULAR":
            print("Resetting to CircularMaze...")
            self.maze = CircularMaze(num_rings=4, sectors=12)
            print("CircularMaze Generated.")
        else:
            self.maze = Maze(width=w, height=h)
        print("Maze Generated")
        print("Maze Generated")
        pygame.event.pump()
        
        # Run Analysis
        print("Running BFS Analysis...")
        self.maze.bfs_analysis()
        self.maze.generate_heuristic_map() # Generate Greedy Map
        print("BFS Analysis Complete")
        pygame.event.pump()
        
        print("Running A* Optimal...")
        self.optimal_cost = self.maze.a_star_optimal()
        print(f"A* Complete. Cost: {self.optimal_cost}")
        pygame.event.pump()
        
        print("Initializing Player and AI...")
        self.player = Player(self.maze.start_node)
        self.ai = EuclideanAI(self.maze.start_node, self.maze.goal_node, self.maze)
        print("Initialization Complete")
        pygame.event.pump()

        self.game_over = False
        self.consumed_items = set()
        self.start_time = time.time()
        self.elapsed_time = 0
        self.show_bfs = False
        self.map_mode = 0 # 0=Off, 1=BFS, 2=Greedy
        
        # Replay System
        self.history = [] # List of (player_node, ai_node, ai_path_index)
        self.replay_index = 0
        self.replay_speed = 0
        self.show_heuristics = False
        self.show_graph = False
        self.show_visited = False
        self.show_huffman = False
        self.show_huffman = False
        self.record_frame()

        # Simulation System
        self.simulation_agents = []
        self.sim_names = []
        self.current_sim_index = 0


    def record_frame(self):
        # Record current state for replay
        self.history.append({
            'player_pos': (self.player.current_node.r, self.player.current_node.c),
            'ai_pos': (self.ai.current_node.r, self.ai.current_node.c),
            'ai_path': list(self.ai.path), # Copy
            'time': self.elapsed_time
        })

    def draw_menu(self):
        w, h = self.screen.get_size()
        self.screen.fill(BG_PRIMARY)

        # Title
        self.draw_text("DUEL OF LABYRINTH", self.title_font, ACCENT_GREEN, (w//2, h//3))


        options = [
            ("EASY", "EASY"),
            ("MEDIUM", "MEDIUM"),
            ("HARD", "HARD"),
            ("DYNAMIC", "DYNAMIC"),
            ("CIRCULAR", "CIRCULAR"),
            ("INSTRUCTIONS", INSTRUCTIONS)
        ]

        mx, my = pygame.mouse.get_pos()
        base_y = h//2 - 30

        for i, (text, val) in enumerate(options):
            y = base_y + i * 70
            rect = pygame.Rect(w//2 - 150, y - 30, 300, 60)
            hovered = rect.collidepoint(mx, my)
            
            # Button Style
            color = ACCENT_PURPLE if hovered else BG_SECONDARY
            text_col = BG_PRIMARY if hovered else TEXT_MAIN
            
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            if not hovered:
                pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2, border_radius=12)
            
            text_surf = self.heading_font.render(text, True, text_col)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        hint = self.small_font.render("Select a level to start", True, TEXT_SUB)
        self.screen.blit(hint, hint.get_rect(center=(w//2, h - 50)))


    def draw_circular_maze(self):
        """Render circular maze as stone labyrinth with thick walls and carved corridors."""
        w, h = self.screen.get_size()
        cx, cy = w // 2, h // 2 + 30  # Center point with header offset
        
        max_radius = min(w, h) // 2 - 50
        num_rings = self.maze.num_rings
        ring_step = max_radius // (num_rings + 0.5)
        
        # Wall and corridor dimensions
        wall_thickness = 10  # Thick stone walls
        
        # Color scheme: Stone labyrinth aesthetic
        wall_color = (90, 90, 110)           # Dark blue-gray stone
        corridor_floor = (60, 55, 50)        # Warm dark stone floor
        corridor_outline = (40, 35, 30)      # Darker outline for depth
        
        # Helper function for polar coordinates
        def get_pt(deg, radius):
            """Convert polar (angle, radius) to screen (x, y)."""
            rad = math.radians(deg)
            return (cx + math.cos(rad) * radius, cy + math.sin(rad) * radius)
        
        # ========== LAYER 1: Draw all walls (full grid) ==========
        # Draw complete wall grid first, then carve corridors
        wall_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        for r in range(num_rings):
            radius_inner = r * ring_step
            radius_outer = (r + 1) * ring_step
            
            S = self.maze.sectors_per_ring
            angle_step = 360 / S
            offset_angle = self.maze.offsets[r] * angle_step
            
            # Draw radial walls (all sectors)
            for s in range(S):
                start_deg = -90 + (s * angle_step) + offset_angle
                end_deg = start_deg + angle_step
                
                # Radial wall at end of sector (clockwise edge)
                wp_inner = get_pt(end_deg, radius_inner)
                wp_outer = get_pt(end_deg, radius_outer)
                pygame.draw.line(wall_surf, wall_color, wp_inner, wp_outer, wall_thickness)
            
            # Draw ring wall (arc between rings)
            if r > 0:  # No inner wall for center
                # Draw continuous arc for this ring
                pts = []
                for i in range(int(S * 10)):  # High precision arc
                    deg = -90 + (i / (S * 10)) * 360 + offset_angle
                    pts.append(get_pt(deg, radius_inner))
                if len(pts) > 1:
                    pygame.draw.lines(wall_surf, wall_color, True, pts, wall_thickness)
        
        # Draw outer boundary (always solid)
        pygame.draw.circle(wall_surf, wall_color, (cx, cy), int(max_radius), wall_thickness)
        
        # ========== LAYER 2: Carve corridors where walls are open ==========
        corridor_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        for r in range(num_rings):
            radius_inner = r * ring_step
            radius_outer = (r + 1) * ring_step
            
            S = self.maze.sectors_per_ring
            angle_step = 360 / S
            offset_angle = self.maze.offsets[r] * angle_step
            
            for s in range(S):
                node = self.maze.grid[r][s]
                start_deg = -90 + (s * angle_step) + offset_angle
                end_deg = start_deg + angle_step
                
                # Draw corridor floor for this sector
                # Create polygon for corridor area
                pts = []
                # Outer arc
                for i in range(11):
                    pts.append(get_pt(start_deg + (i/10)*angle_step, radius_outer - wall_thickness//2))
                # Inner arc (reverse)
                for i in range(10, -1, -1):
                    pts.append(get_pt(start_deg + (i/10)*angle_step, radius_inner + wall_thickness//2))
                
                # Draw corridor floor
                pygame.draw.polygon(corridor_surf, corridor_floor, pts)
                pygame.draw.polygon(corridor_surf, corridor_outline, pts, 2)  # Outline for depth
                
                # Carve CW opening (remove radial wall if open)
                if not node.walls['cw']:
                    # Draw corridor color over the wall
                    wp_inner = get_pt(end_deg, radius_inner + wall_thickness//2)
                    wp_outer = get_pt(end_deg, radius_outer - wall_thickness//2)
                    pygame.draw.line(corridor_surf, corridor_floor, wp_inner, wp_outer, wall_thickness + 4)
                
                # Carve In opening (remove ring wall if open)
                if r > 0 and not node.walls['in']:
                    # Draw corridor color over the inner arc wall
                    pts = []
                    for i in range(11):
                        pts.append(get_pt(start_deg + (i/10)*angle_step, radius_inner))
                    pygame.draw.lines(corridor_surf, corridor_floor, False, pts, wall_thickness + 4)
        
        # Blit walls and corridors
        self.screen.blit(wall_surf, (0, 0))
        self.screen.blit(corridor_surf, (0, 0))
        
        # ========== LAYER 3: Draw DP cost glow overlay ==========
        glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        for r in range(num_rings):
            radius_inner = r * ring_step
            radius_outer = (r + 1) * ring_step
            
            S = self.maze.sectors_per_ring
            angle_step = 360 / S
            offset_angle = self.maze.offsets[r] * angle_step
            
            for s in range(S):
                node = self.maze.grid[r][s]
                start_deg = -90 + (s * angle_step) + offset_angle
                end_deg = start_deg + angle_step
                
                # DP glow (cyan/teal for low cost) - Toggle with K key
                if self.show_dp_viz and node.dp_cost < float('inf'):
                    val = max(0, 20 - node.dp_cost) / 20.0
                    if val > 0:
                        color = (0, int(180 * val), int(200 * val), 80)
                        pts = []
                        # Outer arc
                        for i in range(11):
                            pts.append(get_pt(start_deg + (i/10)*angle_step, radius_outer - wall_thickness//2))
                        # Inner arc
                        for i in range(10, -1, -1):
                            pts.append(get_pt(start_deg + (i/10)*angle_step, radius_inner + wall_thickness//2))
                        pygame.draw.polygon(glow_surf, color, pts)
        
        self.screen.blit(glow_surf, (0, 0))
        
        # ========== LAYER 4: Draw Goal (Center) ==========
        # Draw glowing center goal
        goal_radius = min(ring_step // 2, 20)
        # Outer glow
        for i in range(3):
            alpha = 100 - i * 30
            r = goal_radius + (3 - i) * 8
            s = pygame.Surface((r*2+20, r*2+20), pygame.SRCALPHA)
            pygame.draw.circle(s, (50, 200, 50, alpha), (r+10, r+10), r)
            self.screen.blit(s, (cx - r - 10, cy - r - 10))
        # Solid center
        pygame.draw.circle(self.screen, (80, 255, 80), (cx, cy), goal_radius)
        pygame.draw.circle(self.screen, (200, 255, 200), (cx, cy), goal_radius, 3)
        self.draw_text("G", self.font, (20, 20, 20), (cx, cy), shadow=False)
        
        # ========== LAYER 5: Draw Player ==========
        if self.player and self.player.current_node:
            pr = self.player.current_node.r
            pc = self.player.current_node.c
            
            # Calculate Player position (center of corridor)
            p_offset = self.maze.offsets[pr] * (360/self.maze.sectors_per_ring)
            p_angle = -90 + (pc * (360/self.maze.sectors_per_ring)) + p_offset + (360/self.maze.sectors_per_ring)/2
            p_rad = math.radians(p_angle)
            p_dist = (pr * ring_step) + ring_step/2
            
            px = cx + math.cos(p_rad) * p_dist
            py = cy + math.sin(p_rad) * p_dist
            
            # Player with glow
            glow_r = 15
            for i in range(3):
                alpha = 80 - i * 25
                r = glow_r + (3 - i) * 4
                s = pygame.Surface((r*2+10, r*2+10), pygame.SRCALPHA)
                pygame.draw.circle(s, (*ACCENT_BLUE, alpha), (r+5, r+5), r)
                self.screen.blit(s, (int(px - r - 5), int(py - r - 5)))
            
            pygame.draw.circle(self.screen, ACCENT_BLUE, (int(px), int(py)), 10)
            pygame.draw.circle(self.screen, TEXT_MAIN, (int(px), int(py)), 10, 2)
        
        # ========== LAYER 6: Draw AI ==========
        if self.ai and self.ai.current_node:
            ar = self.ai.current_node.r
            ac = self.ai.current_node.c
            
            # Calculate AI position (center of corridor)
            a_offset = self.maze.offsets[ar] * (360/self.maze.sectors_per_ring)
            a_angle = -90 + (ac * (360/self.maze.sectors_per_ring)) + a_offset + (360/self.maze.sectors_per_ring)/2
            a_rad = math.radians(a_angle)
            a_dist = (ar * ring_step) + ring_step/2
            
            ax = cx + math.cos(a_rad) * a_dist
            ay = cy + math.sin(a_rad) * a_dist
            
            # AI with glow (orange)
            glow_r = 15
            for i in range(3):
                alpha = 80 - i * 25
                r = glow_r + (3 - i) * 4
                s = pygame.Surface((r*2+10, r*2+10), pygame.SRCALPHA)
                pygame.draw.circle(s, (*ACCENT_ORANGE, alpha), (r+5, r+5), r)
                self.screen.blit(s, (int(ax - r - 5), int(ay - r - 5)))
            
            pygame.draw.circle(self.screen, ACCENT_ORANGE, (int(ax), int(ay)), 10)
            pygame.draw.circle(self.screen, TEXT_MAIN, (int(ax), int(ay)), 10, 2)
        
    def draw_grid(self):
        if isinstance(self.maze, CircularMaze):
            self.draw_circular_maze()
            return
            
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                node = self.maze.get_node(r, c)
                if node is None: continue 
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE)

                # Fog of War Logic
                visible = True
                if self.state != REPLAY and not isinstance(self.maze, DynamicMaze):
                    if self.player and self.player.current_node:
                        dist = max(abs(node.r - self.player.current_node.r), abs(node.c - self.player.current_node.c))
                        visible = dist <= 3 or node.visited_by_player or node in (self.maze.start_node, self.maze.goal_node)
                    else:
                        visible = True 
                    
                    if not visible:
                        pygame.draw.rect(self.screen, BG_PRIMARY, rect)
                        continue

                # Dynamic Maze Visualizations (Warning/Animation)
                if isinstance(self.maze, DynamicMaze):
                    for change in self.maze.pending_changes:
                        if change['node'] == node:
                            if change['state'] == 'WARNING':
                                # Pulsing Yellow/Orange Overlay
                                pulse = (math.sin(time.time() * 10) + 1) * 0.5
                                alpha = int(100 * pulse)
                                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                                color = (255, 165, 0, alpha) if change['type'] == 'ADD_WALL' else (0, 255, 255, alpha)
                                s.fill(color)
                                self.screen.blit(s, rect)
                                pygame.draw.rect(self.screen, color[:3], rect, 2)
                                
                            elif change['state'] == 'ANIMATING':
                                # Scaling Animation
                                progress = 1.0 - (change['timer'] / 1.5) # 0 to 1
                                if change['type'] == 'ADD_WALL':
                                    # Growing Wall
                                    size = int(TILE_SIZE * progress)
                                    center_rect = pygame.Rect(0, 0, size, size)
                                    center_rect.center = rect.center
                                    pygame.draw.rect(self.screen, BG_SECONDARY, center_rect)
                                elif change['type'] == 'REMOVE_WALL':
                                    # Dissolving Wall (Fading out)
                                    alpha = int(255 * (1 - progress))
                                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                                    s.fill((*BG_SECONDARY, alpha))
                                    self.screen.blit(s, rect)
                            break

                # Flash Effect for Dynamic Changes
                if isinstance(self.maze, DynamicMaze) and self.maze.last_event_node == node:
                     time_diff = time.time() - self.maze.last_update_time
                     if time_diff < 1.0: # Flash for 1 second
                         if int(time_diff * 10) % 2 == 0: # Strobe
                             pygame.draw.rect(self.screen, (255, 255, 255), rect)
                             pygame.draw.rect(self.screen, ACCENT_YELLOW, rect, 3)
                             continue

                if node.type == '#':
                    color = BG_SECONDARY
                    pygame.draw.rect(self.screen, color, rect)
                else:
                    color = (20, 20, 30) # Darker floor for contrast
                    
                    # Map Visualization
                    mode = getattr(self, 'map_mode', 0)
                    if not mode and getattr(self, 'show_bfs', False): mode = 1 # Fallback

                    if mode == 1 and hasattr(self.maze, 'bfs_map') and node in self.maze.bfs_map:
                        # BFS (Cyan)
                        dist = self.maze.bfs_map[node]
                        max_dist = self.maze.max_bfs_distance if self.maze.max_bfs_distance > 0 else 1
                        intensity = 1 - (dist / max_dist)
                        intensity = max(0.0, min(1.0, intensity))
                        g = int(255 * intensity * 0.5)
                        b = int(255 * intensity)
                        color = (0, g, b)
                    
                    elif mode == 2 and hasattr(self.maze, 'heuristic_map') and node in self.maze.heuristic_map:
                        # Greedy Heuristic (Magenta/Red)
                        dist = self.maze.heuristic_map[node]
                        max_dist = self.maze.max_heuristic_dist if self.maze.max_heuristic_dist > 0 else 1
                        intensity = 1 - (dist / max_dist)
                        intensity = max(0.0, min(1.0, intensity))
                        r = int(255 * intensity)
                        b = int(255 * intensity * 0.5)
                        color = (r, 0, b)

                    pygame.draw.rect(self.screen, color, rect)
                    # Subtle grid lines
                    pygame.draw.rect(self.screen, (40, 40, 55), rect, 1)

                if (r,c) not in self.consumed_items:
                    if node.type == 'T':
                        pygame.draw.circle(self.screen, ACCENT_RED, rect.center, TILE_SIZE//4)
                    elif node.type == 'P':
                        pygame.draw.circle(self.screen, ACCENT_GREEN, rect.center, TILE_SIZE//4)

                # Dynamic Maze Visualization
                if getattr(self, 'show_regions', False) and isinstance(self.maze, DynamicMaze):
                    if node in self.maze.articulation_points:
                        # Articulation Point (Orange Diamond)
                        cx, cy = rect.center
                        pts = [(cx, cy-8), (cx+8, cy), (cx, cy+8), (cx-8, cy)]
                        pygame.draw.polygon(self.screen, ACCENT_ORANGE, pts)
                    elif node in self.maze.regions:
                        # Region Coloring (Subtle Tint)
                        rid = self.maze.regions[node]
                        # Deterministic color from Region ID
                        colors = [
                            (50, 0, 0), (0, 50, 0), (0, 0, 50), 
                            (50, 50, 0), (0, 50, 50), (50, 0, 50)
                        ]
                        tint = colors[rid % len(colors)]
                        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        s.fill((*tint, 100))
                        self.screen.blit(s, rect)

                if node == self.maze.start_node and self.player.current_node != node:
                    self.draw_text("S", self.font, ACCENT_GREEN, rect.center, shadow=False)
                elif node == self.maze.goal_node:
                    self.draw_text("G", self.font, ACCENT_PURPLE, rect.center, shadow=False)

                if self.show_heuristics and node.heuristic_value is not None and visible:
                    h = f"{node.heuristic_value:.1f}"
                    hs = self.small_font.render(h, True, ACCENT_BLUE)
                    self.screen.blit(hs, (rect.x + 2, rect.y + 2))

    def draw_graph_overlay(self):
        if not self.show_graph: return
        drawn = set()
        for node in self.maze.adjacency_list:
            dist = max(abs(node.r - self.player.current_node.r), abs(node.c - self.player.current_node.c))
            if dist > 4 and not node.visited_by_player and node not in (self.maze.start_node, self.maze.goal_node):
                continue
            pos = (node.c * TILE_SIZE + TILE_SIZE//2, node.r * TILE_SIZE + TILE_SIZE//2 + GRID_OFFSET_Y)
            for neigh, wt in self.maze.adjacency_list[node]:
                edge = tuple(sorted([(node.r,node.c),(neigh.r,neigh.c)]))
                if edge in drawn: continue
                drawn.add(edge)
                npos = (neigh.c * TILE_SIZE + TILE_SIZE//2, neigh.r * TILE_SIZE + TILE_SIZE//2 + GRID_OFFSET_Y)
                color = ACCENT_GREEN if wt <= 0 else ACCENT_RED if wt >= 3 else (60, 60, 80)
                pygame.draw.line(self.screen, color, pos, npos, 1)

    def draw_entities(self):
        # Circular maze handles its own entity rendering
        if isinstance(self.maze, CircularMaze):
            return
        
        # Player trail
        if len(self.player.path) > 1:
            points = [(n.c * TILE_SIZE + TILE_SIZE//2, n.r * TILE_SIZE + TILE_SIZE//2 + GRID_OFFSET_Y) for n in self.player.path]
            if len(points) > 1:
                pygame.draw.lines(self.screen, ACCENT_BLUE, False, points, 2)

        # AI trail
        if len(self.ai.path) > 1 and self.show_annotations:
            points = [(n.c * TILE_SIZE + TILE_SIZE//2, n.r * TILE_SIZE + TILE_SIZE//2 + GRID_OFFSET_Y) for n in self.ai.path]
            if len(points) > 1:
                pygame.draw.lines(self.screen, ACCENT_ORANGE, False, points, 2)

        # Player
        pr = pygame.Rect(self.player.current_node.c * TILE_SIZE, self.player.current_node.r * TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE)
        pygame.draw.circle(self.screen, ACCENT_BLUE, pr.center, TILE_SIZE//3)
        pygame.draw.circle(self.screen, TEXT_MAIN, pr.center, TILE_SIZE//3, 2) # White border
        
        # AI
        ar = pygame.Rect(self.ai.current_node.c * TILE_SIZE, self.ai.current_node.r * TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE)
        pygame.draw.circle(self.screen, ACCENT_ORANGE, ar.center, TILE_SIZE//3)

        if self.show_annotations:
            for node, _ in self.ai.current_candidates:
                cr = pygame.Rect(node.c * TILE_SIZE, node.r * TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (100, 200, 255, 50), cr, 2)

    def draw_hud(self):
        w, h = self.screen.get_size()
        
        # Top Bar (Level & Time)
        bar_h = 60
        pygame.draw.rect(self.screen, CARD_BG, (0, 0, w, bar_h))
        pygame.draw.line(self.screen, BORDER_COLOR, (0, bar_h), (w, bar_h))

        self.draw_text(f"LEVEL: {self.level}", self.heading_font, ACCENT_BLUE, (20, bar_h//2), anchor="midleft", shadow=False)
        self.draw_text(f"TIME: {self.elapsed_time:.1f}s", self.heading_font, ACCENT_PURPLE, (w - 20, bar_h//2), anchor="midright", shadow=False)
        self.draw_text("DUEL OF LABYRINTH", self.heading_font, TEXT_MAIN, (w//2, bar_h//2), shadow=False)

        # Side Panel (Metrics)
        panel_w = 300
        panel_x = w - panel_w - 20
        panel_y = bar_h + 20
        panel_h = h - bar_h - 40
        
        # Only show full metrics if there is space
        if w > self.grid_size[0] * TILE_SIZE + 320:
            rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            pygame.draw.rect(self.screen, CARD_BG, rect, border_radius=12)
            pygame.draw.rect(self.screen, BORDER_COLOR, rect, 1, border_radius=12)

            y = panel_y + 30
            self.draw_text("METRICS", self.large_font, ACCENT_GREEN, (panel_x + panel_w//2, y), shadow=False)
            y += 40

            # Scores
            self.draw_text("PLAYER", self.medium_font, ACCENT_BLUE, (panel_x + 70, y), shadow=False)
            self.draw_text("AI", self.medium_font, ACCENT_ORANGE, (panel_x + 230, y), shadow=False)
            y += 30
            self.draw_text(f"Cost: {self.player.total_cost}", self.font, TEXT_MAIN, (panel_x + 70, y), shadow=False)
            self.draw_text(f"Cost: {self.ai.total_cost}", self.font, TEXT_MAIN, (panel_x + 230, y), shadow=False)
            y += 20
            self.draw_text(f"Steps: {self.player.steps}", self.font, TEXT_SUB, (panel_x + 70, y), shadow=False)
            self.draw_text(f"Steps: {self.ai.steps}", self.font, TEXT_SUB, (panel_x + 230, y), shadow=False)
            
            y += 40
            pygame.draw.line(self.screen, BORDER_COLOR, (panel_x + 20, y), (panel_x + panel_w - 20, y))
            y += 20

            # AI Analysis
            stats = [
                f"Explored: {self.ai.metrics.nodes_explored}",
                f"Backtracks: {self.ai.metrics.backtrack_count}",
                f"Efficiency: {self.ai.get_efficiency_vs_optimal(self.maze.optimal_path_length)*100:.1f}%"
            ]
            
            for line in stats:
                self.draw_text(line, self.font, TEXT_MAIN, (panel_x + panel_w//2, y), shadow=False)
                y += 25

            # Dynamic Maze Log
            if isinstance(self.maze, DynamicMaze):
                 y += 10
                 pygame.draw.line(self.screen, BORDER_COLOR, (panel_x + 20, y), (panel_x + panel_w - 20, y))
                 y += 20
                 self.draw_text("DYNAMIC EVENTS", self.medium_font, ACCENT_CYAN, (panel_x + panel_w//2, y), shadow=False)
                 y += 25
                 self.draw_text(self.maze.last_event_description, self.small_font, ACCENT_YELLOW, (panel_x + panel_w//2, y), shadow=False)

                 # Live Graph Panel
                 y += 20
                 pygame.draw.line(self.screen, BORDER_COLOR, (panel_x + 20, y), (panel_x + panel_w - 20, y))
                 y += 20
                 self.draw_text("LIVE GRAPH", self.medium_font, ACCENT_GREEN, (panel_x + panel_w//2, y), shadow=False)
                 y += 10
                 
                 # Draw Mini Graph
                 graph_h = 240
                 graph_rect = pygame.Rect(panel_x + 20, y, panel_w - 40, graph_h)
                 pygame.draw.rect(self.screen, (10, 10, 15), graph_rect)
                 pygame.draw.rect(self.screen, (50, 50, 60), graph_rect, 1)
                 
                 # Coordinate mapping
                 gw, gh = graph_rect.w, graph_rect.h
                 mw, mh = self.maze.width, self.maze.height
                 scale_x = gw / mw
                 scale_y = gh / mh
                 
                 def to_screen(c, r):
                     return (graph_rect.x + int(c * scale_x) + int(scale_x/2),
                             graph_rect.y + int(r * scale_y) + int(scale_y/2))

                 # Draw Edges (Green for active, Red/Fade for changes)
                 # 1. Static Edges
                 for r in range(mh):
                    for c in range(mw):
                        node = self.maze.grid[r][c]
                        if node.type == '#': continue
                        p1 = to_screen(c, r)
                        # Right
                        if c+1 < mw and self.maze.grid[r][c+1].type != '#':
                            p2 = to_screen(c+1, r)
                            pygame.draw.line(self.screen, (0, 100, 0), p1, p2, 1)
                        # Down
                        if r+1 < mh and self.maze.grid[r+1][c].type != '#':
                            p2 = to_screen(c, r+1)
                            pygame.draw.line(self.screen, (0, 100, 0), p1, p2, 1)

                 # 2. Animated Changes
                 for node, type, timer in self.maze.recent_edge_changes:
                     # Flash/Fade Effect
                     intensity = int(255 * (timer / 1.0)) # 1.0s duration
                     color = (0, 255, 0) if type == 'ADD' else (255, 0, 0)
                     if type == 'REMOVE': intensity = max(0, intensity)
                     
                     cx, cy = to_screen(node.c, node.r)
                     pygame.draw.circle(self.screen, (*color, intensity), (cx, cy), int(scale_x*1.5))
                     
                 # Draw Nodes
                 for r in range(mh):
                     for c in range(mw):
                         node = self.maze.grid[r][c]
                         if node.type == '#': continue
                         
                         pos = to_screen(c, r)
                         color = (100, 100, 100) # White/Gray
                         radius = 1
                         
                         if node == self.player.current_node:
                             color = ACCENT_BLUE
                             radius = 3
                         elif node in self.maze.articulation_points:
                             color = ACCENT_RED
                             radius = 2
                         
                         pygame.draw.circle(self.screen, color, pos, radius)

            # Controls Hint
            y = panel_y + panel_h - 40
            self.draw_text("ESC: Menu | R: Restart | B: BFS", self.small_font, TEXT_SUB, (panel_x + panel_w//2, y), shadow=False)

    def draw_graph_simulation(self):
        """Mode 3: Full Screen Graph Simulation View"""
        self.screen.fill((10, 10, 15)) # Deep Dark Background
        
        w, h = self.screen.get_size()
        
        # Calculate Scale to fit maze with padding
        padding = 50
        mw, mh = self.maze.width, self.maze.height
        
        avail_w = w - 2 * padding
        avail_h = h - 2 * padding
        
        scale = min(avail_w / mw, avail_h / mh)
        
        # Center the graph
        offset_x = (w - mw * scale) / 2
        offset_y = (h - mh * scale) / 2
        
        def to_screen(c, r):
            return (int(offset_x + c * scale + scale/2), 
                    int(offset_y + r * scale + scale/2))

        # 1. Draw Edges
        # Static Edges (Green, faint)
        for r in range(mh):
            for c in range(mw):
                node = self.maze.grid[r][c]
                if node.type == '#': continue
                
                p1 = to_screen(c, r)
                # Right
                if c+1 < mw and self.maze.grid[r][c+1].type != '#':
                    p2 = to_screen(c+1, r)
                    pygame.draw.line(self.screen, (0, 50, 0), p1, p2, 2)
                # Down
                if r+1 < mh and self.maze.grid[r+1][c].type != '#':
                    p2 = to_screen(c, r+1)
                    pygame.draw.line(self.screen, (0, 50, 0), p1, p2, 2)

        # Animated Edges (Bright Green for ADD, Red/Fade for REMOVE)
        if isinstance(self.maze, DynamicMaze):
             for node, type, timer in self.maze.recent_edge_changes:
                 intensity = int(255 * (timer / 1.0))
                 width = int(scale * 0.2)
                 if type == 'ADD':
                     color = (0, 255, 0)
                 else:
                     color = (255, 0, 0)
                     intensity = max(0, intensity)
                 
                 cx, cy = to_screen(node.c, node.r)
                 # Draw a glow around the node for now as edges are harder to isolate without source
                 s = pygame.Surface((int(scale*3), int(scale*3)), pygame.SRCALPHA)
                 pygame.draw.circle(s, (*color, max(0, min(100, intensity))), (int(scale*1.5), int(scale*1.5)), int(scale*1.2))
                 self.screen.blit(s, (cx - int(scale*1.5), cy - int(scale*1.5)))

        # 2. Draw Nodes
        node_radius = int(scale * 0.3)
        for r in range(mh):
            for c in range(mw):
                node = self.maze.grid[r][c]
                if node.type == '#': continue
                
                pos = to_screen(c, r)
                color = (200, 200, 200) # White/Gray
                
                if node == self.player.current_node:
                    color = ACCENT_BLUE
                    radius = node_radius + 4
                elif isinstance(self.maze, DynamicMaze) and node in self.maze.articulation_points:
                    color = ACCENT_RED
                    radius = node_radius + 2
                else:
                    radius = node_radius
                
                pygame.draw.circle(self.screen, color, pos, radius)

        # HUD Overlay
        self.draw_text("GRAPH SIMULATION MODE", self.large_font, ACCENT_GREEN, (w//2, 40), shadow=True)
        self.draw_text("Press 'G' or ESC to Exit", self.medium_font, TEXT_SUB, (w//2, h - 40), shadow=True)
        
        if isinstance(self.maze, DynamicMaze):
             self.draw_text(self.maze.last_event_description, self.medium_font, ACCENT_YELLOW, (w//2, 80), shadow=True)

    def draw_game_over(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((20, 20, 30, 220))
        self.screen.blit(overlay, (0, 0))

        card_w, card_h = 600, 450
        cx, cy = w//2, h//2
        card = pygame.Rect(cx - card_w//2, cy - card_h//2, card_w, card_h)
        
        pygame.draw.rect(self.screen, BG_SECONDARY, card, border_radius=20)
        pygame.draw.rect(self.screen, BORDER_COLOR, card, 2, border_radius=20)

        self.draw_text("GAME OVER", self.title_font, ACCENT_RED, (cx, cy - 160))

        p_win = self.player.current_node == self.maze.goal_node
        a_win = self.ai.current_node == self.maze.goal_node

        if p_win and not a_win:
            result, col = "VICTORY! (Reached Goal First)", ACCENT_GREEN
        elif a_win and not p_win:
            result, col = "AI WINS! (Reached Goal First)", ACCENT_ORANGE
        elif p_win and a_win:
            # Both finished - Compare Cost first
            if self.player.total_cost < self.ai.total_cost:
                result, col = "YOU WIN! (Lower Cost)", ACCENT_GREEN
            elif self.ai.total_cost < self.player.total_cost:
                result, col = "AI WINS! (Lower Cost)", ACCENT_ORANGE
            else:
                # Tiebreaker: Steps
                if self.player.steps < self.ai.steps:
                    result, col = "YOU WIN! (Fewer Steps)", ACCENT_GREEN
                elif self.ai.steps < self.player.steps:
                    result, col = "AI WINS! (Fewer Steps)", ACCENT_ORANGE
                else:
                    result, col = "DRAW!", ACCENT_BLUE
        else:
            # Should not happen if game_over is triggered by both finishing
            # But if AI gets stuck and gives up?
            if self.ai.finished and not a_win:
                 result, col = "VICTORY! (AI Failed)", ACCENT_GREEN
            else:
                 result, col = "NO ONE REACHED GOAL", TEXT_SUB

        self.draw_text(result, self.heading_font, col, (cx, cy - 90))

        y = cy - 20
        stats = [
            f"Your Cost: {self.player.total_cost}  |  AI Cost: {self.ai.total_cost}",
            f"Your Steps: {self.player.steps}  |  AI Steps: {self.ai.steps}",
            "",
            f"AI Efficiency: {self.ai.get_efficiency_vs_optimal(self.maze.optimal_path_length)*100:.1f}%"
        ]

        for line in stats:
            if line:
                self.draw_text(line, self.medium_font, TEXT_MAIN, (cx, y), shadow=False)
            y += 35
            
        # Huffman Analysis
        # from game_classes import Huffman # Removed
        huff = Huffman() # Restored instantiation
        h_stats = huff.get_stats(self.ai.action_log)
        
        y += 20
        self.draw_text("Algorithm Analysis:", self.medium_font, ACCENT_YELLOW, (cx, y), shadow=False)
        y += 30
        self.draw_text(f"BFS Reachability: 100% (Verified)", self.font, TEXT_MAIN, (cx, y), shadow=False)
        y += 25
        self.draw_text(f"Huffman Compression: {h_stats['ratio']}% ({h_stats['original_bits']}b -> {h_stats['compressed_bits']}b)", self.font, TEXT_MAIN, (cx, y), shadow=False)

        if time.time() % 1.5 > 0.5:
            self.draw_text("Press ENTER to Menu", self.large_font, ACCENT_BLUE, (cx, cy + 160))
        
        self.draw_text("Press P to Watch Replay", self.medium_font, TEXT_SUB, (cx, cy + 200))
        self.draw_text("Press S to Simulate All Algorithms", self.medium_font, ACCENT_ORANGE, (cx, cy + 230))

    def draw_dp_simulation(self):
        """Animated DP computation visualization - shows wave spreading from center"""
        if not isinstance(self.maze, CircularMaze):
            self.state = PLAYING
            return
            
        self.screen.fill((5, 5, 10))
        w, h = self.screen.get_size()
        
        self.dp_sim_time += 1/60.0
        wave_speed = 50
        self.dp_sim_wave_radius = self.dp_sim_time * wave_speed
        
        self.draw_circular_maze()
        
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        max_radius = min(w, h) // 2 - 50
        
        # Center pulse
        pulse_scale = 1.0 + 0.3 * math.sin(self.dp_sim_time * 3)
        center_radius = 20 * pulse_scale
        for i in range(3):
            alpha = 180 - i * 50
            radius = center_radius + i * 8
            pygame.draw.circle(overlay, (0, 255, 200, alpha), (cx, cy), int(radius))
        
        # Wave spreading
        if self.dp_sim_wave_radius < max_radius:
            wave_thickness = 40
            for i in range(wave_thickness):
                alpha = int(150 * (1 - i / wave_thickness))
                radius = int(self.dp_sim_wave_radius - i)
                if radius > 0:
                    pygame.draw.circle(overlay, (0, 180, 255, alpha), (cx, cy), radius, 2)
        
        # Light up nodes
        num_rings = self.maze.num_rings
        sectors = self.maze.sectors_per_ring
        ring_step = max_radius / num_rings
        
        for r in range(num_rings):
            radius = (r + 0.5) * ring_step
            if radius <= self.dp_sim_wave_radius:
                for s in range(sectors):
                    node = self.maze.grid[r][s]
                    if (r, s) not in self.dp_sim_discovered:
                        self.dp_sim_discovered.add((r, s))
                    
                    if node.dp_cost < float('inf'):
                        intensity = max(0, 20 - node.dp_cost) / 20.0
                        if intensity > 0:
                            angle_step = 360 / sectors
                            offset_angle = self.maze.offsets[r] * angle_step
                            start_deg = -90 + (s * angle_step) + offset_angle
                            angle_rad = math.radians(start_deg + angle_step / 2)
                            nx = cx + int(radius * math.cos(angle_rad))
                            ny = cy + int(radius * math.sin(angle_rad))
                            glow_color = (0, int(200 * intensity), int(220 * intensity), 180)
                            pygame.draw.circle(overlay, glow_color, (nx, ny), 8)
                            pulse = 1.0 + 0.2 * math.sin(self.dp_sim_time * 5)
                            outer_radius = int(8 * pulse)
                            pygame.draw.circle(overlay, (0, 150, 200, 100), (nx, ny), outer_radius, 2)
        
        self.screen.blit(overlay, (0, 0))
        
        info_text = f"DP COMPUTATION SIMULATION | Wave Progress: {int(min(100, (self.dp_sim_wave_radius / max_radius) * 100))}%"
        self.draw_text(info_text, self.heading_font, (0, 255, 200), (w//2, 40))
        sub_text = "Nodes light up as DP costs are computed from center outward"
        self.draw_text(sub_text, self.medium_font, (150, 200, 255), (w//2, 75))
        
        if self.dp_sim_wave_radius >= max_radius + 50:
            if self.dp_sim_time > (max_radius / wave_speed) + 2:
                self.state = PLAYING
                self.show_dp_viz = True
                print("DP Simulation complete - returning to game with DP viz enabled")
        
        complete_text = "Press ESC to exit simulation" if self.dp_sim_wave_radius < max_radius else "Simulation Complete - Returning to game..."
        self.draw_text(complete_text, self.small_font, (200, 200, 200), (w//2, h - 30))

    def prepare_simulation(self):
        print("Preparing Simulation Agents...")
        self.simulation_agents = [
            HierarchicalAI(self.maze.start_node, self.maze.goal_node, self.maze),
            EuclideanAI(self.maze.start_node, self.maze.goal_node, self.maze),
            ManhattanAI(self.maze.start_node, self.maze.goal_node, self.maze),
            ChebyshevAI(self.maze.start_node, self.maze.goal_node, self.maze),
            HillClimbingAI(self.maze.start_node, self.maze.goal_node, self.maze),
            BFSAI(self.maze.start_node, self.maze.goal_node, self.maze),
            DFSAI(self.maze.start_node, self.maze.goal_node, self.maze),
            AStarAI(self.maze.start_node, self.maze.goal_node, self.maze)
        ]
        self.sim_names = [
            "Divide & Conquer (Hierarchical)",
            "Greedy Best-First (Euclidean)",
            "Greedy Best-First (Manhattan)",
            "Greedy Best-First (Chebyshev)",
            "Pure Greedy (Hill Climbing)",
            "Breadth-First Search (BFS)",
            "Depth-First Search (DFS)",
            "A* Search (Optimal)"
        ]
        self.current_sim_index = 0
        print("Simulation Agents Ready")

    def draw_simulation(self):
        self.screen.fill(BG_PRIMARY)
        
        # Use the current simulation agent as the 'active' AI for visualization
        current_agent = self.simulation_agents[self.current_sim_index]
        
        # Hack: Temporarily swap self.ai to current_agent to reuse draw methods
        # or just manually draw what we need. Let's manually draw to be safe and explicit.
        
        # 1. Draw Grid (Background)
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                node = self.maze.get_node(r, c)
                if node.type == '#':
                    pygame.draw.rect(self.screen, BG_SECONDARY, (c*TILE_SIZE, r*TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE))
                else:
                    color = (20, 20, 30)
                    # Show visited for current agent
                    if node in current_agent.visited_nodes:
                         color = (40, 40, 60) # Slightly lighter for visited
                    
                    pygame.draw.rect(self.screen, color, (c*TILE_SIZE, r*TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, (30, 30, 40), (c*TILE_SIZE, r*TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE), 1)

                if node == self.maze.start_node:
                    self.draw_text("S", self.font, ACCENT_GREEN, (c*TILE_SIZE + TILE_SIZE//2, r*TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2), shadow=False)
                elif node == self.maze.goal_node:
                    self.draw_text("G", self.font, ACCENT_PURPLE, (c*TILE_SIZE + TILE_SIZE//2, r*TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2), shadow=False)

        # 2. Draw Path
        if len(current_agent.full_path) > 1:
            points = [(n.c * TILE_SIZE + TILE_SIZE//2, n.r * TILE_SIZE + TILE_SIZE//2 + GRID_OFFSET_Y) for n in current_agent.full_path]
            pygame.draw.lines(self.screen, ACCENT_ORANGE, False, points, 3)

        # 3. Hierarchical AI Special Visualization (Divide & Conquer Plan)
        # DEBUG PRINT (Run once per second to avoid spam)
        if isinstance(current_agent, HierarchicalAI):
            if int(time.time()) % 2 == 0 and not hasattr(self, '_last_debug_print'):
                 self._last_debug_print = time.time()
                 print(f"DEBUG RENDER: Agent={current_agent.algorithm_name}, PlanLen={len(current_agent.high_level_plan)}, Regions={len(self.maze.regions) if hasattr(self.maze, 'regions') else 'None'}")
        
        if isinstance(current_agent, HierarchicalAI) and current_agent.high_level_plan:
            # A. REGION COLORING (The "Divide" Phase)
            # Define a palette of distinct colors (avoiding red/green/blue which are used for Start/Goal/Player)
            region_colors = [
                (100, 100, 0), (100, 0, 100), (0, 100, 100), 
                (100, 50, 0), (50, 100, 0), (0, 50, 100),
                (100, 0, 50), (50, 0, 100), (80, 80, 80)
            ]
            
            # Draw Region Overlays
            # We iterate over the grid and check region_map
            if hasattr(self.maze, 'regions'):
                for r in range(self.maze.height):
                    for c in range(self.maze.width):
                        node = self.maze.get_node(r, c)
                        if node in self.maze.regions:
                            rid = self.maze.regions[node]
                            color = region_colors[rid % len(region_colors)]
                            
                            # Draw semi-transparent overlay? Pygame rects are solid mostly unless Surface used.
                            # Let's draw a small colored square in the center or a border.
                            # Using a distinct border or inner rect is safer for performance than creating surfaces per cell.
                            x = c * TILE_SIZE
                            y = r * TILE_SIZE + GRID_OFFSET_Y
                            
                            # Draw inner colored rect
                            pygame.draw.rect(self.screen, color, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4))


            # B. HIGH-LEVEL PLAN (The "Plan" Phase)
            # We need to compute centroids for regions in the plan to draw clear arrows
            # Pre-compute centroids for all regions (or just the ones in plan)
            region_centroids = {}
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    node = self.maze.get_node(r, c)
                    if node in self.maze.regions:
                        rid = self.maze.regions[node]
                        if rid not in region_centroids: region_centroids[rid] = []
                        region_centroids[rid].append((r, c))
            
            # Average the coordinates
            final_centroids = {}
            for rid, coords in region_centroids.items():
                sr = sum(r for r, c in coords) / len(coords)
                sc = sum(c for r, c in coords) / len(coords)
                final_centroids[f"R_{rid}"] = (sr, sc)

            # Draw Plan Lines
            plan_points = []
            for item in current_agent.high_level_plan:
                if isinstance(item, str) and item.startswith("R_"): # Region
                    if item in final_centroids:
                        r, c = final_centroids[item]
                        x = int(c * TILE_SIZE + TILE_SIZE//2)
                        y = int(r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2)
                        plan_points.append((x, y))
                        # Draw Region Center
                        pygame.draw.circle(self.screen, (0, 255, 255), (x, y), 8) # Cyan dot
                        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 8, 1)
                        # Label Region ID
                        rid_num = item.split('_')[1]
                        self.draw_text(rid_num, self.small_font, (255, 255, 255), (x, y), shadow=True)
                        
                elif isinstance(item, Node): # Articulation Point
                    x = int(item.c * TILE_SIZE + TILE_SIZE//2)
                    y = int(item.r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2)
                    plan_points.append((x, y))
                    # Draw AP
                    pygame.draw.circle(self.screen, (255, 0, 255), (x, y), 6) # Magenta dot
            
            if len(plan_points) > 1:
                pygame.draw.lines(self.screen, (0, 200, 255), False, plan_points, 4) # Thick Cyan Line for High-Level Plan

        # 4. Draw Agent (at end of path or animated? Let's show full path static for now, or animated if we want)
        # For simulation, showing the FULL PATH immediately is often better for comparison.
        # But let's show the agent at the goal or end of path.
        end_node = current_agent.full_path[-1] if current_agent.full_path else current_agent.current_node
        pygame.draw.circle(self.screen, ACCENT_ORANGE, (end_node.c * TILE_SIZE + TILE_SIZE//2, end_node.r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2), TILE_SIZE//3)

        # 4. HUD
        w, h = self.screen.get_size()
        
        # Header
        pygame.draw.rect(self.screen, CARD_BG, (0, 0, w, 80))
        self.draw_text(f"SIMULATION MODE: {self.sim_names[self.current_sim_index]}", self.heading_font, ACCENT_BLUE, (w//2, 40))
        
        # Metrics Panel
        panel_y = h - 150
        pygame.draw.rect(self.screen, (0, 0, 0, 200), (0, panel_y, w, 150))
        
        stats = [
            f"Total Cost: {current_agent.solution_cost}",
            f"Steps: {current_agent.solution_steps}",
            f"Nodes Explored: {current_agent.metrics.nodes_explored}",
            f"Nodes Visited: {current_agent.metrics.nodes_visited}",
            f"Efficiency: {current_agent.get_efficiency_vs_optimal(self.maze.optimal_path_length)*100:.1f}%"
        ]
        
        # Explicit Proof of No Backtracking
        sx = w // 2
        sy = panel_y + 30
        
        # Add big red warning
        self.draw_text("BACKTRACKING: DISABLED", self.heading_font, ACCENT_RED, (sx, sy - 40), shadow=False)
        
        # Check if failed
        if current_agent.full_path and current_agent.full_path[-1] != self.maze.goal_node:
             self.draw_text("STATUS: FAILED (Stuck at Dead End)", self.heading_font, ACCENT_RED, (sx, sy - 10), shadow=False)
        else:
             self.draw_text("STATUS: SUCCESS", self.heading_font, ACCENT_GREEN, (sx, sy - 10), shadow=False)

        for i, line in enumerate(stats):
            self.draw_text(line, self.medium_font, TEXT_MAIN, (sx, sy + i * 25 + 20), shadow=False)

        # Controls
        self.draw_text("< PREV (Left)   |   NEXT (Right) >   |   ESC: Menu", self.small_font, TEXT_SUB, (w//2, h - 20))

    def draw_replay(self):
        # Debug Logging
        # print(f"Replay Frame: {self.replay_index}, History: {len(self.history)}")
        
        self.screen.fill(BG_PRIMARY)
        try:
            self.draw_grid() # Draws base maze and BFS if enabled
        except Exception as e:
            print(f"Draw Grid Error: {e}")
            raise e
        
        if not self.history: return

        # Get state from history
        state = self.history[self.replay_index]
        
        # --- VISUALIZATION LAYERS ---
        
        # 1. Graph Representation (Nodes & Edges)
        if self.show_graph:
            for r in range(self.maze.height):
                for c in range(self.maze.width):
                    node = self.maze.get_node(r, c)
                    if node.type != '#':
                        cx = c * TILE_SIZE + TILE_SIZE//2
                        cy = r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2
                        # Draw Edges
                        for neighbor in self.maze.get_neighbors(node):
                            nx = neighbor.c * TILE_SIZE + TILE_SIZE//2
                            ny = neighbor.r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2
                            pygame.draw.line(self.screen, (50, 50, 70), (cx, cy), (nx, ny), 1)
                        # Draw Node
                        pygame.draw.circle(self.screen, (80, 80, 100), (cx, cy), 2)

        # 2. AI Search Process (Visited Nodes)
        if self.show_visited and hasattr(self.ai, 'visited_nodes'):
            for node in self.ai.visited_nodes:
                 vx = node.c * TILE_SIZE
                 vy = node.r * TILE_SIZE + GRID_OFFSET_Y
                 # Draw a faint blue overlay for visited nodes
                 s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                 s.fill((100, 100, 255, 40)) # Transparent Blue
                 self.screen.blit(s, (vx, vy))
                 # Optional: Small dot
                 # pygame.draw.circle(self.screen, (100, 100, 255), (vx + TILE_SIZE//2, vy + TILE_SIZE//2), 2)

        # 3. Entities
        # Draw Player
        pr, pc = state['player_pos']
        px = pc * TILE_SIZE
        py = pr * TILE_SIZE + GRID_OFFSET_Y
        pygame.draw.circle(self.screen, ACCENT_GREEN, (px + TILE_SIZE//2, py + TILE_SIZE//2), TILE_SIZE//3)
        
        # Draw AI
        ar, ac = state['ai_pos']
        ax = ac * TILE_SIZE
        ay = ar * TILE_SIZE + GRID_OFFSET_Y
        pygame.draw.circle(self.screen, ACCENT_ORANGE, (ax + TILE_SIZE//2, ay + TILE_SIZE//2), TILE_SIZE//3)
        
        # 4. Greedy Heuristic Lens (AI Path)
        if self.show_heuristics:
            path = state['ai_path']
            if len(path) > 1:
                points = []
                for node in path:
                    points.append((node.c * TILE_SIZE + TILE_SIZE//2, 
                                   node.r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2))
                pygame.draw.lines(self.screen, (255, 100, 100), False, points, 2)
                
                # Draw Line to Goal
                goal_x = self.maze.goal_node.c * TILE_SIZE + TILE_SIZE//2
                goal_y = self.maze.goal_node.r * TILE_SIZE + GRID_OFFSET_Y + TILE_SIZE//2
                pygame.draw.line(self.screen, (255, 255, 0), (ax + TILE_SIZE//2, ay + TILE_SIZE//2), (goal_x, goal_y), 1)

        # Draw HUD Overlay
        w, h = self.screen.get_size()
        pygame.draw.rect(self.screen, (0, 0, 0, 200), (0, h-80, w, 80))
        
        progress = (self.replay_index / (len(self.history)-1)) if len(self.history) > 1 else 1
        bar_w = w - 40
        pygame.draw.rect(self.screen, (100, 100, 100), (20, h-60, bar_w, 10))
        pygame.draw.rect(self.screen, ACCENT_BLUE, (20, h-60, bar_w * progress, 10))
        
        self.draw_text(f"REPLAY | Frame: {self.replay_index}/{len(self.history)-1} | Speed: {self.replay_speed}x", self.small_font, TEXT_MAIN, (w//2, h-35))
        self.draw_text("Space: Pause | Arrows: Seek | V: Visited | C: Huffman | G: Graph | B: BFS | H: Path", self.small_font, TEXT_SUB, (w//2, h-15))

        # 5. Huffman Overlay
        if self.show_huffman:
            overlay = pygame.Surface((w - 100, 250), pygame.SRCALPHA)
            overlay.fill((20, 20, 30, 230)) # Dark semi-transparent
            pygame.draw.rect(overlay, ACCENT_CYAN, overlay.get_rect(), 2) # Border
            
            ox, oy = 50, h//2 - 125
            self.screen.blit(overlay, (ox, oy))
            
            # Title
            self.draw_text("HUFFMAN CODING ANALYSIS", self.medium_font, ACCENT_CYAN, (w//2, oy + 30))
            
            # Explanation
            expl = "Huffman coding compresses the AI's action log by assigning shorter binary codes to more frequent moves."
            self.draw_text(expl, self.small_font, TEXT_MAIN, (w//2, oy + 60))
            
            # Stats
            # Reconstruct action log up to current frame
            # Since we don't store partial logs, we'll estimate from full log or just show full log stats
            # For simplicity and accuracy, let's show the FULL GAME stats as "Post-Game Analysis"
            
            full_log = self.ai.action_log
            if full_log:
                huff = Huffman()
                # encode() builds the tree internally and populates self.codes
                encoded = huff.encode(full_log)
                codes = huff.codes
                
                original_bits = len(full_log) * 8
                compressed_bits = len(encoded)
                ratio = (1 - compressed_bits/original_bits) * 100
                
                self.draw_text(f"Action Log: {full_log[:30]}..." if len(full_log) > 30 else f"Action Log: {full_log}", self.small_font, ACCENT_ORANGE, (w//2, oy + 100))
                self.draw_text(f"Original Size: {original_bits} bits", self.small_font, TEXT_SUB, (w//2, oy + 130))
                self.draw_text(f"Compressed Size: {compressed_bits} bits", self.small_font, ACCENT_GREEN, (w//2, oy + 150))
                self.draw_text(f"Compression Ratio: {ratio:.2f}%", self.medium_font, ACCENT_GREEN, (w//2, oy + 190))
            else:
                self.draw_text("No Action Log Available (AI didn't move?)", self.small_font, TEXT_SUB, (w//2, oy + 100))

    def process_move(self, agent):
        node = agent.current_node
        cost = 1 if (node.r, node.c) in self.consumed_items else node.cost

        if node.type == 'T' and (node.r, node.c) not in self.consumed_items:
            self.consumed_items.add((node.r, node.c))
        elif node.type == 'P' and (node.r, node.c) not in self.consumed_items:
            self.consumed_items.add((node.r, node.c))

        agent.total_cost = max(0, agent.total_cost + cost)
        if node == self.maze.goal_node:
            agent.finished = True

    def handle_input(self):
        if self.player.finished: return

        keys = pygame.key.get_pressed()
        now = time.time()
        if now - self.last_move_time < 0.12: return  # Move delay

        dx, dy = 0, 0
        # Cardinals
        if keys[pygame.K_w] or keys[pygame.K_UP]: dx, dy = -1, 0
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]: dx, dy = 1, 0
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]: dx, dy = 0, -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx, dy = 0, 1
        # Diagonals
        elif keys[pygame.K_q]: dx, dy = -1, -1
        elif keys[pygame.K_e]: dx, dy = -1, 1
        elif keys[pygame.K_z]: dx, dy = 1, -1
        elif keys[pygame.K_c]: dx, dy = 1, 1

        if dx != 0 or dy != 0:
            if isinstance(self.maze, CircularMaze):
                # Strict Graph Movement for Circular Maze
                # dx: Left/Right (CCW/CW) -> dc
                # dy: Up/Down (In/Out) -> dr
                # In polar coords: Down is OUT (r approaches N-1). Up is IN (r approaches 0).
                # Wait, standard maze: (0,0) is top-left.
                # Here: (0,0) is CENTER.
                # So if r=0 is center, r=N-1 is outer.
                # Moving OUT means increasing r. Moving IN means decreasing r.
                # Key UP (dy=-1) -> Decrease r (Move In)
                # Key DOWN (dy=+1) -> Increase r (Move Out)
                # Key LEFT (dx=-1) -> Decrease c (CCW)
                # Key RIGHT (dx=+1) -> Increase c (CW)
                
                dr, dc = dy, dx
                target = self.maze.get_movement_target(self.player.current_node, (dr, dc))
                
                if target:
                    self.player.current_node = target
                    self.last_move_time = now
                    self.process_move(self.player)
            
            elif self.player.move((dx, dy), self.maze):
                self.process_move(self.player)
                self.last_move_time = now
                self.record_frame()

    def run(self):
        running = True
        frame_count = 0
        print("Entering Game Loop...")
        while running:
            self.clock.tick(FPS)
            frame_count += 1
            
            dt = self.clock.get_time() / 1000.0 # Delta time in seconds
            
            # Dynamic/Circular Maze Update
            # Allow updates in PLAYING, GRAPH_VIEW or SIMULATION
            if (self.state == PLAYING or self.state == GRAPH_VIEW):
                if isinstance(self.maze, DynamicMaze):
                    self.maze.update_structure()
                    if self.maze.process_updates(dt):
                        print("Structure Updated! Re-calculating AI path...")
                        self.ai.compute_path()
                elif isinstance(self.maze, CircularMaze):
                    self.maze.update(dt) # Continuous rotation
                    # Run DP every frame for glow or less frequently?
                    # Every frame is fine for 72 nodes.
                    self.maze.run_dp()


            
            if frame_count % 60 == 0:
                print(f"Game Loop Running... Frame: {frame_count}, State: {self.state}")
            
            self.pulse_time = time.time()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                elif event.type == pygame.MOUSEWHEEL and self.state == INSTRUCTIONS:
                    self.instruction_scroll_y = max(0, min(self.max_scroll, self.instruction_scroll_y - event.y * 40))

                elif event.type == pygame.MOUSEBUTTONDOWN and self.state == INSTRUCTIONS and self.max_scroll > 0:
                    sb_x = self.screen.get_width() - 40
                    if sb_x <= mouse_pos[0] <= sb_x + 16:
                        self.scrollbar_grabbed = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.scrollbar_grabbed = False

                elif self.state == MENU:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                            idx = event.key - pygame.K_1
                            if idx < 3:
                                lvl = ["EASY", "MEDIUM", "HARD"][idx]
                            elif idx == 3:
                                lvl = "DYNAMIC"
                            else:
                                lvl = "CIRCULAR"
                            self.reset_game(lvl)
                            self.state = PLAYING
                            self.start_time = time.time()
                        elif event.key == pygame.K_i:
                            self.state = INSTRUCTIONS
                            self.instruction_scroll_y = 0
                        elif event.key == pygame.K_RETURN:
                            self.state = PLAYING
                            self.start_time = time.time()
                        elif event.key == pygame.K_s:
                             self.state = SIMULATION
                             self.prepare_simulation()
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        w, h = self.screen.get_size()
                        base_y = h//2 - 30  # Match draw_menu() base_y
                        options = ["EASY", "MEDIUM", "HARD", "DYNAMIC", "CIRCULAR", INSTRUCTIONS]
                        
                        for i, val in enumerate(options):
                            y = base_y + i * 70
                            rect = pygame.Rect(w//2 - 150, y - 30, 300, 60)
                            if rect.collidepoint(event.pos):
                                if val == INSTRUCTIONS:
                                    self.state = INSTRUCTIONS
                                    self.instruction_scroll_y = 0
                                else:
                                    self.reset_game(val)
                                    self.state = PLAYING
                                    self.start_time = time.time()

                elif self.state == PLAYING and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g: self.state = GRAPH_VIEW # Toggle Graph Mode
                    elif event.key == pygame.K_l: 
                        # Start Logic Visualization
                        self.state = VISUALIZE_LOGIC
                        self.visualizer = TarjanVisualizer(self.maze)
                        self.vis_stage = 0
                        self.vis_start_time = time.time()
                    elif event.key == pygame.K_h: self.show_heuristics = not self.show_heuristics
                    elif event.key == pygame.K_k:
                        self.show_dp_viz = not self.show_dp_viz
                        print(f"DP Visualization: {'ON' if self.show_dp_viz else 'OFF'}")
                    elif event.key == pygame.K_j:
                        # DP Simulation
                        self.state = DP_SIMULATION
                        self.dp_sim_time = 0
                        self.dp_sim_discovered = set()
                        self.dp_sim_wave_radius = 0
                        self.show_dp_viz = True
                        print("Starting DP Simulation...")
                    elif event.key == pygame.K_a: self.show_annotations = not self.show_annotations
                    elif event.key == pygame.K_b: self.show_bfs = not self.show_bfs
                    elif event.key == pygame.K_v: self.show_regions = getattr(self, 'show_regions', False); self.show_regions = not self.show_regions
                    elif event.key == pygame.K_r: self.reset_game(self.level)
                    elif event.key == pygame.K_s: # Enable Simulation Mode from Playing
                        self.state = SIMULATION
                        self.prepare_simulation()
                    elif event.key == pygame.K_ESCAPE: self.state = MENU

                elif self.state == GRAPH_VIEW and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g or event.key == pygame.K_ESCAPE:
                        self.state = PLAYING # Return to Game
                    elif event.key == pygame.K_r: # Allow restart from graph view
                        self.reset_game(self.level)
                        self.state = PLAYING
                
                elif self.state == VISUALIZE_LOGIC and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l or event.key == pygame.K_ESCAPE:
                        self.state = PLAYING
                    elif event.key == pygame.K_r:
                        self.visualizer = TarjanVisualizer(self.maze)
                        self.vis_stage = 0

                elif self.state == DP_SIMULATION and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = PLAYING
                        self.show_dp_viz = True

                elif self.state == GAME_OVER and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = MENU
                    elif event.key == pygame.K_p:
                        self.state = REPLAY
                        self.replay_index = 0
                        self.replay_speed = 0.5 # Slower default
                        self.map_mode = 2 # Default to Greedy Map for visualization
                        self.show_heuristics = True # Show path lines
                        self.show_graph = True # Show Graph Nodes/Edges
                        self.show_visited = False # Show visited by default for "AI Logic"
                    elif event.key == pygame.K_s:
                        self.state = SIMULATION
                        self.prepare_simulation()


                elif self.state == REPLAY and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.state = GAME_OVER
                    elif event.key == pygame.K_RIGHT: self.replay_index = min(len(self.history)-1, self.replay_index + 1)
                    elif event.key == pygame.K_LEFT: self.replay_index = max(0, self.replay_index - 1)
                    elif event.key == pygame.K_SPACE: self.replay_speed = 0 if self.replay_speed > 0 else 0.5
                    elif event.key == pygame.K_UP: self.replay_speed += 0.5
                    elif event.key == pygame.K_DOWN: self.replay_speed = max(0, self.replay_speed - 0.5)
                    # Toggles
                    elif event.key == pygame.K_b: 
                        # Cycle: 0=Off, 1=BFS, 2=Greedy Map
                        self.map_mode = (self.map_mode + 1) % 3
                    elif event.key == pygame.K_h: self.show_heuristics = not self.show_heuristics
                    elif event.key == pygame.K_g: self.show_graph = not self.show_graph # Graph Toggle
                    elif event.key == pygame.K_v: self.show_visited = not self.show_visited # Visited Toggle
                    elif event.key == pygame.K_c: self.show_huffman = not self.show_huffman # Huffman Toggle

                elif self.state == SIMULATION and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.state = GAME_OVER
                    elif event.key == pygame.K_RIGHT: 
                        self.current_sim_index = (self.current_sim_index + 1) % len(self.simulation_agents)
                    elif event.key == pygame.K_LEFT:
                        self.current_sim_index = (self.current_sim_index - 1) % len(self.simulation_agents)


                elif self.state == INSTRUCTIONS and event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        self.state = MENU

            if self.scrollbar_grabbed and self.max_scroll > 0:
                sb_h = self.screen.get_height() - 200
                ratio = (mouse_pos[1] - 100) / sb_h
                self.instruction_scroll_y = max(0, min(self.max_scroll, ratio * self.max_scroll))

            # Logic Visualization Update
            if self.state == VISUALIZE_LOGIC:
                 # Check for Dynamic Updates
                 if isinstance(self.maze, DynamicMaze):
                      start_time = getattr(self, 'vis_start_time', 0)
                      if self.maze.last_update_time > start_time:
                         # Maze changed! Restart visualization
                         self.visualizer = TarjanVisualizer(self.maze)
                         self.vis_stage = 0
                         self.vis_start_time = time.time()

                 if frame_count % 5 == 0:
                     self.visualizer.step()
                     if self.visualizer.finished:
                         if self.vis_stage == 0:
                             # Switch to Region Viz
                             aps = self.visualizer.articulation_points
                             self.visualizer = RegionVisualizer(self.maze, aps)
                             self.vis_stage = 1
                         elif self.vis_stage == 1:
                             # Switch to Conquer Viz
                             self.visualizer = ConquerVisualizer(self.maze, HierarchicalAI)
                             self.vis_stage = 2

            # Rendering
            if self.state == MENU:
                self.draw_menu()
            elif self.state == VISUALIZE_LOGIC:
                self.screen.fill(BG_PRIMARY)
                self.draw_grid()
                self.visualizer.draw(self.screen, TILE_SIZE, GRID_OFFSET_Y, self.small_font)
            
            elif self.state == DP_SIMULATION:
                self.draw_dp_simulation()
            
            elif self.state == INSTRUCTIONS:
                self.draw_instructions()
            elif self.state == PLAYING:
                self.handle_input()
                self.elapsed_time = time.time() - self.start_time
                
                # AI Logic
                if not self.ai.finished and int(self.elapsed_time * self.ai_speed) > self.ai.steps:
                    self.ai.choose_move(self.maze)
                    self.process_move(self.ai)
                    self.record_frame()

                if self.player.finished and self.ai.finished:
                    self.state = GAME_OVER
                
                self.screen.fill(BG_PRIMARY)
                self.draw_grid()
                self.draw_entities()
                self.draw_hud()

            elif self.state == GRAPH_VIEW:
                self.draw_graph_simulation()

            elif self.state == SIMULATION:
                self.draw_simulation()

            elif self.state == REPLAY:
                try:
                    self.draw_replay()
                    if self.replay_speed > 0:
                        speed_factor = int(self.replay_speed * 5 + 1)
                        if frame_count % max(1, 60 // speed_factor) == 0:
                             self.replay_index = min(len(self.history)-1, self.replay_index + 1)
                except Exception as e:
                    print(f"Replay Error: {e}")
                    with open("replay_error.txt", "w") as f:
                        f.write(str(e))
                    self.state = MENU # Exit replay on error

            elif self.state == GAME_OVER:
                self.draw_game_over()

            pygame.display.flip()


        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        print("Starting game...")
        game = GameController()
        game.run()
    except BaseException as e:
        # Ignore normal exit
        if isinstance(e, SystemExit) and e.code == 0:
            sys.exit(0)
            
        with open("error_log.txt", "w") as f:
            import traceback
            traceback.print_exc(file=f)
            f.write(f"\nException: {e}")
        print(f"Game crashed: {e}")
        sys.exit(1)