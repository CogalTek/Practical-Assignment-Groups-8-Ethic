import pygame

class InteractionSystem:
    def __init__(self, brain, quests):
        self.brain = brain
        self.quests = quests
        self.active = False
        self.current_npc = None
        self.conversation = []
        self.player_text = ""
        self.typing = False

    def start_dialogue(self, npc_id):
        self.active = True
        self.current_npc = npc_id
        initial_greeting = self.brain.process_input(npc_id, '')
        self.conversation = [
            f"{npc_id}: {initial_greeting}",
            "Appuyez sur H pour l'aide"
        ]
        print(f"Début du dialogue avec {npc_id}, self.active = {self.active}")

    def process_input(self, npc_id, text):
        if not text.strip():  # Ignorer les entrées vides
            return "..."
            
        response = self.brain.process_input(npc_id, text)
        self.conversation.append(f"Vous: {text}")
        self.conversation.append(f"{npc_id}: {response}")
        
        # Mise à jour des quêtes basées sur le dialogue
        quest_updated = self.quests.update(npc_id, response)
        
        # Limiter la taille de l'historique de conversation
        if len(self.conversation) > 10:
            self.conversation = self.conversation[-10:]
        
        return response
    
    def end_dialogue(self):
        print("Fin du dialogue")
        self.active = False
        self.current_npc = None
        self.player_text = ""
        
    def update_typing(self, event):
        if not self.active:
            return
            
        if event.key == pygame.K_BACKSPACE:
            self.player_text = self.player_text[:-1]
        elif event.key == pygame.K_RETURN:
            # Traiter l'entrée et réinitialiser
            if self.player_text.strip():
                self.process_input(self.current_npc, self.player_text)
                self.player_text = ""
        elif event.unicode.isprintable():
            # Limiter la longueur du texte
            if len(self.player_text) < 40:
                self.player_text += event.unicode
                
    def draw_input_field(self, screen, font, rect):
        import pygame
        # Dessiner le champ de saisie
        pygame.draw.rect(screen, (50, 50, 50), rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        
        # Afficher le texte saisi
        text_surface = font.render(self.player_text + ("|" if pygame.time.get_ticks() % 1000 < 500 else ""), True, (255, 255, 255))
        screen.blit(text_surface, (rect.x + 10, rect.y + 10))