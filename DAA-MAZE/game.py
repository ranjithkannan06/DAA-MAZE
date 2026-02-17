import pygame
import sys
import math
from config import *
from maze import MazeGenerator
from ai import GreedyAI
from ui import UI
from Huffman.huffman import Huffman

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("MAZE_RUNNER.OS [v1.0.4]")
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.huffman = Huffman()
        
        self.state = "MENU"
        self.difficulty = "2"
        self.opponent_idx = 0
        
        self.maze_gen = None
        self.graph = None
        self.player_pos = (0, 0)
        self.player_pixel = [0, 0]
        self.ai_pixel = [0, 0]
        self.ai = None
        
        self.player_path = []
        self.player_total_cost = 0
        self.explored_cells = set()
        
        self.show_graph = False
        self.show_heuristic = False
        self.show_ai_annotations = False
        self.paused = False
        
        self.winner = None
        self.countdown = 0
        self.optimal_dist = 0
        self.game_results = {}
        self.huffman_codes = {}

    def init_game(self):
        grid_w, grid_h = DIFFICULTIES[self.difficulty]['grid_size']
        self.maze_gen = MazeGenerator(grid_w, grid_h)
        self.graph = self.maze_gen.generate()
        
        # Calculate Optimal Path
        from game_classes import Maze
        temp_maze = Maze(grid_w, grid_h)
        temp_maze.gen = self.maze_gen
        temp_maze.graph = self.graph
        self.optimal_dist = temp_maze.bfs_analysis()
        
        self.player_pos = self.maze_gen.start_pos
        self.player_pixel = [self.player_pos[0] * TILE_SIZE, self.player_pos[1] * TILE_SIZE]
        self.player_path = [self.player_pos]
        self.player_total_cost = 0
        self.explored_cells = set()
        self.update_visibility()
        
        # Set AI based on index
        name, h_type, backtrack = self.ui.opponents[self.opponent_idx]
        
        # Use ProjectAI for GBFS variants and Hill Climbing to satisfy "use GBFS folder files"
        from ai import ProjectAI
        self.ai = ProjectAI(temp_maze, temp_maze.graph.get_node(*self.maze_gen.start_pos), 
                           temp_maze.graph.get_node(*self.maze_gen.goal_pos), 
                           h_type, not backtrack)
        
        self.ai_pixel = [self.maze_gen.start_pos[0] * TILE_SIZE, self.maze_gen.start_pos[1] * TILE_SIZE]
        
        self.state = "COUNTDOWN"
        self.countdown = 3.0
        self.winner = None
        self.paused = False
        self.game_results = {}
        self.huffman_codes = {}

    def update_visibility(self):
        px, py = self.player_pos
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                self.explored_cells.add((px + dx, py + dy))
        gx, gy = self.maze_gen.goal_pos
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                self.explored_cells.add((gx + dx, gy + dy))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        self.difficulty = chr(event.key)
                    elif event.key == pygame.K_LEFT:
                        self.opponent_idx = (self.opponent_idx - 1) % len(self.ui.opponents)
                    elif event.key == pygame.K_RIGHT:
                        self.opponent_idx = (self.opponent_idx + 1) % len(self.ui.opponents)
                    elif event.key == pygame.K_i:
                        self.state = "INSTRUCTIONS"
                    elif event.key == CONTROLS['START']:
                        self.init_game()
                
                elif self.state == "INSTRUCTIONS":
                    if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

                elif self.state == "PLAYING":
                    if event.key == CONTROLS['TOGGLE_GRAPH']: self.show_graph = not self.show_graph
                    if event.key == CONTROLS['TOGGLE_HEURISTIC']: self.show_heuristic = not self.show_heuristic
                    if event.key == CONTROLS['TOGGLE_AI_ANNOTATION']: self.show_ai_annotations = not self.show_ai_annotations
                    if event.key == CONTROLS['TOGGLE_PAUSE']: self.paused = not self.paused
                    
                    if self.paused: return

                    dx, dy = 0, 0
                    if event.key == CONTROLS['UP'] or event.key == CONTROLS['UP_ALT']: dy = -1
                    elif event.key == CONTROLS['DOWN'] or event.key == CONTROLS['DOWN_ALT']: dy = 1
                    elif event.key == CONTROLS['LEFT'] or event.key == CONTROLS['LEFT_ALT']: dx = -1
                    elif event.key == CONTROLS['RIGHT'] or event.key == CONTROLS['RIGHT_ALT']: dx = 1
                    elif event.key == CONTROLS['UP_LEFT']: dx, dy = -1, -1
                    elif event.key == CONTROLS['UP_RIGHT']: dx, dy = 1, -1
                    elif event.key == CONTROLS['DOWN_LEFT']: dx, dy = -1, 1
                    elif event.key == CONTROLS['DOWN_RIGHT']: dx, dy = 1, 1
                    
                    if (dx, dy) != (0, 0):
                        new_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
                        if new_pos in self.graph.nodes:
                            self.player_total_cost += self.graph.get_node(*new_pos).weight
                            self.player_pos = new_pos
                            self.player_path.append(new_pos)
                            self.update_visibility()
                            if self.player_pos == self.maze_gen.goal_pos:
                                if not self.winner: self.winner = "Player"
                                self.finish_game()

                elif self.state == "GAME_OVER":
                    if event.key == CONTROLS['START']:
                        self.state = "MENU"

    def finish_game(self):
        def get_dir_string(path):
            s = ""
            for i in range(1, len(path)):
                dx, dy = path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]
                s += f"{dx}{dy}"
            return s if s else "G"

        p_str = get_dir_string(self.player_path)
        a_str = get_dir_string(self.ai.history)
        
        # Proper Huffman encoding and capture codes
        combined_text = p_str + a_str
        self.huffman.build_tree(combined_text)
        self.huffman_codes = self.huffman.codes

        p_steps = len(self.player_path) - 1
        a_steps = len(self.ai.history) - 1
        p_cost = int(self.player_total_cost)
        a_cost = int(self.ai.total_cost)
        o_steps = self.optimal_dist

        # Determine Metric Victors
        steps_winner = "PLAYER" if p_steps < a_steps else ("AI" if a_steps < p_steps else "DRAW")
        cost_winner = "PLAYER" if p_cost < a_cost else ("AI" if a_cost < p_cost else "DRAW")
        
        if p_steps == o_steps: steps_winner = "PLAYER (IDEAL)"
        elif a_steps == o_steps: steps_winner = "AI (IDEAL)"
        
        self.game_results = {
            "Winner": self.winner,
            "Player Steps": p_steps,
            "Player Cost": p_cost,
            "Player Huffman Bits": self.huffman.get_encoded_size(p_str),
            "AI Steps": a_steps,
            "AI Cost": a_cost,
            "AI Huffman Bits": self.huffman.get_encoded_size(a_str),
            "Optimal Steps": o_steps,
            "Opponent": self.ui.opponents[self.opponent_idx][0],
            "Steps Winner": steps_winner,
            "Cost Winner": cost_winner
        }
        self.state = "GAME_OVER"

    def update(self):
        dt = self.clock.get_time() / 1000.0
        self.ui.update_animations()
        if self.state == "COUNTDOWN":
            self.countdown -= dt
            if self.countdown <= 0: self.state = "PLAYING"
        elif self.state == "PLAYING" and not self.paused:
            if not self.ai.finished:
                self.ai.step()
                if self.ai.current_pos == self.maze_gen.goal_pos and not self.winner:
                    self.winner = "AI"

        # Interpolation
        tp_x, tp_y = self.player_pos[0] * TILE_SIZE, self.player_pos[1] * TILE_SIZE
        self.player_pixel[0] += (tp_x - self.player_pixel[0]) * ANIM_SPEED_MOVE
        self.player_pixel[1] += (tp_y - self.player_pixel[1]) * ANIM_SPEED_MOVE
        if self.ai:
            ta_x, ta_y = self.ai.current_pos[0] * TILE_SIZE, self.ai.current_pos[1] * TILE_SIZE
            self.ai_pixel[0] += (ta_x - self.ai_pixel[0]) * ANIM_SPEED_MOVE
            self.ai_pixel[1] += (ta_y - self.ai_pixel[1]) * ANIM_SPEED_MOVE

    def draw(self):
        if self.state == "MENU":
            self.ui.draw_menu_ext(self.difficulty, self.opponent_idx)
        elif self.state == "INSTRUCTIONS":
            self.ui.draw_instructions()
        elif self.state == "GAME_OVER":
            self.ui.draw_game_over_scene(self.game_results, self.huffman_codes)
        else:
            self.screen.fill(COLOR_BG)
            self.ui.draw_tech_bg()
            
            for (x, y), node in self.graph.nodes.items():
                if (x, y) not in self.explored_cells: continue
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = COLOR_PATH
                if (x, y) == self.maze_gen.start_pos: color = COLOR_START
                elif (x, y) == self.maze_gen.goal_pos: color = COLOR_GOAL
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

                if node.is_trap: self.ui.draw_pulse_effect(x, y, COLOR_TRAP)
                if node.is_powerup: self.ui.draw_pulse_effect(x, y, COLOR_POWERUP)
                if self.show_heuristic: self.ui.draw_node_info(node, True)

            if self.show_graph:
                for (x, y), node in self.graph.nodes.items():
                    if (x, y) not in self.explored_cells: continue
                    for n_pos in node.neighbors:
                        if n_pos in self.explored_cells:
                            s = (x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2)
                            e = (n_pos[0]*TILE_SIZE+TILE_SIZE//2, n_pos[1]*TILE_SIZE+TILE_SIZE//2)
                            pygame.draw.line(self.screen, COLOR_GRAPH_EDGE, s, e, 1)

            # Draw Trails
            for p in self.player_path:
                if p in self.explored_cells:
                    s = pygame.Surface((TILE_SIZE-20, TILE_SIZE-20), pygame.SRCALPHA)
                    s.fill(COLOR_PATH_TRAIL_PLAYER)
                    self.screen.blit(s, (p[0]*TILE_SIZE+10, p[1]*TILE_SIZE+10))
            for p in self.ai.history:
                if p in self.explored_cells:
                    s = pygame.Surface((TILE_SIZE-30, TILE_SIZE-30), pygame.SRCALPHA)
                    s.fill(COLOR_PATH_TRAIL_AI)
                    self.screen.blit(s, (p[0]*TILE_SIZE+15, p[1]*TILE_SIZE+15))

            # Characters
            pygame.draw.circle(self.screen, COLOR_PLAYER, (int(self.player_pixel[0]) + TILE_SIZE // 2, int(self.player_pixel[1]) + TILE_SIZE // 2), TILE_SIZE // 3)
            if (self.ai.current_pos[0], self.ai.current_pos[1]) in self.explored_cells:
                pygame.draw.rect(self.screen, COLOR_AI, (int(self.ai_pixel[0]) + 8, int(self.ai_pixel[1]) + 8, TILE_SIZE - 16, TILE_SIZE - 16), border_radius=3)

            if self.show_ai_annotations: self.ui.draw_ai_annotations(self.ai)
            
            stats = self.ai.get_metrics()
            stats["Human Steps"] = len(self.player_path) - 1
            stats["Ideal Dist"] = self.optimal_dist
            self.ui.draw_metrics(stats)

            if self.state == "COUNTDOWN":
                self.ui.draw_overlay("SYSTEM_READY", f"ADVERSARY TYPE: {self.ui.opponents[self.opponent_idx][0]}")
            elif self.paused:
                self.ui.draw_overlay("SYSTEM_PAUSE", "INPUT_INTERCEPTED")

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
