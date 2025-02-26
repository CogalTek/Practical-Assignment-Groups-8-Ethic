import pygame

def load_images():
    path = "./content/"
    image = {
        "background": {
            "image": pygame.image.load(path + "game-background.png"),
            "position": (0, 0),
            "size": (600, 700)
        },
        "firstPlayer": {
            "image": pygame.image.load(path + "sprt_player.png"),
            "position": (300, 552),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "max-index": 7
        },
    }
    image = resize(image)
    image = extract_sprites(image)
    return image

def resize(images):
    for key in images:
        img_data = images[key]
        target_width, target_height = img_data["size"]
        images[key]["image"] = pygame.transform.scale(img_data["image"], (target_width, target_height))
    return images

def extract_sprites(images):
    for key in images:
        img_data = images[key]
        if "sprite" in img_data:  # Vérifie si c'est une sprite sheet
            sprite_width, sprite_height = img_data["sprite"]
            sprite_index = img_data.get("index", 0)  # Par défaut, prend le sprite 0

            # Définir le rectangle du sprite à extraire
            sprite_rect = pygame.Rect(sprite_index * sprite_width, 0, sprite_width, sprite_height)

            # Extraire et remplacer l'image originale par le sprite extrait
            images[key]["image"] = images[key]["image"].subsurface(sprite_rect)

    return images
