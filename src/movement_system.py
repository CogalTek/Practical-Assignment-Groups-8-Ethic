import pygame
import random
import math
import time

class MovementSystem:
    def __init__(self):
        self.floor_positions = [552, 461, 387, 314, 241, 168]
        self.last_update = time.time()
        self.last_floor_change = 0
        self.elevator_sound = None

    def set_elevator_sound(self, sound):
        self.elevator_sound = sound

    def change_floor(self, entity, direction):
        new_floor = entity["floor"] + direction
        if 0 <= new_floor < len(self.floor_positions):
            entity["floor"] = new_floor
            entity["position"] = (entity["position"][0], self.floor_positions[entity["floor"]])
            if self.elevator_sound:
                self.elevator_sound.play()

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