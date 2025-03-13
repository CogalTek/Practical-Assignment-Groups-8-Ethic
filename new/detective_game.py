import pygame
import sys
import time
import random
import json
import math
from src.assets import load_images, get_player, update_rect
from src.movement import MovementSystem
from src.tools import draw_text
from case_processor import CaseProcessor

class DetectiveGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Enquête - Détective IA")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        # Systèmes principaux
        self.movement = MovementSystem()
        self.case_processor = CaseProcessor()
        
        # Chargement des ressources
        self.images = load_images()
        self.player_id = get_player(self.images)
        self.init_elevator_sound()
        
        # États du jeu
        self.running = True
        self.active_npc = None
        self.dialogue_active = False
        self.game_phase = "exploration"  # exploration, interrogation, deduction, conclusion
        self.target_npc = None
        self.current_dialogue = []
        self.dialogue_progress = 0
        self.last_dialogue_time = 0
        self.dialogue_speed = 1000  # Millisecondes entre chaque dialogue
        self.current_deduction = None
        self.deductions = []
        self.conclusion = None
        self.show_controls = False
        self.fast_mode = False  # Mode accéléré pour la simulation
        self.last_floor_change = 0  # Dernière fois qu'on a changé d'étage
        self.debug_movement = True  # Affiche les infos de déplacement en console
        self.interrogated_npcs = []  # Liste des PNJ interrogés
        
        # Initialiser les NPC actifs et inactive les autres
        self.active_npcs = []
        
        # Vérification et debug des étages
        print("Vérification des étages initiaux:")
        print(f"Positions des étages: {self.movement.floor_positions}")
        for entity_id, entity in self.images.items():
            if entity_id.startswith("npc") or entity_id == self.player_id:
                floor = entity.get("floor", -1)
                position_y = entity.get("position", (0, 0))[1]
                expected_y = self.movement.floor_positions[floor] if 0 <= floor < len(self.movement.floor_positions) else "?"
                print(f"{entity_id}: Étage {floor}, Position Y = {position_y}, Y attendu = {expected_y}")
        
    def toggle_fast_mode(self):
        """Active/désactive le mode accéléré"""
        self.fast_mode = not self.fast_mode
        if self.fast_mode:
            self.dialogue_speed = 200  # Plus rapide en mode accéléré
        else:
            self.dialogue_speed = 1000  # Normal

    def init_elevator_sound(self):
        pygame.mixer.init()
        try:
            self.elevator_sound = pygame.mixer.Sound("./content/ascenseur.wav")
            self.movement.set_elevator_sound(self.elevator_sound)
        except pygame.error:
            print("⚠️ Fichier audio d'ascenseur non trouvé.")
            self.elevator_sound = None

    def load_case(self, json_data):
        """Charge un cas d'enquête et initialise le jeu"""
        num_suspects = self.case_processor.load_case(json_data)
        
        # Activez les NPC correspondants aux suspects
        self.active_npcs = self.case_processor.get_active_npcs()
        
        print("\n=== INITIALISATION DES PERSONNAGES ===")
        
        # IMPORTANT: S'assurer que le détective commence au rez-de-chaussée (étage 0)
        # et que sa position Y correspond bien à l'étage 0 (552)
        self.images[self.player_id]["floor"] = 0
        self.images[self.player_id]["position"] = (300, self.movement.floor_positions[0])
        print(f"Détective: étage {0}, position Y = {self.movement.floor_positions[0]}")
        
        # Mettre à jour les PNJs
        for npc_id in ["npc01", "npc02", "npc03", "npc04", "npc05"]:
            # Désactiver tous les PNJs par défaut
            if npc_id in self.images:
                self.images[npc_id]["active"] = False
        
        # Réactiver et mettre à jour uniquement les PNJs qui correspondent aux suspects
        for npc_id in self.active_npcs:
            if npc_id in self.images:
                # Marquer le PNJ comme actif
                self.images[npc_id]["active"] = True
                
                # Déterminer l'étage du PNJ basé sur son ID
                npc_number = int(npc_id[3:])
                
                # Étage = numéro du PNJ (npc01 -> étage 1, npc02 -> étage 2, etc.)
                correct_floor = npc_number
                
                # Définir l'étage et la position Y correspondante
                self.images[npc_id]["floor"] = correct_floor
                self.images[npc_id]["position"] = (
                    self.images[npc_id]["position"][0],
                    self.movement.floor_positions[correct_floor]
                )
                
                # Mise à jour de la culpabilité
                self.images[npc_id]["guilt"] = self.case_processor.get_suspect_guilt(npc_id)
                
                print(f"{npc_id}: étage {correct_floor}, position Y = {self.movement.floor_positions[correct_floor]}")
        
        print("========================================\n")
        
        # Initialiser le jeu en mode exploration
        self.game_phase = "exploration"
        self.set_next_target()
        for npc_id in self.active_npcs:
            if npc_id in self.images:
                # Déterminer l'étage du PNJ basé sur son ID
                npc_number = int(npc_id[3:])
                
                # Étage = numéro du PNJ (npc01 -> étage 1, npc02 -> étage 2, etc.)
                correct_floor = npc_number
                
                # Définir l'étage et la position Y correspondante
                self.images[npc_id]["floor"] = correct_floor
                self.images[npc_id]["position"] = (
                    self.images[npc_id]["position"][0],
                    self.movement.floor_positions[correct_floor]
                )
                
                # Mise à jour de la culpabilité
                self.images[npc_id]["guilt"] = self.case_processor.get_suspect_guilt(npc_id)
                
                print(f"{npc_id}: étage {correct_floor}, position Y = {self.movement.floor_positions[correct_floor]}")
        
        print("========================================\n")
        
        # Initialiser le jeu en mode exploration
        self.game_phase = "exploration"
        self.set_next_target()

    def set_next_target(self):
        """Définit le prochain NPC à interroger"""
        npc_id, question, answer = self.case_processor.get_next_dialogue()
        
        if npc_id:
            self.target_npc = npc_id
            
            # Obtenir le nom du suspect correspondant au NPC
            suspect_name = None
            if npc_id in self.case_processor.npc_to_suspect:
                suspect_name = self.case_processor.npc_to_suspect[npc_id]
                
            self.current_dialogue = [
                f"Détective: {question}",
                f"{suspect_name if suspect_name else npc_id}: {answer}"
            ]
            
            # Ajouter à la liste des PNJ interrogés s'il n'y est pas déjà
            if npc_id not in self.interrogated_npcs:
                self.interrogated_npcs.append(npc_id)
                
        elif self.game_phase == "exploration":
            # Passage à la phase de déduction
            self.game_phase = "deduction"
            # Déplacer le joueur vers le rez-de-chaussée
            self.images[self.player_id]["floor"] = 0
            
            # Récupérer toutes les déductions
            deduction = self.case_processor.get_next_deduction()
            while deduction:
                self.deductions.append(deduction)
                deduction = self.case_processor.get_next_deduction()
                
            self.current_deduction = 0
        elif self.game_phase == "deduction" and self.current_deduction >= len(self.deductions):
            # Passage à la conclusion
            self.game_phase = "conclusion"
            self.conclusion = self.case_processor.get_conclusion()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.show_controls = not self.show_controls
                # L'appui sur ESPACE est toujours disponible pour une intervention manuelle
                elif event.key == pygame.K_SPACE:
                    self.handle_space_press()
                # Ajout d'une touche pour accélérer la simulation
                elif event.key == pygame.K_f:
                    self.toggle_fast_mode()
                # Touche pour activer/désactiver le debug des déplacements
                elif event.key == pygame.K_m:
                    self.debug_movement = not self.debug_movement
                    print(f"Debug mouvement: {'activé' if self.debug_movement else 'désactivé'}")
                # Touches pour forcer un changement d'étage (pour débugger)
                elif event.key == pygame.K_0:
                    print(f"Force étage 0 (Rez-de-chaussée)")
                    self.force_floor(0)
                elif event.key == pygame.K_1:
                    print(f"Force étage 1")
                    self.force_floor(1)
                elif event.key == pygame.K_2:
                    print(f"Force étage 2")
                    self.force_floor(2)
                elif event.key == pygame.K_3:
                    print(f"Force étage 3")
                    self.force_floor(3)
                # Touche pour afficher les positions de tous les personnages
                elif event.key == pygame.K_p:
                    self.print_all_positions()
    
    def force_floor(self, floor_number):
        """Force le détective à aller à un étage spécifique (pour déboguer)"""
        if 0 <= floor_number < len(self.movement.floor_positions):
            player = self.images[self.player_id]
            
            # Forcer l'étage et la position Y correspondante
            old_floor = player["floor"]
            player["floor"] = floor_number
            player["position"] = (player["position"][0], self.movement.floor_positions[floor_number])
            
            print(f"Déplacement forcé de l'étage {old_floor} à {floor_number}")
            print(f"Nouvelle position: {player['position']}")
    
    def print_all_positions(self):
        """Affiche les positions et étages de tous les personnages"""
        print("\n=== POSITIONS ET ÉTAGES ===")
        print(f"Étages disponibles: {self.movement.floor_positions}")
        
        # Détective
        player = self.images[self.player_id]
        print(f"Détective: Étage {player['floor']}, Position {player['position']}")
        print(f"Position Y attendue: {self.movement.floor_positions[player['floor']]}")
        
        # PNJs
        for npc_id in self.active_npcs:
            npc = self.images.get(npc_id)
            if npc:
                print(f"{npc_id}: Étage {npc['floor']}, Position {npc['position']}")
                print(f"Position Y attendue: {self.movement.floor_positions[npc['floor']]}")
        print("===========================\n")

    def handle_space_press(self):
        # Cette fonction n'est plus nécessaire pour l'autonomie, mais nous la gardons pour 
        # permettre à l'utilisateur d'intervenir manuellement s'il le souhaite
        if self.dialogue_active:
            self.dialogue_progress += 1
            if self.dialogue_progress >= len(self.current_dialogue):
                self.dialogue_active = False
                self.dialogue_progress = 0
                
                # Si on était en conversation avec le target_npc, passer au suivant
                if self.active_npc == self.target_npc:
                    self.set_next_target()
        
        # Si en déduction, avancer
        elif self.game_phase == "deduction":
            self.current_deduction += 1
            if self.current_deduction >= len(self.deductions):
                self.game_phase = "conclusion"
                self.conclusion = self.case_processor.get_conclusion()
        
        # Si près d'un NPC, commencer le dialogue
        elif self.active_npc and self.active_npc == self.target_npc:
            self.dialogue_active = True
            self.dialogue_progress = 0
            self.last_dialogue_time = pygame.time.get_ticks()
            
    def move_detective_autonomously(self):
        """Déplace le détective de manière autonome vers sa cible"""
        player = self.images[self.player_id]
        
        # Vérifier que la position Y correspond bien à l'étage
        expected_y = self.movement.floor_positions[player["floor"]]
        if abs(player["position"][1] - expected_y) > 2:  # Petite tolérance
            if self.debug_movement:
                print(f"CORRECTION: Détective à l'étage {player['floor']} mais position Y = {player['position'][1]}, devrait être {expected_y}")
            player["position"] = (player["position"][0], expected_y)
        
        # Si on n'a pas de cible, ou si on est en phase de déduction, revenir au rez-de-chaussée
        if not self.target_npc or self.game_phase == "deduction":
            # Si on n'est pas déjà au rez-de-chaussée, y aller
            if player["floor"] != 0:
                # Se diriger vers l'ascenseur (x entre 243 et 287)
                elevator_x = 265
                if abs(player["position"][0] - elevator_x) > 5:
                    # Déplacer vers l'ascenseur
                    if player["position"][0] < elevator_x:
                        player["position"] = (player["position"][0] + 3, player["position"][1])
                        player["index"] = 5  # Sprite face droite
                    else:
                        player["position"] = (player["position"][0] - 3, player["position"][1])
                        player["index"] = 1  # Sprite face gauche
                else:
                    # Descendre d'un étage en utilisant l'ascenseur
                    if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                        # Utiliser le système d'ascenseur du jeu
                        old_floor = player["floor"]
                        old_position = player["position"]
                        self.movement.change_floor(player, -1)
                        self.last_floor_change = pygame.time.get_ticks()
                        
                        # Vérifier que le changement d'étage a bien été effectué
                        if self.debug_movement:
                            print(f"Changement d'étage: {old_floor} -> {player['floor']}")
                            print(f"Changement de position: {old_position} -> {player['position']}")
                            
                            expected_new_y = self.movement.floor_positions[player["floor"]]
                            if abs(player["position"][1] - expected_new_y) > 2:
                                print(f"ALERTE: Position Y incorrecte après changement d'étage!")
                                print(f"  Devrait être: {expected_new_y}, est: {player['position'][1]}")
                                # Forcer la correction
                                player["position"] = (player["position"][0], expected_new_y)
            return
        
        # Trouver l'étage de la cible
        target_npc = self.images.get(self.target_npc)
        if not target_npc:
            print(f"PNJ cible introuvable: {self.target_npc}")
            return
            
        target_floor = target_npc["floor"]
        
        # Debug - afficher les positions et étages
        if self.debug_movement and hasattr(self, 'debug_counter'):
            self.debug_counter += 1
            if self.debug_counter >= 60:  # Afficher toutes les secondes environ
                print(f"Détective: étage {player['floor']}, position Y = {player['position'][1]}")
                print(f"Cible {self.target_npc}: étage {target_floor}, position Y = {target_npc['position'][1]}")
                
                # Vérification des positions Y attendues
                detective_expected_y = self.movement.floor_positions[player['floor']]
                target_expected_y = self.movement.floor_positions[target_floor]
                print(f"Position Y attendue pour détective: {detective_expected_y}")
                print(f"Position Y attendue pour cible: {target_expected_y}")
                self.debug_counter = 0
        else:
            self.debug_counter = 0
        
        # Si on n'est pas sur le bon étage, utiliser l'ascenseur
        if player["floor"] != target_floor:
            # Se diriger vers l'ascenseur (x entre 243 et 287)
            elevator_x = 265
            if abs(player["position"][0] - elevator_x) > 5:
                # Déplacer vers l'ascenseur
                if player["position"][0] < elevator_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Sprite face droite
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Sprite face gauche
            else:
                # On est à l'ascenseur, prêt à changer d'étage
                # Forcer la position x à être dans l'ascenseur
                player["position"] = (elevator_x, player["position"][1])
                
                # Déterminer si on monte ou descend
                direction = 1 if target_floor > player["floor"] else -1
                
                # Changement d'étage
                if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                    old_floor = player["floor"]
                    old_position = player["position"]
                    
                    # Utiliser le système d'ascenseur du jeu
                    self.movement.change_floor(player, direction)
                    self.last_floor_change = pygame.time.get_ticks()
                    
                    # Vérifier que le changement d'étage a bien été effectué
                    if self.debug_movement:
                        print(f"Changement d'étage: {old_floor} -> {player['floor']}")
                        print(f"Changement de position: {old_position} -> {player['position']}")
                        
                        expected_new_y = self.movement.floor_positions[player["floor"]]
                        if abs(player["position"][1] - expected_new_y) > 2:
                            print(f"ALERTE: Position Y incorrecte après changement d'étage!")
                            print(f"  Devrait être: {expected_new_y}, est: {player['position'][1]}")
                            # Forcer la correction
                            player["position"] = (player["position"][0], expected_new_y)
        else:
            # Sur le bon étage, se diriger vers la cible
            target_x = target_npc["position"][0]
            if abs(player["position"][0] - target_x) > 30:  # Distance plus grande pour éviter les oscillations
                # Déplacer vers la cible
                if player["position"][0] < target_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Sprite face droite
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Sprite face gauche
            else:
                # On est assez proche, rester immobile
                player["index"] = 3  # Sprite face avant-chaussée
        if not self.target_npc or self.game_phase == "deduction":
            # Si on n'est pas déjà au rez-de-chaussée, y aller
            if player["floor"] != 0:
                # Se diriger vers l'ascenseur (x entre 243 et 287)
                elevator_x = 265
                if abs(player["position"][0] - elevator_x) > 5:
                    # Déplacer vers l'ascenseur
                    if player["position"][0] < elevator_x:
                        player["position"] = (player["position"][0] + 3, player["position"][1])
                        player["index"] = 5  # Sprite face droite
                    else:
                        player["position"] = (player["position"][0] - 3, player["position"][1])
                        player["index"] = 1  # Sprite face gauche
                else:
                    # Descendre d'un étage en utilisant l'ascenseur
                    if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                        # Utiliser le système d'ascenseur du jeu
                        old_floor = player["floor"]
                        old_position = player["position"]
                        self.movement.change_floor(player, -1)
                        self.last_floor_change = pygame.time.get_ticks()
                        
                        # Vérifier que le changement d'étage a bien été effectué
                        if self.debug_movement:
                            print(f"Changement d'étage: {old_floor} -> {player['floor']}")
                            print(f"Changement de position: {old_position} -> {player['position']}")
                            
                            expected_new_y = self.movement.floor_positions[player["floor"]]
                            if abs(player["position"][1] - expected_new_y) > 2:
                                print(f"ALERTE: Position Y incorrecte après changement d'étage!")
                                print(f"  Devrait être: {expected_new_y}, est: {player['position'][1]}")
                                # Forcer la correction
                                player["position"] = (player["position"][0], expected_new_y)
            return
        
        # Trouver l'étage de la cible
        target_npc = self.images.get(self.target_npc)
        if not target_npc:
            print(f"PNJ cible introuvable: {self.target_npc}")
            return
            
        target_floor = target_npc["floor"]
        
        # Debug - afficher les positions et étages
        if self.debug_movement and hasattr(self, 'debug_counter'):
            self.debug_counter += 1
            if self.debug_counter >= 60:  # Afficher toutes les secondes environ
                print(f"Détective: étage {player['floor']}, position Y = {player['position'][1]}")
                print(f"Cible {self.target_npc}: étage {target_floor}, position Y = {target_npc['position'][1]}")
                
                # Vérification des positions Y attendues
                detective_expected_y = self.movement.floor_positions[player['floor']]
                target_expected_y = self.movement.floor_positions[target_floor]
                print(f"Position Y attendue pour détective: {detective_expected_y}")
                print(f"Position Y attendue pour cible: {target_expected_y}")
                self.debug_counter = 0
        else:
            self.debug_counter = 0
        
        # Si on n'est pas sur le bon étage, utiliser l'ascenseur
        if player["floor"] != target_floor:
            # Se diriger vers l'ascenseur (x entre 243 et 287)
            elevator_x = 265
            if abs(player["position"][0] - elevator_x) > 5:
                # Déplacer vers l'ascenseur
                if player["position"][0] < elevator_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Sprite face droite
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Sprite face gauche
            else:
                # On est à l'ascenseur, prêt à changer d'étage
                # Forcer la position x à être dans l'ascenseur
                player["position"] = (elevator_x, player["position"][1])
                
                # Déterminer si on monte ou descend
                direction = 1 if target_floor > player["floor"] else -1
                
                # Changement d'étage
                if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                    old_floor = player["floor"]
                    old_position = player["position"]
                    
                    # Utiliser le système d'ascenseur du jeu
                    self.movement.change_floor(player, direction)
                    self.last_floor_change = pygame.time.get_ticks()
                    
                    # Vérifier que le changement d'étage a bien été effectué
                    if self.debug_movement:
                        print(f"Changement d'étage: {old_floor} -> {player['floor']}")
                        print(f"Changement de position: {old_position} -> {player['position']}")
                        
                        expected_new_y = self.movement.floor_positions[player["floor"]]
                        if abs(player["position"][1] - expected_new_y) > 2:
                            print(f"ALERTE: Position Y incorrecte après changement d'étage!")
                            print(f"  Devrait être: {expected_new_y}, est: {player['position'][1]}")
                            # Forcer la correction
                            player["position"] = (player["position"][0], expected_new_y)
        else:
            # Sur le bon étage, se diriger vers la cible
            target_x = target_npc["position"][0]
            if abs(player["position"][0] - target_x) > 30:  # Distance plus grande pour éviter les oscillations
                # Déplacer vers la cible
                if player["position"][0] < target_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Sprite face droite
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Sprite face gauche
            else:
                # On est assez proche, rester immobile
                player["index"] = 3  # Sprite face avant-chaussée
        if not self.target_npc or self.game_phase == "deduction":
            # Si on n'est pas déjà au rez-de-chaussée, y aller
            if player["floor"] != 0:
                # Se diriger vers l'ascenseur (x entre 243 et 287)
                elevator_x = 265
                if abs(player["position"][0] - elevator_x) > 5:
                    # Déplacer vers l'ascenseur
                    if player["position"][0] < elevator_x:
                        player["position"] = (player["position"][0] + 3, player["position"][1])
                        player["index"] = 5  # Sprite face droite
                    else:
                        player["position"] = (player["position"][0] - 3, player["position"][1])
                        player["index"] = 1  # Sprite face gauche
                else:
                    # Descendre d'un étage en utilisant l'ascenseur
                    if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                        # Utiliser le système d'ascenseur du jeu
                        self.movement.change_floor(player, -1)
                        self.last_floor_change = pygame.time.get_ticks()
                        print(f"Descente: Étage {player['floor']} -> {player['floor']-1}, position Y = {player['position'][1]}")
            return
        
        # Trouver l'étage de la cible
        target_npc = self.images.get(self.target_npc)
        if not target_npc:
            print(f"PNJ cible introuvable: {self.target_npc}")
            return
            
        target_floor = target_npc["floor"]
        
        # Debug - afficher les positions et étages
        if self.debug_movement:
            print(f"Détective: étage {player['floor']}, position {player['position'][1]}")
            print(f"Cible {self.target_npc}: étage {target_floor}, position {target_npc['position'][1]}")
            
            # Vérification avec les positions de sol
            detective_floor_y = self.movement.floor_positions[player['floor']]
            target_floor_y = self.movement.floor_positions[target_floor]
            print(f"Position Y attendue pour détective: {detective_floor_y}, réelle: {player['position'][1]}")
            print(f"Position Y attendue pour cible: {target_floor_y}, réelle: {target_npc['position'][1]}")
        
        # Si on n'est pas sur le bon étage, utiliser l'ascenseur
        if player["floor"] != target_floor:
            # Se diriger vers l'ascenseur (x entre 243 et 287)
            elevator_x = 265
            if abs(player["position"][0] - elevator_x) > 5:
                # Déplacer vers l'ascenseur
                if player["position"][0] < elevator_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Sprite face droite
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Sprite face gauche
                
                if self.debug_movement:
                    print(f"Se déplace vers l'ascenseur: {player['position'][0]}")
            else:
                # On est à l'ascenseur, prêt à changer d'étage
                # Forcer la position x à être dans l'ascenseur
                player["position"] = (elevator_x, player["position"][1])
                
                # Déterminer si on monte ou descend
                direction = 1 if target_floor > player["floor"] else -1
                
                # Changement d'étage
                if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                    if self.debug_movement:
                        print(f"Dans l'ascenseur: changement de l'étage {player['floor']} à {player['floor'] + direction}")
                        print(f"Position Y avant: {player['position'][1]}")
                    
                    # Utiliser le système d'ascenseur du jeu
                    old_floor = player["floor"]
                    self.movement.change_floor(player, direction)
                    self.last_floor_change = pygame.time.get_ticks()
                    
                    # Vérifier le changement
                    if self.debug_movement:
                        print(f"Position Y après: {player['position'][1]}")
                        if player["floor"] != old_floor + direction:
                            print(f"ERREUR: Changement d'étage incorrect! Attendu: {old_floor + direction}, Obtenu: {player['floor']}")
        else:
            # Sur le bon étage, se diriger vers la cible
            target_x = target_npc["position"][0]
            if abs(player["position"][0] - target_x) > 30:  # Distance plus grande pour éviter les oscillations
                # Déplacer vers la cible
                if player["position"][0] < target_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Sprite face droite
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Sprite face gauche
                
                if self.debug_movement:
                    print(f"Se déplace vers la cible: {player['position'][0]}")
            else:
                # On est assez proche, rester immobile
                player["index"] = 3  # Sprite face avant
    
    def start_dialogue_automatically(self):
        """Commence automatiquement un dialogue lorsque le détective rencontre sa cible"""
        # Délai pour éviter de déclencher le dialogue trop rapidement
        current_time = pygame.time.get_ticks()
        if hasattr(self, "last_dialogue_end") and current_time - self.last_dialogue_end < 1500:
            return
        
        if self.debug_movement:
            player = self.images[self.player_id]
            target_npc = self.images.get(self.target_npc)
            if target_npc:
                print(f"Début dialogue: Détective à l'étage {player['floor']}, PNJ {self.target_npc} à l'étage {target_npc.get('floor')}")
            
        self.dialogue_active = True
        self.dialogue_progress = 0
        self.last_dialogue_time = current_time
        
    def advance_dialogue_automatically(self):
        """Avance automatiquement dans le dialogue après un certain délai"""
        if not self.dialogue_active:
            return
            
        current_time = pygame.time.get_ticks()
        # Délai entre chaque dialogue (plus court en mode accéléré)
        dialogue_delay = 500 if self.fast_mode else 2000
        
        if current_time - self.last_dialogue_time > dialogue_delay:
            self.dialogue_progress += 1
            self.last_dialogue_time = current_time
            
            # Si on a terminé le dialogue actuel
            if self.dialogue_progress >= len(self.current_dialogue):
                self.dialogue_active = False
                self.dialogue_progress = 0
                self.last_dialogue_end = current_time
                
                # Si on était en conversation avec le target_npc, passer au suivant
                if self.active_npc == self.target_npc:
                    self.set_next_target()
    
    def advance_deduction_automatically(self):
        """Avance automatiquement dans les déductions"""
        if self.game_phase != "deduction" or len(self.deductions) == 0:
            return
            
        current_time = pygame.time.get_ticks()
        # Délai entre chaque déduction (plus court en mode accéléré)
        deduction_delay = 800 if self.fast_mode else 3000
        
        if not hasattr(self, "last_deduction_time") or current_time - self.last_deduction_time > deduction_delay:
            self.current_deduction += 1
            self.last_deduction_time = current_time
            
            # Si on a terminé toutes les déductions
            if self.current_deduction >= len(self.deductions):
                self.game_phase = "conclusion"
                self.conclusion = self.case_processor.get_conclusion()
    
    def update(self):
        player = self.images[self.player_id]
        
        # Vérifier que la position Y correspond bien à l'étage
        current_floor = player["floor"]
        expected_y = self.movement.floor_positions[current_floor]
        actual_y = player["position"][1]
        
        # Si la position Y ne correspond pas à l'étage, la corriger
        if abs(actual_y - expected_y) > 2:  # Petite tolérance
            if self.debug_movement:
                print(f"CORRECTION: Détective à l'étage {current_floor} mais position Y = {actual_y}, devrait être {expected_y}")
            player["position"] = (player["position"][0], expected_y)
        
        # Ne pas permettre le mouvement pendant un dialogue
        if not self.dialogue_active and self.game_phase in ["exploration", "deduction"]:
            # Déplacement autonome du détective
            self.move_detective_autonomously()
            
            # Mettre à jour le PNJ actif
            self.active_npc = None
            
            # Vérifier les collisions avec les PNJ
            player_rect = pygame.Rect(player["position"], (50, 50))
            for npc_id in self.active_npcs:
                npc = self.images.get(npc_id)
                if not npc or not npc.get("active", True):
                    continue
                    
                # Ne pas interagir avec les PNJ d'autres étages
                if npc.get('floor') != player.get('floor'):
                    continue
                    
                npc_rect = pygame.Rect(npc["position"], (50, 50))
                
                if player_rect.colliderect(npc_rect):
                    self.active_npc = npc_id
                    # Si on rencontre le PNJ cible, commencer automatiquement le dialogue
                    if self.active_npc == self.target_npc and not self.dialogue_active:
                        self.start_dialogue_automatically()
                    break
        
        # Mettre à jour le comportement des PNJ
        self.update_npcs()
                    
        # Mettre à jour les rectangles de collision
        update_rect(self.images)
        
        # Avancer le dialogue automatiquement si actif
        self.advance_dialogue_automatically()
        
        # Avancer les déductions automatiquement
        self.advance_deduction_automatically()
        
    def update_npcs(self):
        """Met à jour tous les PNJs"""
        # N'update que les PNJ qui sont actifs
        for npc_id in self.active_npcs:
            npc = self.images.get(npc_id)
            if npc and npc.get("active", True) and not self.dialogue_active:
                # S'assurer que le PNJ reste à son étage assigné
                npc_number = int(npc_id[3:])
                correct_floor = npc_number
                
                # Vérifier si la position Y correspond bien à l'étage
                expected_y = self.movement.floor_positions[correct_floor]
                actual_y = npc["position"][1]
                
                # Si la position Y ne correspond pas à l'étage, la corriger
                if abs(actual_y - expected_y) > 2:  # Petite tolérance
                    if self.debug_movement:
                        print(f"CORRECTION: {npc_id} à l'étage {correct_floor} mais position Y = {actual_y}, devrait être {expected_y}")
                    npc["position"] = (npc["position"][0], expected_y)
                
                # S'assurer que le numéro d'étage est correct
                if npc.get('floor') != correct_floor:
                    if self.debug_movement:
                        print(f"CORRECTION: {npc_id} a l'étage {npc.get('floor')}, devrait être {correct_floor}")
                    npc['floor'] = correct_floor
                    
                # Mise à jour du comportement
                self.update_npc_behavior(npc)

    def update_npc_behavior(self, npc):
        """Met à jour le comportement des PNJ"""
        # Changer d'état selon un timer
        current_time = pygame.time.get_ticks()
        
        # Assurer que le PNJ reste sur son étage
        npc_id = npc.get("id", "")
        if npc_id.startswith("npc"):
            npc_number = int(npc_id[3:])
            npc_floor = npc_number
            
            # Corriger la position Y si nécessaire
            if npc.get("floor") != npc_floor:
                npc["floor"] = npc_floor
                npc["position"] = (npc["position"][0], self.movement.floor_positions[npc_floor])
        
        # États: "idle", "walking", "stressed"
        if "last_state_change" not in npc:
            npc["last_state_change"] = current_time
            npc["state"] = "idle"
            npc["target_pos"] = None
            npc["wait_time"] = random.randint(3000, 7000)  # 3-7 secondes
        
        # Changer d'état si nécessaire
        time_since_change = current_time - npc["last_state_change"]
        
        if npc["state"] == "idle" and time_since_change > npc["wait_time"]:
            # Passer à l'état walking
            npc["state"] = "walking"
            
            # Choisir une position cible sur le même étage (limité par les bords)
            floor_y = self.movement.floor_positions[npc["floor"]]
            npc["target_pos"] = (random.randint(100, 500), floor_y)
            npc["last_state_change"] = current_time
        
        elif npc["state"] == "walking":
            # Si une cible est définie, s'y déplacer
            if npc["target_pos"]:
                # Calculer la distance à la cible
                dx = npc["target_pos"][0] - npc["position"][0]
                dy = npc["target_pos"][1] - npc["position"][1]
                distance = math.hypot(dx, dy)
                
                # Culpabilité influence la vitesse et le mouvement
                speed_factor = 0.8 + (npc.get("guilt", 0.1) * 0.5)
                jitter = npc.get("guilt", 0.1) * 2.0
                
                # Ajout d'un léger mouvement aléatoire pour les PNJ stressés
                dx += random.uniform(-jitter, jitter)
                dy += random.uniform(-jitter, jitter)
                
                # Si on est arrivé à destination
                if distance < 5:
                    npc["state"] = "idle"
                    npc["wait_time"] = random.randint(3000, 7000)
                    npc["last_state_change"] = current_time
                else:
                    # Déplacement vers la cible
                    speed = 2.0 * speed_factor
                    # Garder uniquement le déplacement horizontal, préserver la position Y de l'étage
                    new_x = npc["position"][0] + (dx / distance) * speed
                    new_y = self.movement.floor_positions[npc["floor"]]  # Forcer à rester sur l'étage
                    npc["position"] = (new_x, new_y)
                    
                    # Animation selon la direction
                    if dx > 0:
                        npc["index"] = 5  # Droite
                    elif dx < 0:
                        npc["index"] = 1  # Gauche
                    else:
                        npc["index"] = 3  # Face
    
    def render(self):
        # Fond
        self.screen.fill((0, 0, 0))
        
        # Dessiner l'image de fond
        bg = self.images.get("background", {})
        self.screen.blit(bg.get("image", None), bg.get("position", (0, 0)))
        
        # Dessiner les indices d'étage
        floors = ["Rez-de-chaussée", "1er étage", "2ème étage", "3ème étage", "4ème étage", "5ème étage"]
        for i, y in enumerate(self.movement.floor_positions):
            draw_text(self.screen, floors[i], (20, y - 20), color=(200, 200, 200))
        
        # Dessiner les personnages (seulement ceux de l'étage actuel)
        current_floor = self.images[self.player_id]["floor"]
        
        # Afficher étage actuel pour déboguer
        draw_text(self.screen, f"Étage actuel: {floors[current_floor]}", (400, 20), color=(255, 255, 0))
        
        # Déboguer l'affichage des PNJ
        if self.debug_movement and hasattr(self, 'debug_render_counter'):
            self.debug_render_counter += 1
            if self.debug_render_counter >= 60:  # Afficher toutes les secondes environ
                print(f"Rendu: étage actuel = {current_floor}, Y = {self.images[self.player_id]['position'][1]}")
                for entity_id, entity in self.images.items():
                    if entity_id not in ["background", self.player_id] and entity_id in self.active_npcs:
                        print(f"  PNJ {entity_id} à l'étage {entity.get('floor', -1)}, Y = {entity.get('position', (0, 0))[1]}")
                self.debug_render_counter = 0
        else:
            self.debug_render_counter = 0
        
        # Afficher seulement les entités de l'étage actuel
        for entity_id, entity in self.images.items():
            if entity_id == "background":
                continue
                
            # Ne pas dessiner les PNJ inactifs
            if entity_id not in ["background", self.player_id] and (entity_id not in self.active_npcs or not entity.get("active", True)):
                continue
                
            # Vérifier si l'entité est au même étage que le joueur
            if entity.get('floor', -1) == current_floor:
                self.screen.blit(entity["image"], entity["position"])
                
                # Afficher l'étage du personnage pour déboguer
                if self.debug_movement:
                    floor_text = f"Étage: {entity.get('floor', -1)}"
                    draw_text(self.screen, floor_text, (entity["position"][0], entity["position"][1] - 25), color=(255, 255, 0))
                
                # Dessiner indicateur pour le PNJ cible
                if entity_id == self.target_npc:
                    pygame.draw.circle(
                        self.screen, 
                        (0, 255, 0), 
                        (entity["position"][0] + 25, entity["position"][1] - 15), 
                        8
                    )
                
                # Dessiner indicateur de PNJ interactif
                if entity.get('npc', False) and entity_id == self.active_npc:
                    pygame.draw.circle(
                        self.screen, 
                        (255, 255, 0), 
                        (entity["position"][0] + 25, entity["position"][1] - 10), 
                        5
                    )
        
        # Interface utilisateur
        self.render_ui()
        
        # Afficher le dialogue ou les déductions
        if self.dialogue_active:
            self.render_dialogue()
        elif self.game_phase == "deduction" and len(self.deductions) > 0:
            self.render_deduction()
        elif self.game_phase == "conclusion" and self.conclusion:
            self.render_conclusion()
            
        # Affichage des contrôles
        if self.show_controls:
            self.render_controls()
            
        pygame.display.flip()
    
    def render_ui(self):
        # Fond de la barre d'interface
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 650, 600, 50))
        
        # Afficher l'étape actuelle
        phase_text = {
            "exploration": "Phase: Investigation",
            "deduction": "Phase: Déduction",
            "conclusion": "Phase: Conclusion"
        }.get(self.game_phase, "Phase: Investigation")
        
        draw_text(self.screen, phase_text, (10, 655), color=(255, 255, 255))
        
        # Afficher le compteur de PNJ interrogés
        interrogation_count = f"Interrogés: {len(self.interrogated_npcs)}/{len(self.active_npcs)}"
        draw_text(self.screen, interrogation_count, (200, 655), color=(255, 200, 0))
        
        # Afficher le statut avec le nom du suspect
        status_text = ""
        if self.game_phase == "exploration":
            if self.dialogue_active and self.target_npc:
                suspect_name = self.case_processor.npc_to_suspect.get(self.target_npc, self.target_npc)
                status_text = f"Interroge: {suspect_name}"
            elif self.target_npc:
                suspect_name = self.case_processor.npc_to_suspect.get(self.target_npc, self.target_npc)
                if self.images[self.player_id]["floor"] != self.images.get(self.target_npc, {}).get("floor", -1):
                    status_text = f"Va voir: {suspect_name}"
                else:
                    status_text = f"S'approche de: {suspect_name}"
            else:
                status_text = "Retour au rez-de-chaussée"
        elif self.game_phase == "deduction":
            status_text = f"Analyse: ({self.current_deduction + 1}/{len(self.deductions)})"
        elif self.game_phase == "conclusion":
            status_text = "Conclut l'enquête"
            
        draw_text(self.screen, status_text, (350, 655), color=(200, 200, 200))
    
    def render_dialogue(self):
        # Panneau de dialogue
        pygame.draw.rect(self.screen, (40, 40, 40, 200), (50, 450, 500, 180))
        pygame.draw.rect(self.screen, (200, 200, 200), (50, 450, 500, 180), 2)
        
        # Afficher le dialogue actuel
        if 0 <= self.dialogue_progress < len(self.current_dialogue):
            current_text = self.current_dialogue[self.dialogue_progress]
            
            # Séparer le nom du personnage et le texte
            parts = current_text.split(": ", 1)
            if len(parts) >= 2:
                speaker, text = parts
                # Nom du personnage en couleur
                draw_text(self.screen, speaker + ":", (70, 470), color=(255, 255, 0))
                
                # Texte du dialogue (avec retour à la ligne)
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if len(test_line) < 60:  # Limite de caractères par ligne
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                for i, line in enumerate(lines):
                    draw_text(self.screen, line, (70, 500 + i * 25))
    
    def render_deduction(self):
        # Panneau de déduction
        pygame.draw.rect(self.screen, (40, 40, 60, 230), (50, 100, 500, 500))
        pygame.draw.rect(self.screen, (200, 200, 220), (50, 100, 500, 500), 2)
        
        # Titre
        draw_text(self.screen, "Analyse du Détective", (200, 120), font=self.title_font, color=(255, 255, 0))
        
        # Afficher les déductions actuelles
        if self.current_deduction < len(self.deductions):
            y_pos = 170
            for i in range(max(0, self.current_deduction - 8), self.current_deduction + 1):
                if i < len(self.deductions):
                    deduction = self.deductions[i]
                    
                    # Mettre en évidence la déduction actuelle
                    color = (255, 255, 255)
                    if i == self.current_deduction:
                        color = (0, 255, 0)
                        
                    # Ajouter un préfixe pour les éléments importants
                    prefix = "• "
                    
                    # Diviser le texte en lignes
                    text = prefix + deduction
                    words = text.split()
                    lines = []
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) < 60:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    for line in lines:
                        draw_text(self.screen, line, (70, y_pos), color=color)
                        y_pos += 25
                        
            # Indication de progression
            progress_text = f"Déduction {self.current_deduction + 1}/{len(self.deductions)}"
            draw_text(self.screen, progress_text, (70, 550), color=(200, 200, 200))
    
    def render_conclusion(self):
        # Panneau de conclusion
        pygame.draw.rect(self.screen, (40, 40, 60, 230), (50, 100, 500, 500))
        pygame.draw.rect(self.screen, (200, 200, 220), (50, 100, 500, 500), 2)
        
        # Titre
        draw_text(self.screen, "Conclusion de l'Enquête", (180, 120), font=self.title_font, color=(255, 215, 0))
        
        # Détails
        y_pos = 180
        
        # Présentation du coupable
        culprit_text = f"Le coupable est: {self.conclusion['culprit']}"
        draw_text(self.screen, culprit_text, (100, y_pos), color=(255, 100, 100))
        y_pos += 40
        
        # Confiance
        confidence = self.conclusion["confidence"] * 100
        confidence_text = f"Confiance dans cette conclusion: {confidence:.1f}%"
        draw_text(self.screen, confidence_text, (100, y_pos), color=(255, 255, 255))
        y_pos += 40
        
        # Résultat
        result_text = "Enquête réussie!" if self.conclusion["correct"] else "Enquête échouée..."
        result_color = (0, 255, 0) if self.conclusion["correct"] else (255, 0, 0)
        draw_text(self.screen, result_text, (100, y_pos), font=self.title_font, color=result_color)
        y_pos += 60
        
        # Message de fin
        end_message = "Le détective a correctement identifié le coupable!" if self.conclusion["correct"] else "Le détective s'est trompé dans son enquête."
        draw_text(self.screen, end_message, (100, y_pos), color=(255, 255, 255))
        y_pos += 40
        
        # Instructions
        draw_text(self.screen, "Appuyez sur ÉCHAP pour quitter", (200, 500), color=(200, 200, 200))
    
    def render_controls(self):
        help_text = [
            "Contrôles:",
            "ESPACE: Intervention manuelle",
            "F: Accélérer/ralentir la simulation",
            "M: Activer/désactiver debug mouvement",
            "P: Afficher positions de tous les personnages",
            "0-3: Forcer l'étage (0-3)",
            "H: Afficher/masquer l'aide",
            "ÉCHAP: Quitter"
        ]
        
        # Fond semi-transparent
        help_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 180))
        self.screen.blit(help_surface, (150, 200))
        
        # Texte d'aide
        for i, line in enumerate(help_text):
            draw_text(self.screen, line, (170, 210 + i * 25), color=(220, 220, 220))
            
        # Statut du mode rapide
        mode_text = "Mode Rapide: ACTIVÉ" if self.fast_mode else "Mode Rapide: Désactivé"
        draw_text(self.screen, mode_text, (170, 210 + len(help_text) * 25), 
                 color=(255, 200, 0) if self.fast_mode else (180, 180, 180))
        
        # Statut du debug mouvement
        debug_text = "Debug Mouvement: ACTIVÉ" if self.debug_movement else "Debug Mouvement: Désactivé"
        draw_text(self.screen, debug_text, (170, 210 + (len(help_text) + 1) * 25), 
                 color=(255, 200, 0) if self.debug_movement else (180, 180, 180))
    
    def run(self, json_data):
        """Démarre le jeu avec un cas particulier"""
        self.load_case(json_data)
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        return self.conclusion["correct"] if self.conclusion else False

# Point d'entrée du programme
if __name__ == "__main__":
    # Charger le JSON du cas
    with open("case.json", "r") as f:
        case_data = json.load(f)
    
    game = DetectiveGame()
    result = game.run(case_data)
    print("Résultat de l'enquête:", "Réussite" if result else "Échec")