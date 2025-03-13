import pygame

def draw_text(screen, text, position, font=None, color=(255, 255, 255)):
    """Draw text on screen"""
    if not font:
        font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)