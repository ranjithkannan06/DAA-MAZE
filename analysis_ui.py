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