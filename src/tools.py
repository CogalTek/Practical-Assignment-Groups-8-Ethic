import pygame

def click_debug(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        print(f"Clic détecté à : ({x}, {y}, : {y - 66})")
