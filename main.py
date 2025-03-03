import pygame
import sys
from src.assets import load_images, get_player, update_rect
from src.movement import MovementSystem
from src.nlp import NPCBrain
from src.interaction import InteractionSystem
from src.quests import QuestSystem
from src.tools import draw_text

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Enquête - IA Deep Learning")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Systèmes principaux
        self.movement = MovementSystem()
        self.brain = NPCBrain()
        self.quests = QuestSystem()
        self.interaction = InteractionSystem(self.brain, self.quests)
        
        # Chargement des ressources
        self.images = load_images()
        self.player_id = get_player(self.images)
        self.load_audio()
        
        # États du jeu
        self.running = True
        self.active_npc = None
        self.player_text = ""
        self.game_phase = "investigation"
        self.show_controls = False
        self.show_debug = False
        self.collectable_items = {
            (421, 168): ('arme', 5),
            (300, 461): ('clé', 1)
        }

    def load_audio(self):
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("./content/music.ogg")
            pygame.mixer.music.play(-1)
            self.movement.set_elevator_sound(pygame.mixer.Sound("./content/ascenseur.wav"))
        except pygame.error:
            print("⚠️ Fichiers audio non trouvés. Le jeu continuera sans son.")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.interaction.active:
                    # Gérer la touche ESC pour fermer le dialogue
                    if event.key == pygame.K_ESCAPE:
                        self.interaction.end_dialogue()
                    else:
                        self.interaction.update_typing(event)
                else:
                    self.handle_keydown(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            print("coucou sans active")
            if self.interaction.active:
                print("coucou")
                self.interaction.end_dialogue()
                pygame.time.delay(10)  # Pause pour s'assurer que l'état est bien mis à jour
                self.interaction.active = False  # Redondance pour être sûr
                return
        elif event.key == pygame.K_SPACE and self.active_npc:
            self.interaction.start_dialogue(self.active_npc)
        elif event.key == pygame.K_e:
            self.try_collect_item()
        elif event.key == pygame.K_h:
            self.show_controls = not self.show_controls
        elif event.key == pygame.K_d:
            self.show_debug = not self.show_debug

    def try_collect_item(self):
        player = self.images[self.player_id]
        items_to_remove = []
        
        for (x, y), (item, floor) in self.collectable_items.items():
            if (abs(player['position'][0] - x) < 50 and 
                player['floor'] == floor):
                
                self.quests.add_item(item)
                print(f"{item.capitalize()} collecté!")
                items_to_remove.append((x, y))
        
        # Supprimer les objets collectés après l'itération
        for position in items_to_remove:
            del self.collectable_items[position]

    def update(self):
        keys = pygame.key.get_pressed()
        player = self.images[self.player_id]
        
        # Ne pas permettre le mouvement pendant un dialogue
        if not self.interaction.active:
            self.movement.handle_player_movement(player, keys)
            
            # Vérifier les objectifs basés sur l'étage
            self.quests.check_floor_objective(player['floor'])
        
        # Réinitialiser le PNJ actif
        self.active_npc = None
        
        # Vérifier les collisions avec les PNJ
        player_rect = pygame.Rect(player['position'], (50, 50))
        for npc_id in ["npc01", "npc02", "npc03", "npc04", "npc05"]:
            npc = self.images[npc_id]
            
            # Ne pas interagir avec les PNJ d'autres étages
            if npc['floor'] != player['floor']:
                continue
                
            npc_rect = pygame.Rect(npc['position'], (50, 50))
            
            if player_rect.colliderect(npc_rect):
                self.active_npc = npc_id
                break  # Priorité au premier PNJ détecté
        
        # Mettre à jour le comportement des PNJ si pas en mode dialogue
        if not self.interaction.active:
            for npc_id in ["npc01", "npc02", "npc03", "npc04", "npc05"]:
                npc = self.images[npc_id]
                self.movement.update_npc(npc, player['position'], self.game_phase)
                update_rect(self.images)  # Mettre à jour les rectangles de collision
        
        # Vérifier la condition de fin de jeu
        if self.quests.quest_completed and not self.interaction.active:
            self.game_phase = "solved"
    
    def render(self):
        # Fond
        self.screen.fill((0, 0, 0))
        
        # Dessiner l'image de fond
        bg = self.images.get("background", {})
        self.screen.blit(bg.get("image", None), bg.get("position", (0, 0)))
        
        # Dessiner les objets collectables
        for (x, y), (item_name, floor) in self.collectable_items.items():
            # Ne dessiner que les objets de l'étage actuel
            if self.images[self.player_id]['floor'] == floor:
                item_color = (255, 215, 0) if item_name == "clé" else (255, 0, 0)
                pygame.draw.circle(self.screen, item_color, (x, y), 8)
        
        # Dessiner l'ascenseur
        # pygame.draw.rect(self.screen, (100, 100, 100), (243, 170, 44, 400))
        
        # Dessiner les indices d'étage
        floors = ["Rez-de-chaussée", "1er étage", "2ème étage", "3ème étage", "4ème étage", "5ème étage"]
        for i, y in enumerate(self.movement.floor_positions):
            draw_text(self.screen, floors[i], (20, y - 20), color=(200, 200, 200))
        
        # Dessiner les personnages (seulement ceux de l'étage actuel)
        current_floor = self.images[self.player_id]['floor']
        for entity_id, entity in self.images.items():
            if entity_id == "background":
                continue
                
            if entity.get('floor', -1) == current_floor:
                self.screen.blit(entity["image"], entity["position"])
                
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
        
        # Mode dialogue
        if self.interaction.active:
            self.render_dialogue()
        
        # Affichage des contrôles
        if self.show_controls:
            self.render_controls()
            
        # Affichage debug
        if self.show_debug:
            self.render_debug()
            
        # Écran de fin si l'enquête est résolue
        if self.game_phase == "solved":
            self.render_end_screen()
            
        pygame.display.flip()
    
    def render_ui(self):
        # Fond de la barre d'interface
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 650, 600, 50))
        
        # Objectif actuel (en haut à gauche)
        current_obj = self.quests.get_current_objective()
        draw_text(self.screen, f"Objectif: {current_obj}", (10, 655), color=(255, 255, 255))
        
        # Barre de progression (en bas à gauche)
        progress = self.quests.get_completion_percentage()
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 680, 200, 10))  # Fond de la barre
        pygame.draw.rect(self.screen, (0, 200, 0), (10, 680, int(progress * 2), 10))  # Barre de progression
        
        # Inventaire (en haut à droite)
        inventory_text = "Inventaire: " + ", ".join(self.quests.inventory) if self.quests.inventory else "Inventaire: vide"
        draw_text(self.screen, inventory_text, (400, 655), color=(255, 255, 255))
        
        # Indication d'interaction (au centre, juste au-dessus de la barre d'interface)
        if self.active_npc:
            draw_text(self.screen, "Appuyez sur ESPACE pour parler", (220, 630), color=(255, 255, 0))
        elif any((abs(self.images[self.player_id]['position'][0] - x) < 50 and 
                self.images[self.player_id]['floor'] == floor) 
                for (x, y), (_, floor) in self.collectable_items.items()):
            draw_text(self.screen, "Appuyez sur E pour ramasser", (220, 630), color=(255, 255, 0))
    
    def render_dialogue(self):
        # Panneau de dialogue
        pygame.draw.rect(self.screen, (40, 40, 40, 200), (50, 100, 500, 500))
        pygame.draw.rect(self.screen, (200, 200, 200), (50, 100, 500, 500), 2)
        
        # Titre du dialogue
        npc_id = self.interaction.current_npc
        draw_text(self.screen, f"Conversation avec {npc_id}", (70, 110), color=(255, 255, 0))
        
        # Historique des messages
        for i, message in enumerate(self.interaction.conversation[-8:]):  # Derniers messages uniquement
            draw_text(self.screen, message, (70, 150 + i * 30))
        
        # Champ de saisie
        input_rect = pygame.Rect(70, 520, 460, 40)
        self.interaction.draw_input_field(self.screen, self.font, input_rect)
        
        # Instructions
        draw_text(self.screen, "Appuyez sur ENTRÉE pour envoyer, ÉCHAP pour quitter", (70, 570), color=(150, 150, 150))
    
    def render_controls(self):
        help_text = [
            "Contrôles:",
            "Flèches: Déplacer le personnage",
            "ESPACE: Parler avec un PNJ",
            "E: Ramasser un objet",
            "H: Afficher/masquer l'aide",
            "D: Mode debug",
            "ÉCHAP: Quitter le dialogue"
        ]
        
        # Fond semi-transparent
        help_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 180))
        self.screen.blit(help_surface, (150, 200))
        
        # Texte d'aide
        for i, line in enumerate(help_text):
            draw_text(self.screen, line, (170, 210 + i * 25), color=(220, 220, 220))
    
    def render_debug(self):
        debug_info = [
            f"FPS: {int(self.clock.get_fps())}",
            f"Position joueur: {self.images[self.player_id]['position']}",
            f"Étage: {self.images[self.player_id]['floor']}",
            f"NPJ actif: {self.active_npc}",
            f"Indices trouvés: {len(self.quests.clues_found)}",
            f"Phase: {self.game_phase}"
        ]
        
        # Fond semi-transparent pour le texte de débogage
        debug_surface = pygame.Surface((250, 150), pygame.SRCALPHA)
        debug_surface.fill((0, 0, 50, 150))
        self.screen.blit(debug_surface, (10, 10))
        
        # Afficher les informations de débogage
        for i, info in enumerate(debug_info):
            draw_text(self.screen, info, (20, 20 + i * 22), color=(200, 200, 255))
        
        # Afficher les points de suspicion
        y_pos = 170
        draw_text(self.screen, "Suspicion:", (20, y_pos), color=(255, 100, 100))
        for npc_id, points in self.quests.suspect_points.items():
            y_pos += 20
            draw_text(self.screen, f"{npc_id}: {points}", (20, y_pos), color=(255, 150, 150))
    
    def render_end_screen(self):
        # Superposition semi-transparente
        end_surface = pygame.Surface((600, 700), pygame.SRCALPHA)
        end_surface.fill((0, 0, 0, 200))
        self.screen.blit(end_surface, (0, 0))
        
        # Calculer le coupable basé sur les points de suspicion
        guilty_npc = max(self.quests.suspect_points.items(), key=lambda x: x[1])[0]
        
        # Message de fin
        title_font = pygame.font.Font(None, 48)
        draw_text(self.screen, "Enquête Résolue!", (180, 200), font=title_font, color=(255, 215, 0))
        
        # Détails de la solution
        solution_text = [
            f"Le coupable est: {guilty_npc}",
            "Vous avez trouvé l'arme du crime et les preuves nécessaires.",
            "",
            "Indices collectés:",
            ", ".join(self.quests.clues_found),
            "",
            "Merci d'avoir joué!",
            "",
            "Appuyez sur une touche pour quitter..."
        ]
        
        for i, line in enumerate(solution_text):
            draw_text(self.screen, line, (100, 250 + i * 30))
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Point d'entrée du programme
if __name__ == "__main__":
    game = Game()
    game.run()