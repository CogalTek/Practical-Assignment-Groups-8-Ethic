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