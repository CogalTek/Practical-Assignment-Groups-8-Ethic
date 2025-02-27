# Documentation

## Structure de base

### Main

Le fichier `main.py` est divisé en deux parties :
1. **L'initialisation** des composants nécessaires au jeu.
2. **La boucle principale** qui gère l'affichage et la logique du jeu.

---

### Initialisation

```Python
import pygame
from src.assets import load_images, get_player, update_rect
from src.tools import click_debug
from src.movement import handle_movement, goto
```

Tout d'abord, nous importons `pygame`, qui est le moteur de jeu utilisé, ainsi que les différentes fonctions définies dans d'autres fichiers. Ces fonctions sont réparties dans plusieurs fichiers situés dans le dossier `src`.

```Python
# Initialisation de Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((600, 700))
clock = pygame.time.Clock()

pygame.mixer.music.load("./content/music.ogg")
pygame.mixer.music.play(-1)
images = load_images()
player_key = get_player(images)
```

- **Initialisation de Pygame** : `pygame.init()` initialise la bibliothèque Pygame.
- **Initialisation du mixeur audio** : `pygame.mixer.init()` permet de gérer le son.
- **Création de la fenêtre** : `pygame.display.set_mode((600, 700))` définit une fenêtre de 600x700 pixels.
- **Initialisation de l'horloge** : `pygame.time.Clock()` permet de contrôler la fréquence d'affichage (ici, 10 FPS).
- **Chargement et lecture de la musique** :

  ```Python
  pygame.mixer.music.load("./content/music.ogg")
  pygame.mixer.music.play(-1)
  ```
  > L'argument `-1` indique que la musique doit être lue en boucle.

Ensuite, nous chargeons toutes les images du jeu et récupérons la clé correspondant au joueur :

```Python
images = load_images()
player_key = get_player(images)
```

---

### Boucle principale

```Python
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
```

La boucle principale s'exécute en continu tant que `running` est `True`.

- **Définition de la couleur du fond** :
  ```Python
  screen.fill((30, 30, 30))
  ```
  Le fond est rempli avec une couleur gris foncé (RGB : 30, 30, 30).

- **Gestion du mouvement du joueur** :
  ```Python
  if player_key:
      keys = pygame.key.get_pressed()
      handle_movement(images[player_key], keys)
  ```
  Cette partie du code permet de récupérer les touches pressées et d'appliquer les déplacements du joueur à l'aide des fonctions du fichier `movement.py`.

- **Gestion des événements** :
  ```Python
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          running = False
      # click_debug(event)
  ```
  Ici, nous traitons les événements tels que les clics et les touches du clavier. Si l'utilisateur ferme la fenêtre (`pygame.QUIT`), la variable `running` passe à `False`, ce qui met fin à la boucle.
  > La fonction `click_debug(event)` est utilisée pour afficher dans le terminal les coordonnées du clic de la souris (utile pour le débogage).

- **Mise à jour et affichage des images** :
  ```Python
  for key, data in images.items():
      screen.blit(data["image"], data["position"])
      images = update_rect(images)
  ```
  Chaque image est redessinée à sa nouvelle position pour animer les déplacements.

- **Rafraîchissement de l'affichage** :
  ```Python
  pygame.display.flip()
  clock.tick(10)
  ```
  `pygame.display.flip()` met à jour l'affichage, et `clock.tick(10)` limite la fréquence d'images à 10 FPS.

Enfin, lorsque la boucle est terminée, le programme quitte proprement :
```Python
pygame.quit()
```


### Tools

```Python
import pygame

def click_debug(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        print(f"Clic détecté à : ({x}, {y}, : {y - 66})")
```

### Assets

```Python
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
```

### Movement

```Python
import pygame

elevator = (243, 287)
floor = [552, 461, 387, 314, 241, 166]
border = (50, 530)
couldown = 0

pygame.mixer.init()
sound = pygame.mixer.Sound("./content/ascenseur.wav")

def handle_movement(player, keys):
    i = 0
    if keys:
        i += move_left(player, keys, border)
        i += move_right(player, keys, border)
        i += move_up_elevator(player, keys, elevator, floor)
        i += move_down_elevator(player, keys, elevator, floor)

    if i == 0:
        reset_rect(player)

def move_left(player, keys, border):
    if keys == "left" or keys[pygame.K_LEFT]:
        pos = list(player["position"])
        left, _ = border
        if pos[0] > left:
            pos[0] -= 10
        player["position"] = tuple(pos)

        if (player["index"] > 3 or player["index"] == 0):
            player["index"] = 2
        else:
            player["index"] = player["index"] - 1
        return 1
    return 0

def move_right(player, keys, border):
    if keys == "right" or keys[pygame.K_RIGHT]:
        pos = list(player["position"])
        _, right = border
        if pos[0] < right:
            pos[0] += 10
        player["position"] = tuple(pos)

        if (player["index"] < 3 or player["index"] == 6):
            player["index"] = 4
        else:
            player["index"] = player["index"] + 1
        return 1
    return 0

def move_up_elevator(player, keys, elevator, floor):
    if keys == "up" or keys[pygame.K_UP]:
        pos = list(player["position"])
        left, right = elevator
        if pos[0] > left and pos[0] < right:
            if player["floor"] < len(floor) - 1:
                player["floor"] += 1
                pos[1] = floor[player["floor"]]
                player["position"] = tuple(pos)
                sound.play()
                return 1
    return 0

def move_down_elevator(player, keys, elevator, floor):
    if keys == "down" or keys[pygame.K_DOWN]:
        pos = list(player["position"])
        left, right = elevator
        if pos[0] > left and pos[0] < right:
            if player["floor"] > 0:
                player["floor"] -= 1
                pos[1] = floor[player["floor"]]
                player["position"] = tuple(pos)
                sound.play()
                return 1
    return 0

def reset_rect(player):
    player["index"] = player["default_index"]

def goto(player, target):
    ecart = 35
    elevator_left = 243
    elevator_right = 287
    x, _ = player["position"]
    x_npc, _ = target["position"]

    if target == None:
        return 0

    # si la target est à un autre etage
    if player["floor"] != target["floor"]:
        # ce rendre à l'ascenceur
            if x < elevator_left:
                # print("mov to right")
                move_right(player, "right", border)
                return 0
            if x > elevator_right:
                # print("mov to left")
                move_left(player, "left", border)
                return 0
        # monter à l'étage
            if player["floor"] < target["floor"]:
                # print("mov to up")
                move_up_elevator(player, "up", elevator, floor)
                return 0
            if player["floor"] > target["floor"]:
                # print("mov to down")
                move_down_elevator(player, "down", elevator, floor)
                return 0
    # avancer vers la target
    if x < (x_npc - ecart):
        move_right(player, "right", border)
        return 0
    if x > (x_npc + ecart):
        move_left(player, "left", border)
        return 0
    return 1
```