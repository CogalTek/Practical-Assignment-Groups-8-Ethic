import pygame
from src.assets import load_images, get_player, update_rect
from src.tools import click_debug
from src.movement import handle_movement

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((600, 700))
clock = pygame.time.Clock()

images = load_images()
player_key = get_player(images)

running = True
while running:
    screen.fill((30, 30, 30))

    if player_key:
        keys = pygame.key.get_pressed()
        handle_movement(images[player_key], keys)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # click_debug(event)

    for key, data in images.items():
        screen.blit(data["image"], data["position"])
        images = update_rect(images)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
