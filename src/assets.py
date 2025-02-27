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
            "_original": pygame.image.load(path + "sprt_player.png"),
            "position": (300, 552),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "default_index": 3,
            "max-index": 7,
            "player": True,
            "floor": 0,
            "target": None
        },
        "npc01": {
            "image": pygame.image.load(path + "neighbor1.png"),
            "_original": pygame.image.load(path + "neighbor1.png"),
            "position": (160, 461),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "default_index": 3,
            "npc": True,
            "floor": 1
        },
        "npc02": {
            "image": pygame.image.load(path + "neighbor2.png"),
            "_original": pygame.image.load(path + "neighbor2.png"),
            "position": (421, 388),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "default_index": 3,
            "npc": True,
            "floor": 2
        },
        "npc03": {
            "image": pygame.image.load(path + "neighbor3.png"),
            "_original": pygame.image.load(path + "neighbor3.png"),
            "position": (75, 314),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "default_index": 3,
            "npc": True,
            "floor": 3
        },
        "npc04": {
            "image": pygame.image.load(path + "neighbor4.png"),
            "_original": pygame.image.load(path + "neighbor4.png"),
            "position": (160, 242),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "default_index": 3,
            "npc": True,
            "floor": 4
        },
        "npc05": {
            "image": pygame.image.load(path + "neighbor5.png"),
            "_original": pygame.image.load(path + "neighbor5.png"),
            "position": (421, 168),
            "size": (175, 66),
            "sprite": (25, 66),
            "index": 3,
            "default_index": 3,
            "npc": True,
            "floor": 5
        }
    }
    resize(image)
    return image

def resize(images):
    for key in images:
        img_data = images[key]
        target_width, target_height = img_data["size"]
        images[key]["image"] = pygame.transform.scale(img_data["image"], (target_width, target_height))

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

def update_rect(images):
    """Met à jour les rect des images en fonction de l'index du sprite."""
    for key, img_data in images.items():
        if "sprite" in img_data:  # Vérifie si c'est une sprite sheet
            sprite_width, sprite_height = img_data["sprite"]
            target_width, target_height = img_data["size"]
            sprite_index = img_data["index"]
            sprite_rect = pygame.Rect(sprite_index * sprite_width, 0, sprite_width, sprite_height)
            tmp = img_data["_original"]
            tmp = pygame.transform.scale(tmp, (target_width, target_height))
            images[key]["image"] = tmp.subsurface(sprite_rect)
    return images  # Retourne le dictionnaire mis à jour

def get_player(images):
    for key, img_data in images.items():
        if img_data.get("player", False):  # Vérifie si l'entrée a la clé "player" à True
            return key  # Retourne le nom de l'objet joueur
        print(key)
    return None
