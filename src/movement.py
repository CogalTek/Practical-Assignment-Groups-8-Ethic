import pygame

def handle_movement(player, keys):
    # print("handle_movement")
    i = 0
    if keys:
        # print("pressed")
        i += move_left(player, keys)
        i += move_right(player, keys)

    # print("i = ", i)
    if i == 0:
        # print("reset")
        reset_rect(player)

def move_left(player, keys):
    if keys[pygame.K_LEFT]:
        pos = list(player["position"])
        pos[0] -= 10
        player["position"] = tuple(pos)

        if (player["index"] > 3 or player["index"] == 0):
            player["index"] = 2
            # print("reset")
        else:
            # print(player["index"])
            player["index"] = player["index"] - 1
            # print("left")
        # print(player["index"])
        return 1
    # print("left return 0")
    return 0

def move_right(player, keys):
    if keys[pygame.K_RIGHT]:
        pos = list(player["position"])
        pos[0] += 10
        player["position"] = tuple(pos)

        if (player["index"] < 3 or player["index"] == 6):
            player["index"] = 4
        else:
            player["index"] = player["index"] + 1
        return 1
    # print("right return 0")
    return 0

def reset_rect(player):
    player["index"] = player["default_index"]
