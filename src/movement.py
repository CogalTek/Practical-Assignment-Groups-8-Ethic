import pygame

def handle_movement(player, keys):
    elevator = (243, 287)
    floor = [552, 461, 387, 314, 241, 166]
    border = (50, 530)
    i = 0
    if keys:
        i += move_left(player, keys, border)
        i += move_right(player, keys, border)
        i += move_up_elevator(player, keys, elevator, floor)
        i += move_down_elevator(player, keys, elevator, floor)

    if i == 0:
        reset_rect(player)

def move_left(player, keys, border):
    if keys[pygame.K_LEFT]:
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
    if keys[pygame.K_RIGHT]:
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
    if keys[pygame.K_UP]:
        pos = list(player["position"])
        left, right = elevator
        if pos[0] > left and pos[0] < right:
            if player["floor"] < len(floor) - 1:
                player["floor"] += 1
                pos[1] = floor[player["floor"]]
                player["position"] = tuple(pos)
                return 1
    return 0

def move_down_elevator(player, keys, elevator, floor):
    if keys[pygame.K_DOWN]:
        pos = list(player["position"])
        left, right = elevator
        if pos[0] > left and pos[0] < right:
            if player["floor"] > 0:
                player["floor"] -= 1
                pos[1] = floor[player["floor"]]
                player["position"] = tuple(pos)
                return 1
    return 0

def reset_rect(player):
    player["index"] = player["default_index"]
