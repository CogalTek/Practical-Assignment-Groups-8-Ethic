import pygame

def click_debug(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        print(f"Clic détecté à : ({x}, {y}, : {y - 66})")

def draw_text(screen, text, position, font=None, color=(255, 255, 255)):
    """Affiche du texte à l'écran"""
    if not font:
        font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def text_input(screen, font=None, max_length=30):
    """Gère la saisie de texte par le joueur"""
    input_string = ""
    done = False
    color = pygame.Color('dodgerblue2')
    
    if not font:
        font = pygame.font.Font(None, 32)
    
    input_rect = pygame.Rect(50, 650, 500, 40)
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    input_string = input_string[:-1]
                else:
                    if len(input_string) < max_length:
                        input_string += event.unicode
        
        # Fond de l'input
        pygame.draw.rect(screen, (30, 30, 30), input_rect)
        txt_surface = font.render(input_string, True, color)
        screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))
        pygame.draw.rect(screen, color, input_rect, 2)
        
        pygame.display.flip()
    
    return input_string

def draw_text(screen, text, position, font=None, color=(255, 255, 255)):
    if not font:
        font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)