import pygame

def load_images():
    path = "./content/"
    images = {
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
            "target": None,
            "id": "player",
            "velocity": [0, 0],
            "accelerating": False
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
            "floor": 1,
            "id": "npc01",
            "velocity": [0, 0],
            "behavior_state": "walking",
            "current_goal": 0,
            "idle_end": 0,
            "anim_timer": 0,
            "frame_index": 0,
            "guilt": 0.1
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
            "floor": 2,
            "id": "npc02",
            "velocity": [0, 0],
            "behavior_state": "walking",
            "current_goal": 0,
            "idle_end": 0,
            "anim_timer": 0,
            "frame_index": 0,
            "guilt": 0.2
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
            "floor": 3,
            "id": "npc03",
            "velocity": [0, 0],
            "behavior_state": "walking",
            "current_goal": 0,
            "idle_end": 0,
            "anim_timer": 0,
            "frame_index": 0,
            "guilt": 0.8
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
            "floor": 4,
            "id": "npc04",
            "velocity": [0, 0],
            "behavior_state": "walking",
            "current_goal": 0,
            "idle_end": 0,
            "anim_timer": 0,
            "frame_index": 0,
            "guilt": 0.4
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
            "floor": 5,
            "id": "npc05",
            "velocity": [0, 0],
            "behavior_state": "walking",
            "current_goal": 0,
            "idle_end": 0,
            "anim_timer": 0,
            "frame_index": 0,
            "guilt": 0.6
        }
    }

    # Post-process images
    resize(images)
    update_rect(images)
    return images

def resize(images):
    for key in images:
        img_data = images[key]
        if "size" in img_data:
            target_size = img_data["size"]
            img_data["image"] = pygame.transform.scale(img_data["image"], target_size)
            if "_original" in img_data:
                img_data["_original"] = pygame.transform.scale(img_data["_original"], target_size)

def update_rect(images):
    for key in images:
        img_data = images[key]
        if "sprite" in img_data:
            sprite_w, sprite_h = img_data["sprite"]
            index = img_data["index"]
            
            original = img_data["_original"]
            sprite_rect = pygame.Rect(
                index * sprite_w,
                0,
                sprite_w,
                sprite_h
            )
            img_data["image"] = original.subsurface(sprite_rect)
            # Update collision rect
            img_data["rect"] = pygame.Rect(
                img_data["position"][0], 
                img_data["position"][1],
                50,  # Collision width
                66   # Collision height
            )
    return images

def get_player(images):
    for key, data in images.items():
        if data.get("player", False):
            return key
    return None