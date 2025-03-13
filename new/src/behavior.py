import random
import math
from collections import deque

class NPCAI:
    def __init__(self):
        self.personalities = {
            'npc01': {'speed': 1.2, 'curiosity': 0.8, 'routes': []},
            'npc03': {'speed': 2.0, 'curiosity': 0.3, 'routes': []}
        }
        
        self.memory = {
            'player_positions': deque(maxlen=10),
            'points_of_interest': {}
        }
        
        self.STATES = {
            'IDLE': self.handle_idle,
            'WALKING': self.handle_walking,
            'TALKING': self.handle_talking,
            'FLEEING': self.handle_fleeing
        }

    def generate_path(self, start, end):
        """Génère un chemin avec des courbes bézier pour un mouvement naturel"""
        control_point = (
            (start[0] + end[0]) // 2 + random.randint(-50, 50),
            (start[1] + end[1]) // 2 + random.randint(-30, 30)
        )
        return [start, control_point, end]

    def get_next_action(self, npc_id, player_pos):
        personality = self.personalities[npc_id]
        current_pos = (npc['position'][0], npc['position'][1])
        
        # Modèle de décision markovien
        if random.random() < 0.02:
            return 'PAUSE'
        if self.detect_player_proximity(current_pos, player_pos):
            return 'FLEE' if personality['curiosity'] < 0.5 else 'OBSERVE'
        
        return 'WALK'

    def apply_human_locomotion(self, npc, target_pos):
        """Simule la biomécanique humaine avec acceleration/décélération"""
        dx = target_pos[0] - npc['position'][0]
        dy = target_pos[1] - npc['position'][1]
        distance = math.sqrt(dx**2 + dy**2)
        
        speed = self.personalities[npc['id']]['speed']
        acceleration = 0.1 if distance > 50 else 0.05
        deceleration = 0.2 if distance < 20 else 0.1
        
        npc['velocity'][0] += dx/distance * acceleration
        npc['velocity'][1] += dy/distance * acceleration
        
        # Limite de vitesse
        npc['velocity'][0] = max(-speed, min(speed, npc['velocity'][0]))
        npc['velocity'][1] = max(-speed, min(speed, npc['velocity'][1]))
        
        # Application du mouvement
        npc['position'][0] += npc['velocity'][0]
        npc['position'][1] += npc['velocity'][1]