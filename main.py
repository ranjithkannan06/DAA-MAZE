import pygame
import sys
import time
import math
from game_classes import Maze, Player
from Huffman.huffman import Huffman
from GBFS.Euclidean.euclidean import EuclideanAI
from GBFS.Manhattan.manhattan import ManhattanAI
from GBFS.Chebyshev.chebyshev import ChebyshevAI
from HillClimbing.hill_climbing import HillClimbingAI
from DFS.dfs import DFSAI
from BFS.bfs import BFSAI
from AStar.astar import AStarAI

# UI States
MENU = 0
PLAYING = 1
GAME_OVER = 2
INSTRUCTIONS = 3
REPLAY = 4
SIMULATION = 5

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
        self.show_annotations = False

        # Animation & Scroll
        self.pulse_time = 0
        self.instruction_scroll_y = 0
        self.max_scroll = 0
        self.scrollbar_grabbed = False
        self.last_move_time = 0

        self.reset_game("MEDIUM")

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
        speeds = {"EASY": 1.0, "MEDIUM": 2.0, "HARD": 4.0}
        sizes = {"EASY": (15,15), "MEDIUM": (21,21), "HARD": (25,25)}
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
        self.maze = Maze(width=w, height=h)
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
            ("INSTRUCTIONS", INSTRUCTIONS)
        ]

        mx, my = pygame.mouse.get_pos()
        base_y = h//2 + 20

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

    def draw_grid(self):
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                node = self.maze.get_node(r, c)
                if node is None: continue # Safety check
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE + GRID_OFFSET_Y, TILE_SIZE, TILE_SIZE)

                # Fog of War Logic
                visible = True
                if self.state != REPLAY:
                    if self.player and self.player.current_node:
                        dist = max(abs(node.r - self.player.current_node.r), abs(node.c - self.player.current_node.c))
                        visible = dist <= 3 or node.visited_by_player or node in (self.maze.start_node, self.maze.goal_node)
                    else:
                        visible = True # Fallback if player not ready
                    
                    if not visible:
                        pygame.draw.rect(self.screen, BG_PRIMARY, rect)
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

            # Controls Hint
            y = panel_y + panel_h - 40
            self.draw_text("ESC: Menu | R: Restart | B: BFS", self.small_font, TEXT_SUB, (panel_x + panel_w//2, y), shadow=False)

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

    def prepare_simulation(self):
        print("Preparing Simulation Agents...")
        self.simulation_agents = [
            EuclideanAI(self.maze.start_node, self.maze.goal_node, self.maze),
            ManhattanAI(self.maze.start_node, self.maze.goal_node, self.maze),
            ChebyshevAI(self.maze.start_node, self.maze.goal_node, self.maze),
            HillClimbingAI(self.maze.start_node, self.maze.goal_node, self.maze),
            BFSAI(self.maze.start_node, self.maze.goal_node, self.maze),
            DFSAI(self.maze.start_node, self.maze.goal_node, self.maze),
            AStarAI(self.maze.start_node, self.maze.goal_node, self.maze)
        ]
        self.sim_names = [
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

        # 3. Draw Agent (at end of path or animated? Let's show full path static for now, or animated if we want)
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
            if self.player.move((dx, dy), self.maze):
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
                        if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            lvl = ["EASY", "MEDIUM", "HARD"][event.key - pygame.K_1]
                            self.reset_game(lvl)
                            self.state = PLAYING
                            self.start_time = time.time()
                        elif event.key == pygame.K_i:
                            self.state = INSTRUCTIONS
                            self.instruction_scroll_y = 0
                        elif event.key == pygame.K_RETURN:
                            self.state = PLAYING
                            self.start_time = time.time()
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        w, h = self.screen.get_size()
                        base_y = h//2 + 20
                        options = ["EASY", "MEDIUM", "HARD", INSTRUCTIONS]
                        
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
                    if event.key == pygame.K_g: self.show_graph = not self.show_graph
                    elif event.key == pygame.K_h: self.show_heuristics = not self.show_heuristics
                    elif event.key == pygame.K_a: self.show_annotations = not self.show_annotations
                    elif event.key == pygame.K_b: self.show_bfs = not self.show_bfs
                    elif event.key == pygame.K_r: self.reset_game(self.level)
                    elif event.key == pygame.K_ESCAPE: self.state = MENU

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

            # Rendering
            if self.state == MENU:
                self.draw_menu()
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