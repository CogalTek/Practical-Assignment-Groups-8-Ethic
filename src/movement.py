import pygame
import random
import math
import time

class MovementSystem:
    def __init__(self):
        self.npc_routines = {
            'npc01': {'path': [(160, 461), (300, 461), (421, 461)], 'speed': 0.8, 'pause_chance': 0.003},
            'npc02': {'path': [(100, 388), (400, 388)], 'speed': 1.0, 'pause_chance': 0.005},
            'npc03': {'path': [(75, 314), (243, 314), (421, 314)], 'speed': 1.2, 'pause_chance': 0.001},
            'npc04': {'path': [(160, 242), (300, 242)], 'speed': 0.7, 'pause_chance': 0.002},
            'npc05': {'path': [(243, 168), (421, 168)], 'speed': 0.9, 'pause_chance': 0.004}
        }
        self.elevator_sound = None
        self.floor_positions = [552, 461, 387, 314, 241, 168]
        self.last_update = time.time()
        self.last_floor_change = 0

    def set_elevator_sound(self, sound):
        self.elevator_sound = sound

    def handle_player_movement(self, player, keys):
        speed = 3  # Réduction de la vitesse du joueur
        x, y = player["position"]
        current_floor = player["floor"]
        current_time = time.time()

        # Déplacement horizontal avec inertie
        if keys[pygame.K_LEFT]:
            x = max(50, x - speed)
        
        if keys[pygame.K_RIGHT]:
            x = min(530, x + speed)

        # Déplacement vertical via ascenseur avec délai
        if current_time - self.last_floor_change > 0.15:  # Ajout d'un délai
            if keys[pygame.K_UP] and 243 <= x <= 287:
                self.change_floor(player, 1)
                self.last_floor_change = current_time
            if keys[pygame.K_DOWN] and 243 <= x <= 287:
                self.change_floor(player, -1)
                self.last_floor_change = current_time

        player["position"] = (x, self.floor_positions[player["floor"]])
        self.update_animation(player, 'left' if keys[pygame.K_LEFT] else 'right' if keys[pygame.K_RIGHT] else 'idle')

    def change_floor(self, entity, direction):
        new_floor = entity["floor"] + direction
        if 0 <= new_floor < len(self.floor_positions):
            entity["floor"] = new_floor
            if self.elevator_sound:
                self.elevator_sound.play()

    def update_npc(self, npc, player_pos, game_phase):
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # Comportement basé sur l'état
        if npc['behavior_state'] == 'fleeing':
            self.flee_behavior(npc, player_pos, delta_time)
        elif npc['behavior_state'] == 'idle':
            if current_time > npc['idle_end']:
                npc['behavior_state'] = 'walking'
        else:
            self.natural_walking(npc, delta_time)

        self.update_animation(npc, npc['behavior_state'])

    def natural_walking(self, npc, delta_time):
        routine = self.npc_routines.get(npc['id'], {})
        path = routine.get('path', [])
        if not path:
            return

        target_index = npc['current_goal']
        target = path[target_index]
        
        # Calcul de trajectoire avec courbe de Bézier
        dx = target[0] - npc['position'][0]
        dy = target[1] - npc['position'][1]
        distance = math.hypot(dx, dy)
        
        if distance < 5:  # Seuil d'arrivée
            if random.random() < routine['pause_chance']:
                npc['behavior_state'] = 'idle'
                npc['idle_end'] = time.time() + random.uniform(2, 5)
            npc['current_goal'] = (target_index + 1) % len(path)
            return

        # Déplacement avec accélération/décélération
        speed = routine['speed'] * (1 + random.uniform(-0.2, 0.2))  # Variation de vitesse
        npc['velocity'][0] += (dx/distance) * speed * delta_time * 60
        npc['velocity'][1] += (dy/distance) * speed * delta_time * 60
        
        # Application du mouvement avec inertie
        new_x = npc['position'][0] + npc['velocity'][0]
        new_y = npc['position'][1] + npc['velocity'][1]
        
        # Limiter les déplacements à l'intérieur de la fenêtre
        new_x = max(50, min(530, new_x))  # Limites horizontales
        new_y = max(168, min(552, new_y))  # Limites verticales (basées sur les étages)
        
        npc['position'] = (new_x, new_y)

    def flee_behavior(self, npc, player_pos, delta_time):
        dx = npc['position'][0] - player_pos[0]
        dy = npc['position'][1] - player_pos[1]
        distance = math.hypot(dx, dy)
        
        if distance > 300:  # Distance de sécurité
            npc['behavior_state'] = 'walking'
            return

        # Fuite en courbe avec variation
        angle = math.atan2(dy, dx) + random.uniform(-0.3, 0.3)
        speed = 3.0 * delta_time * 60
        
        npc['position'] = (
            npc['position'][0] + math.cos(angle) * speed,
            npc['position'][1] + math.sin(angle) * speed
        )

    def update_animation(self, entity, action):
        frames = {
            'left': {'frames': [2, 1, 0], 'speed': 0.2},
            'right': {'frames': [4, 5, 6], 'speed': 0.2},
            'idle': {'frames': [3], 'speed': 0},
            'walking': {'frames': [3, 4, 5, 4], 'speed': 0.15},
            'fleeing': {'frames': [2, 1, 0, 1], 'speed': 0.1}
        }
        
        anim = frames.get(action, frames['idle'])
        entity['anim_timer'] = entity.get('anim_timer', 0) + anim['speed']
        
        if entity['anim_timer'] >= 1:
            entity['anim_timer'] = 0
            entity['frame_index'] = (entity.get('frame_index', 0) + 1) % len(anim['frames'])
            entity['index'] = anim['frames'][entity['frame_index']]

    def check_collision(self, entity1, entity2):
        rect1 = pygame.Rect(entity1['position'], (50, 66))
        rect2 = pygame.Rect(entity2['position'], (50, 66))
        return rect1.colliderect(rect2)