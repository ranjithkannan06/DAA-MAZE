import pygame
import math
import time

class AnalysisUI:
    """
    UI Wrapper handling rendering overlays for Backtracking and Complexity.
    Refactored to distribute rendering logic equally across 4 team members.
    """
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
        
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
    # ==== MEMBER 1 SECTION ====
    # Responsibility: Dead-End Animation Polish
    # ==========================================
    
    def draw_dead_end_flash(self, current_node, status, offset_y, tile_size):
        """Draws the flashing pulsing red beacon when a dead end is struck."""
        if current_node and status == "DEAD_END":
             cx = current_node.c * tile_size + tile_size//2
             cy = current_node.r * tile_size + tile_size//2 + offset_y
             
             # Flash red pulse
             pulse = int(abs(math.sin(time.time() * 10)) * 255)
             pygame.draw.circle(self.screen, (pulse, 0, 0), (cx, cy), tile_size//2 + 4)
             
             self.draw_text("Dead End Reached", self.fonts['small'], (255, 100, 100), (cx, cy - tile_size), shadow=True)
             
             # Dark red circle with X
             pygame.draw.circle(self.screen, (100, 0, 0), (cx, cy), tile_size//2)
             pygame.draw.line(self.screen, (255, 255, 255), (cx-5, cy-5), (cx+5, cy+5), 2)
             pygame.draw.line(self.screen, (255, 255, 255), (cx-5, cy+5), (cx+5, cy-5), 2)
         
    # ==========================================
    # ==== MEMBER 2 SECTION ====
    # Responsibility: Stack Visual Refinement
    # ==========================================
    
    def draw_ai_stack(self, stack, status, w, h):
        """Draws the shrinking/growing AI array natively on the screen."""
        stack_w = 120
        stack_x = w - stack_w - 20
        stack_y = 80
        stack_h = min(400, h - 200)
        
        pygame.draw.rect(self.screen, (20, 20, 25, 200), (stack_x, stack_y, stack_w, stack_h))
        self.draw_text("AI Stack", self.fonts['medium'], (150, 200, 255), (stack_x + stack_w//2, stack_y + 20), shadow=False)
        
        sy = stack_y + 50
        display_limit = (stack_h - 60) // 25
        visible_stack = list(reversed(stack))[:display_limit]
        
        for idx, (node, _) in enumerate(visible_stack):
            text = f"[ ({node.r}, {node.c}) ]"
            color = (150, 255, 150) if idx == 0 and status != "BACKTRACK" else (180, 180, 180)
            y_offset = 0
            
            if idx == 0 and status == "BACKTRACK":
                 color = (255, 80, 80) # Strong Red fade out intent
                 y_offset = 12 # Slide down animation slightly
                 
            self.draw_text(text, self.fonts['small'], color, (stack_x + stack_w//2, sy + y_offset), shadow=False)
            sy += 25
  # ==========================================
    # ==== MEMBER 3 SECTION ====
    # Responsibility: Live Graph Rendering Polish
    # ==========================================
    
    def draw_live_analysis_graph(self, x_start, w, h, metrics, current_metric, metric_titles):
        """Standard 'T' key graph parsing real-time tracking history."""
        analysis_w = w - x_start
        analysis_surface = pygame.Surface((analysis_w, h))
        analysis_surface.fill((255, 255, 255))
        self.screen.blit(analysis_surface, (x_start, 0))
        
        pygame.draw.rect(self.screen, (150, 150, 150), pygame.Rect(x_start, 0, analysis_w, h), 2)
        
        if not metrics:
            self.draw_text("Waiting for Simulation Data...", self.fonts['medium'], (100, 100, 100), (x_start + analysis_w//2, h//2))
            return
            
        last_snap = metrics[-1]
        
        # Draw the top Header and live tracking text block
        self.draw_text("Live Runtime Analysis", self.fonts['large'], (0, 0, 0), (x_start + analysis_w//2, 40), shadow=False)
        
        # Draw stats
        stats_x = x_start + 40
        stats_y = h - 220
        self.draw_text("LIVE METRICS", self.fonts['medium'], (0, 0, 0), (stats_x, stats_y), anchor="topleft", shadow=False)
        pygame.draw.line(self.screen, (150, 150, 150), (stats_x, stats_y + 35), (w - 40, stats_y + 35), 2)
        
        row_space = 25
        self.draw_text("Steps:", self.fonts['mono'], (40, 40, 40), (stats_x, stats_y + 50), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['step']}", self.fonts['mono'], (0, 0, 0), (stats_x + 200, stats_y + 50), anchor="topleft", shadow=False)
        self.draw_text("Nodes Explored:", self.fonts['mono'], (40, 40, 40), (stats_x, stats_y + 50 + row_space), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['nodes']}", self.fonts['mono'], (0, 0, 0), (stats_x + 200, stats_y + 50 + row_space), anchor="topleft", shadow=False)
        self.draw_text("Backtracks:", self.fonts['mono'], (40, 40, 40), (stats_x, stats_y + 50 + row_space*2), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['backtracks']}", self.fonts['mono'], (0, 0, 0), (stats_x + 200, stats_y + 50 + row_space*2), anchor="topleft", shadow=False)
        self.draw_text("Stack Depth:", self.fonts['mono'], (40, 40, 40), (stats_x, stats_y + 50 + row_space*3), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['stack_depth']}", self.fonts['mono'], (0, 0, 0), (stats_x + 200, stats_y + 50 + row_space*3), anchor="topleft", shadow=False)
        self.draw_text("Runtime (ms):", self.fonts['mono'], (40, 40, 40), (stats_x, stats_y + 50 + row_space*4), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['runtime']:.1f}", self.fonts['mono'], (0, 0, 0), (stats_x + 200, stats_y + 50 + row_space*4), anchor="topleft", shadow=False)

        # Draw the graph mapping bounds
        graph_x = x_start + 50
        graph_y = 140
        graph_w = analysis_w - 100
        graph_h = stats_y - graph_y - 40
        
        pygame.draw.line(self.screen, (100, 100, 100), (graph_x, graph_y - 20), (graph_x, graph_y + graph_h), 2) # Y-Axis
        pygame.draw.line(self.screen, (100, 100, 100), (graph_x, graph_y + graph_h), (graph_x + graph_w + 20, graph_y + graph_h), 2) # X-Axis
        self.draw_text(metric_titles[current_metric], self.fonts['medium'], (100, 100, 100), (graph_x + 10, graph_y - 20), anchor="topleft", shadow=False)
        self.draw_text("Step Count", self.fonts['medium'], (100, 100, 100), (graph_x + graph_w - 80, graph_y + graph_h + 15), anchor="topleft", shadow=False)
        
        if len(metrics) >= 2:
            max_step = metrics[-1]['step']
            max_y = max(m[current_metric] for m in metrics)
            if max_y == 0: max_y = 1
            
            points = []
            for m in metrics:
                px = graph_x + (m['step'] / max_step) * graph_w
                py = graph_y + graph_h - (m[current_metric] / max_y) * graph_h
                points.append((px, py))
                if m['state'] == "BACKTRACK":
                    pygame.draw.circle(self.screen, (255, 150, 150, 150), (int(px), int(py)), 8)
                    pygame.draw.circle(self.screen, (220, 30, 30), (int(px), int(py)), 4)
                    
            pygame.draw.lines(self.screen, (30, 80, 200), False, points, 4)



    # ==========================================
    # ==== MEMBER 4 SECTION ====
    # Responsibility: Complexity Screen Layout Polish
    # ==========================================
    
    def draw_complexity_comparison_panel(self, x_start, w, h, complexity_report, metrics, highlight_index):
        """Detailed structured UI Slide drawn for the 'C' Complexity comparison active mode."""
        analysis_w = w - x_start
        analysis_surface = pygame.Surface((analysis_w, h))
        analysis_surface.fill((255, 255, 255))
        self.screen.blit(analysis_surface, (x_start, 0))
        
        pygame.draw.rect(self.screen, (150, 150, 150), pygame.Rect(x_start, 0, analysis_w, h), 2)
        
        if not complexity_report or not metrics:
            return
            
        margin_x = 30
        cursor_y = 30
        last_snap = metrics[-1]
        total_backtracks = len([m for m in metrics if m.get('state') == 'BACKTRACK'])
        gr = complexity_report['grid_theory']
        
        # Title
        self.draw_text("COMPLEXITY COMPARISON MODE", self.fonts['large'], (20, 20, 150), (x_start + analysis_w//2, cursor_y), shadow=False)
        self.draw_text("Use LEFT/RIGHT arrows to step through red backtracks", self.fonts['small'], (100, 100, 100), (x_start + analysis_w//2, cursor_y + 25), shadow=False)
        pygame.draw.line(self.screen, (200, 200, 200), (x_start + margin_x, cursor_y + 40), (w - margin_x, cursor_y + 40), 2)
        cursor_y += 60
        
        # 1. LIVE STATS / WHAT HAPPENED IN GAME
        self.draw_text("1. What Happened In-Game", self.fonts['medium'], (0, 0, 0), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 25
        col1_x = x_start + margin_x
        col2_x = x_start + margin_x + 200
        row_h = 22
        
        self.draw_text("Total Steps Taken:", self.fonts['mono'], (40, 40, 40), (col1_x, cursor_y), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['step']}", self.fonts['mono'], (0, 0, 0), (col2_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += row_h
        self.draw_text("Nodes Explored:", self.fonts['mono'], (40, 40, 40), (col1_x, cursor_y), anchor="topleft", shadow=False)
        self.draw_text(f"{last_snap['nodes']}", self.fonts['mono'], (0, 0, 0), (col2_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += row_h
        self.draw_text("Backtracks:", self.fonts['mono'], (40, 40, 40), (col1_x, cursor_y), anchor="topleft", shadow=False)
        self.draw_text(f"{total_backtracks}", self.fonts['mono'], (200, 0, 0), (col2_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += row_h + 10
        
        self.draw_text(f"Grid Size (n) = {gr['n']}, Total Nodes = {gr['v_approx']}", self.fonts['mono'], (20, 100, 20), (col1_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += row_h
        self.draw_text("DFS explores most nodes in worst case.", self.fonts['small'], (80, 80, 80), (col1_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 35
        
        # 2. WHY BACKTRACKING INCREASED RUNTIME
        self.draw_text("2. Why Backtracking Increased Runtime", self.fonts['medium'], (0, 0, 0), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 30
        box_rect = pygame.Rect(x_start + margin_x, cursor_y, analysis_w - margin_x*2, 80)
        pygame.draw.rect(self.screen, (245, 245, 250), box_rect)
        pygame.draw.rect(self.screen, (180, 180, 200), box_rect, 1)
        
        expl_lines = [
            "- Deep branches -> More stack operations",
            "- More dead ends -> More retracing backwards",
            "- Retracing -> Additional step cost scaling with depth"
        ]
        ty = cursor_y + 10
        for line in expl_lines:
            self.draw_text(line, self.fonts['small'], (40, 40, 40), (x_start + margin_x + 10, ty), anchor="topleft", shadow=False)
            ty += 22
        cursor_y += 95
        
        # 3. BIG O
        self.draw_text("3. Theoretical Complexity", self.fonts['medium'], (0, 0, 0), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 30
        self.draw_text(f"DFS Time Complexity: {complexity_report['theory_label']}", self.fonts['mono'], (0, 0, 0), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 20
        self.draw_text(f"For Grid: V = n^2, E = 4n^2", self.fonts['mono'], (0, 0, 0), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 20
        self.draw_text(f"Therefore -> {gr['final_o']}", self.fonts['large'], (200, 50, 50), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 35
        self.draw_text("Within single maze, traversal grows linearly with steps.", self.fonts['small'], (80, 80, 80), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 18
        self.draw_text("Across increasing grid sizes, overall complexity is O(n^2).", self.fonts['small'], (80, 80, 80), (x_start + margin_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 35
        
        # 4. CHART WITH RED HIGHLIGHTS (Runtime vs Steps)
        graph_y = cursor_y
        graph_h = 130
        graph_w = analysis_w - margin_x * 2 - 20
        
        pygame.draw.line(self.screen, (100, 100, 100), (col1_x, graph_y), (col1_x, graph_y + graph_h), 2)
        pygame.draw.line(self.screen, (100, 100, 100), (col1_x, graph_y + graph_h), (col1_x + graph_w + 20, graph_y + graph_h), 2)
        self.draw_text("Time (ms)", self.fonts['small'], (100, 100, 100), (col1_x + 5, graph_y - 15), anchor="topleft", shadow=False)
        self.draw_text("Steps", self.fonts['small'], (100, 100, 100), (col1_x + graph_w - 30, graph_y + graph_h + 10), anchor="topleft", shadow=False)
        
        if len(metrics) > 1:
            max_step = metrics[-1]['step']
            max_y = max(m['runtime'] for m in metrics)
            if max_y <= 0: max_y = 1
            max_y = max_y * 1.1 # Add 10% vertical padding so graph isn't crushed to roof
            
            # Draw tick marks
            for i in range(1, 6):
                lx = col1_x + (i / 5) * graph_w
                pygame.draw.line(self.screen, (200, 200, 200), (lx, graph_y), (lx, graph_y + graph_h), 1)
                
            points = []
            for m in metrics:
                px = col1_x + (m['step'] / max_step) * graph_w
                py = graph_y + graph_h - (m['runtime'] / max_y) * graph_h
                points.append((px, py))
                
            if len(points) > 1:
                pygame.draw.lines(self.screen, (30, 80, 200), False, points, 3)
            
            # Interactive Marker
            bt_count = 0
            for i, m in enumerate(metrics):
                if m.get('state') == 'BACKTRACK':
                    px = col1_x + (m['step'] / max_step) * graph_w
                    py = graph_y + graph_h - (m['runtime'] / max_y) * graph_h
                    if bt_count == highlight_index:
                        pygame.draw.circle(self.screen, (255, 0, 0, 100), (int(px), int(py)), 12)
                        pygame.draw.circle(self.screen, (255, 30, 30), (int(px), int(py)), 6)
                        pygame.draw.line(self.screen, (100, 100, 100), (px, py - 40), (px, py), 1)
                        self.draw_text(f"Spike #{highlight_index+1}", self.fonts['small'], (200, 0, 0), (px, py - 45), shadow=False)
                    else:
                        pygame.draw.circle(self.screen, (220, 30, 30), (int(px), int(py)), 3)
                    bt_count += 1
            
        cursor_y = graph_y + graph_h + 35
        self.draw_text("* Plotting actual runtime accumulation per step taken.", self.fonts['small'], (100, 100, 100), (col1_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 18
        self.draw_text("* Note the spikes in runtime when the AI hits deep dead ends.", self.fonts['small'], (100, 100, 100), (col1_x, cursor_y), anchor="topleft", shadow=False)
        cursor_y += 40
        
        # 5. FINAL RESULT
        summary = complexity_report['final_summary']
        summary_rect = pygame.Rect(x_start + 40, cursor_y, analysis_w - 80, 100)
        pygame.draw.rect(self.screen, (25, 25, 40), summary_rect, border_radius=8)
        self.draw_text("FINAL RESULT:", self.fonts['font'], (200, 200, 255), (x_start + analysis_w//2, cursor_y + 15), shadow=False)
        
        res_y = cursor_y + 35
        self.draw_text(f"Traversal Type: {summary['traversal']}  |  Grid Representation: V = n^2", self.fonts['small'], (255, 255, 255), (x_start + analysis_w//2, res_y), shadow=False)
        self.draw_text(f"Observed Inter-step Growth: Linear  |  Total Nodes = {gr['v_approx']}", self.fonts['small'], (255, 255, 255), (x_start + analysis_w//2, res_y + 20), shadow=False)
        self.draw_text(f"Conclusion: {summary['conclusion']} across grid sizes", self.fonts['font'], (150, 255, 150), (x_start + analysis_w//2, res_y + 45), shadow=False)