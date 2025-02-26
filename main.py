import pygame
from src.assets import load_images
from src.tools import click_debug

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((600, 700))
clock = pygame.time.Clock()

images = load_images()

running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        click_debug(event)

    for key, data in images.items():
        screen.blit(data["image"], data["position"])

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
