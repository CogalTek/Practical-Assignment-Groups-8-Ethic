import pygame

def load_images():
    path = "./content/"
    image = {
        "background": {"image": pygame.image.load(path + "game-background.png"), "position": (0, 0), "size": (600, 700)},
        # "image2": {"image": pygame.image.load(path + "image2.png"), "position": (200, 200)},
        # "image3": {"image": pygame.image.load(path + "image3.png"), "position": (300, 300)},
    }
    image = resize(image)
    return image

def resize(images):
    for key in images:
        img_data = images[key]
        target_width, target_height = img_data["size"]
        images[key]["image"] = pygame.transform.scale(img_data["image"], (target_width, target_height))
    return images
