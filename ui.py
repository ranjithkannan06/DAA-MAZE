import pygame
import math
from config import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        # Using more "Techie" fonts if available, otherwise defaulting to standard ones
        self.font_main = pygame.font.SysFont('Consolas', 36, bold=True)
        self.font_menu = pygame.font.SysFont('Consolas', 22, bold=True)
        self.font_small = pygame.font.SysFont('Consolas', 18)
        self.font_tiny = pygame.font.SysFont('Consolas', 14)
        self.font_mono = pygame.font.SysFont('Consolas', 12)
        
        self.pulse_val = 0
        self.opponents = [
            ("GBFS Chebyshev", "chebyshev", True),
            ("GBFS Manhattan", "manhattan", True),
            ("GBFS Euclidean", "euclidean", True),
            ("Hill Climbing", "chebyshev", False)
        ]

    def update_animations(self):
        self.pulse_val += ANIM_SPEED_PULSE

    def draw_glass_rect(self, rect, color, border_color=(0, 255, 128, 100), border_radius=5):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), border_radius=border_radius)
        self.screen.blit(shape_surf, (rect[0], rect[1]))
        # Techie border (double line or corner accents)
        pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=border_radius)

    def draw_tech_bg(self):
        # Draw dynamic background gradient
        for i in range(0, HEIGHT, 2):
            color = [
                COLOR_GRADIENT_START[j] + (COLOR_GRADIENT_END[j] - COLOR_GRADIENT_START[j]) * i // HEIGHT
                for j in range(3)
            ]
            pygame.draw.line(self.screen, color, (0, i), (WIDTH, i), 2)
        
        # Draw subtle grid
        for x in range(0, WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (WIDTH, y), 1)

    def draw_menu_ext(self, difficulty, opponent_idx):
        self.draw_tech_bg()
        self.draw_glass_rect((WIDTH // 2 - 380, 80, 760, 600), (20, 25, 30, 230), border_radius=0)
        
        title = self.font_main.render("> MAZE_RUNNER.EXE", True, COLOR_START)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        
        y = 200
        self.screen.blit(self.font_menu.render("[01] SYSTEM_DIFFICULTY", True, COLOR_START), (WIDTH // 2 - 320, y))
        y += 40
        for key, diff in DIFFICULTIES.items():
            is_selected = key == difficulty
            color = COLOR_PLAYER if is_selected else (100, 100, 100)
            status = "<< ACTIVE >>" if is_selected else "[ RELAXED ]"
            txt = self.font_small.render(f"   {key}: {diff['name'].upper()} {status}", True, color)
            self.screen.blit(txt, (WIDTH // 2 - 300, y))
            y += 30
            
        y += 30
        self.screen.blit(self.font_menu.render("[02] ADVERSARY_STRATEGY", True, COLOR_START), (WIDTH // 2 - 320, y))
        y += 40
        for i, (name, h, b) in enumerate(self.opponents):
            is_selected = i == opponent_idx
            color = COLOR_PLAYER if is_selected else (100, 100, 100)
            prefix = " > " if is_selected else "   "
            txt = self.font_small.render(f"{prefix}{name.upper()}", True, color)
            self.screen.blit(txt, (WIDTH // 2 - 300, y))
            y += 30
            
        y += 40
        instr_txt = self.font_small.render("PRESS [I] FOR MISSION_PROTOCOLS", True, COLOR_GOAL)
        pulse = (math.sin(self.pulse_val * 2) + 1) / 2
        instr_txt.set_alpha(int(150 + 105 * pulse))
        self.screen.blit(instr_txt, (WIDTH // 2 - instr_txt.get_width() // 2, y))

        start_txt = self.font_menu.render("INITIATE_RACE (PRESS_ENTER)", True, COLOR_START)
        self.screen.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, HEIGHT - 120))

    def draw_instructions(self):
        self.draw_tech_bg()
        self.draw_glass_rect((100, 100, WIDTH - 200, HEIGHT - 200), (15, 20, 25, 240), border_radius=0)
        
        y = 130
        title = self.font_main.render("> MISSION_PROTOCOLS", True, COLOR_GOAL)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, y))
        y += 80
        
        sections = [
            ("OBJECTIVE", "Reach the PURPLE_NODE before the Orange ADVERSARY."),
            ("SCORING", "Minimize STEPS and WEIGHTED_COST (Traps: 3, Powerups: -2)."),
            ("MOVEMENT", "W/A/S/D or ARROWS for cardinal. Q/E/Z/C for diagonals."),
            ("DATA", "Post-mission analysis includes HUFFMAN path compression."),
            ("SYSTEM", "[G] Graph, [H] Heuristics, [A] AI_Logic, [SPACE] Pause.")
        ]
        
        for sec, desc in sections:
            s_txt = self.font_menu.render(f"// {sec}:", True, COLOR_START)
            d_txt = self.font_small.render(desc, True, COLOR_TEXT)
            self.screen.blit(s_txt, (150, y))
            self.screen.blit(d_txt, (150, y + 30))
            y += 80
            
        exit_txt = self.font_small.render("PRESS [I] TO RETURN TO TERMINAL", True, COLOR_PLAYER)
        exit_txt.set_alpha(int(155 + 100 * math.sin(self.pulse_val * 3)))
        self.screen.blit(exit_txt, (WIDTH // 2 - exit_txt.get_width() // 2, HEIGHT - 150))

    def draw_metrics(self, stats):
        panel_rect = (WIDTH - UI_PANEL_WIDTH + 10, 10, UI_PANEL_WIDTH - 20, HEIGHT - 20)
        self.draw_glass_rect(panel_rect, (10, 15, 20, 220), border_radius=0)
        
        y = 40
        title = self.font_menu.render("DATA_STREAM", True, COLOR_START)
        self.screen.blit(title, (WIDTH - UI_PANEL_WIDTH + 30, y))
        y += 60
        
        for k, v in stats.items():
            label = self.font_mono.render(f"SYS.{k.replace(' ', '_').upper()}", True, (100, 120, 140))
            self.screen.blit(label, (WIDTH - UI_PANEL_WIDTH + 30, y))
            val_str = str(v) if not isinstance(v, float) else f"{v:.1f}"
            val = self.font_small.render(val_str, True, COLOR_TEXT)
            self.screen.blit(val, (WIDTH - UI_PANEL_WIDTH + 30, y + 15))
            y += 45
            
        y = HEIGHT - 200
        self.screen.blit(self.font_mono.render("CORE_CONTROLS", True, COLOR_GOAL), (WIDTH - UI_PANEL_WIDTH + 30, y))
        y += 25
        cmds = [("[WASD]", "MOVE"), ("[QEZC]", "DIAG"), ("[GHA]", "VIS"), ("[SPC]", "PAUSE")]
        for k, d in cmds:
            txt = self.font_tiny.render(f"{k} -> {d}", True, (150, 160, 180))
            self.screen.blit(txt, (WIDTH - UI_PANEL_WIDTH + 30, y))
            y += 20

    def draw_node_info(self, node, show_heuristic):
        if show_heuristic:
            txt = self.font_mono.render(str(int(node.heuristic)), True, COLOR_HEURISTIC)
            px = node.x * TILE_SIZE + TILE_SIZE // 2 - txt.get_width() // 2
            py = node.y * TILE_SIZE + TILE_SIZE // 2 - txt.get_height() // 2
            self.screen.blit(txt, (px, py))

    def draw_pulse_effect(self, x, y, color):
        s = (math.sin(self.pulse_val * 4) + 1) / 2
        radius = int(TILE_SIZE // 6 + (TILE_SIZE // 10) * s)
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, 150), (TILE_SIZE // 2, TILE_SIZE // 2), radius, 2)
        # Scanline effect on circle
        if int(self.pulse_val * 10) % 2 == 0:
            pygame.draw.line(surf, (*color, 100), (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 1)
        self.screen.blit(surf, (x * TILE_SIZE, y * TILE_SIZE))

    def draw_overlay(self, text, subtext=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 180))
        self.screen.blit(overlay, (0, 0))
        txt = self.font_main.render(f"> {text}", True, COLOR_TEXT)
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
        if subtext:
            st = self.font_small.render(subtext, True, COLOR_START)
            self.screen.blit(st, (WIDTH // 2 - st.get_width() // 2, HEIGHT // 2 + 20))

    def draw_game_over_scene(self, res, huffman_codes):
        self.draw_tech_bg()
        self.draw_glass_rect((WIDTH // 2 - 450, 50, 900, 700), (10, 15, 20, 240), border_radius=0)
        
        winner = res["Winner"]
        title_text = f"> MISSION_{'SUCCESS' if winner == 'Player' else 'FAIL'}"
        title_color = COLOR_START if winner == 'Player' else COLOR_TRAP
        self.screen.blit(self.font_main.render(title_text, True, title_color), (WIDTH // 2 - 400, 80))
        
        # Performance Comparison
        y = 160
        headers = ["METRIC", "OPERATOR (P)", "DRONE (AI)", "IDEAL (O)"]
        for i, h in enumerate(headers):
            txt = self.font_mono.render(h, True, COLOR_START)
            self.screen.blit(txt, (WIDTH // 2 - 380 + i*200, y))
        
        y += 30
        metrics = [
            ("QUANTUM_STEPS", res["Player Steps"], res["AI Steps"], res["Optimal Steps"]),
            ("RESOURCE_COST", res["Player Cost"], res["AI Cost"], res["Optimal Steps"]),
            ("HUFFMAN_SIZE", f"{res['Player Huffman Bits']}b", f"{res['AI Huffman Bits']}b", "-")
        ]
        
        for label, p, a, o in metrics:
            p_color, a_color = COLOR_PLAYER, COLOR_AI
            try:
                # Handle strings with 'b' like '45b'
                p_v = int(str(p).replace('b', ''))
                a_v = int(str(a).replace('b', ''))
                if p_v < a_v: p_color = COLOR_POWERUP
                elif a_v < p_v: a_color = COLOR_POWERUP
                elif p_v > a_v: p_color = COLOR_TRAP
                elif a_v > p_v: a_color = COLOR_TRAP
            except: pass

            self.screen.blit(self.font_mono.render(label, True, (150, 160, 180)), (WIDTH // 2 - 380, y))
            self.screen.blit(self.font_small.render(str(p), True, p_color), (WIDTH // 2 - 180, y))
            self.screen.blit(self.font_small.render(str(a), True, a_color), (WIDTH // 2 + 20, y))
            self.screen.blit(self.font_small.render(str(o), True, COLOR_START), (WIDTH // 2 + 220, y))
            y += 40
            
        # Highlight best values and victors
        y += 40
        self.screen.blit(self.font_menu.render(f"// STEPS_VICTOR: {res['Steps Winner']}", True, COLOR_START), (WIDTH // 2 - 380, y))
        y += 35
        self.screen.blit(self.font_menu.render(f"// RESOURCE_VICTOR: {res['Cost Winner']}", True, COLOR_START), (WIDTH // 2 - 380, y))
        
        y += 45
        self.screen.blit(self.font_menu.render("// HUFFMAN_CODE_MAPPINGS", True, COLOR_START), (WIDTH // 2 - 380, y))
        y += 40
        
        # Display directions mapping
        dir_map = {"0-1": "U", "01": "D", "-10": "L", "10": "R", "-1-1": "UL", "1-1": "UR", "-11": "DL", "11": "DR", "G": "G"}
        
        col = 0
        for char, code in huffman_codes.items():
            readable_char = dir_map.get(char, char)
            txt = self.font_mono.render(f"'{readable_char}': {code}", True, COLOR_TEXT)
            self.screen.blit(txt, (WIDTH // 2 - 380 + (col % 4) * 180, y + (col // 4) * 25))
            col += 1
            
        footer = self.font_menu.render("RETURN_TO_SYSTEM_HUB (ENTER)", True, COLOR_START)
        pulse = (math.sin(self.pulse_val * 2) + 1) / 2
        footer.set_alpha(int(150 + 105 * pulse))
        self.screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 100))

    def draw_ai_annotations(self, ai):
        for h, pos in ai.decision_annotations:
            nx, ny = pos
            rect = pygame.Rect(nx * TILE_SIZE, ny * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, (COLOR_ANNOTATION), rect, 1)
            txt = self.font_mono.render(f"H{int(h)}", True, COLOR_ANNOTATION)
            self.screen.blit(txt, (nx * TILE_SIZE + 2, ny * TILE_SIZE + 2))
