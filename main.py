import pygame
from src.assets import load_images, get_player, update_rect
from src.tools import click_debug
from src.movement import handle_movement, goto

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((600, 700))
clock = pygame.time.Clock()

pygame.mixer.music.load("./content/music.ogg")
pygame.mixer.music.play(-1)
images = load_images()
player_key = get_player(images)

# test
i = 0
tg = ["npc01", "npc02", "npc03", "npc04", "npc05"]

running = True
while running:
    if i == 5:
        i = 0
    screen.fill((30, 30, 30))

    images[player_key]["target"] = tg[i]
    i += goto(images[player_key], images[images[player_key]["target"]])

    if player_key:
        keys = pygame.key.get_pressed()
        handle_movement(images[player_key], keys)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        click_debug(event)

    for key, data in images.items():
        screen.blit(data["image"], data["position"])
        images = update_rect(images)

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
