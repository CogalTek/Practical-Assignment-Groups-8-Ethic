class QuestSystem:
    def __init__(self):
        self.objectives = [
            {'type': 'interview', 'target': 'npc03', 'description': "Interroger le concierge (npc03)", 'completed': False, 'keywords': ['clé', 'arme', 'grenier']},
            {'type': 'collect', 'item': 'clé', 'location': 1, 'description': "Trouver la clé cachée au 1er étage", 'completed': False},
            {'type': 'goto', 'floor': 5, 'description': "Aller au 5ème étage avec la clé", 'completed': False, 'requires': ['clé']},
            {'type': 'collect', 'item': 'arme', 'location': 5, 'description': "Trouver l'arme du crime", 'completed': False},
            {'type': 'interview', 'target': 'npc05', 'description': "Confronter le suspect avec les preuves", 'completed': False, 'keywords': ['coupable', 'arme', 'crime'], 'requires': ['arme']}
        ]
        self.inventory = []
        self.current_step = 0
        self.clues_found = []
        self.suspect_points = {
            'npc01': 0,
            'npc02': 0,
            'npc03': 0,
            'npc04': 0,
            'npc05': 0
        }
        self.max_steps = len(self.objectives)
        self.quest_completed = False

    def update(self, npc_id, dialogue):
        if self.current_step >= len(self.objectives):
            return False
            
        current_obj = self.objectives[self.current_step]
        
        # Objectif de type interview
        if current_obj['type'] == 'interview' and npc_id == current_obj['target']:
            # Vérifier si les mots-clés de l'objectif sont dans le dialogue
            if any(keyword in dialogue.lower() for keyword in current_obj.get('keywords', [])):
                self.complete_objective()
                return True
                
        # Accumuler des points de suspicion basés sur le dialogue
        for suspect_keyword in ['suspect', 'coupable', 'crime', 'mensonge']:
            if suspect_keyword in dialogue.lower():
                # Extraire le nom du NPC mentionné dans le dialogue
                for i in range(1, 6):
                    npc_name = f"npc0{i}"
                    if npc_name in dialogue.lower() or f"voisin {i}" in dialogue.lower():
                        self.suspect_points[npc_name] += 1
                        if npc_name not in self.clues_found:
                            self.clues_found.append(f"Indice sur {npc_name}")
                        break
        
        # Ajouter des indices basés sur des mots-clés importants
        for keyword in ['arme', 'clé', 'grenier', 'nuit', 'bruit', 'étage']:
            if keyword in dialogue.lower() and keyword not in self.clues_found:
                self.clues_found.append(f"Indice: {keyword}")
        
        return False

    def complete_objective(self):
        if self.current_step < len(self.objectives):
            self.objectives[self.current_step]['completed'] = True
            print(f"Objectif complété: {self.objectives[self.current_step]['description']}!")
            self.current_step += 1
            
            # Vérifier si la quête est terminée
            if self.current_step >= len(self.objectives):
                self.quest_completed = True
                print("Enquête terminée! Vous avez résolu l'affaire!")
            else:
                print(f"Nouvel objectif: {self.objectives[self.current_step]['description']}")

    def add_item(self, item):
        if item not in self.inventory:
            self.inventory.append(item)
            print(f"{item.capitalize()} ajouté à l'inventaire!")
            
            # Vérifier si cet objet complète un objectif
            if self.current_step < len(self.objectives):
                current_obj = self.objectives[self.current_step]
                if current_obj['type'] == 'collect' and item == current_obj['item']:
                    self.complete_objective()
            
            # Vérifier les objectifs futurs qui pourraient être débloqués
            self.check_requirements()
    
    def check_requirements(self):
        # Si l'objectif courant a des prérequis, vérifier s'ils sont remplis
        if self.current_step < len(self.objectives):
            current_obj = self.objectives[self.current_step]
            if 'requires' in current_obj:
                if all(item in self.inventory for item in current_obj['requires']):
                    print(f"Prérequis pour '{current_obj['description']}' remplis!")
    
    def check_floor_objective(self, player_floor):
        if self.current_step < len(self.objectives):
            current_obj = self.objectives[self.current_step]
            if current_obj['type'] == 'goto' and player_floor == current_obj['floor']:
                # Vérifier si les prérequis sont remplis
                if 'requires' in current_obj:
                    if all(item in self.inventory for item in current_obj['requires']):
                        self.complete_objective()
                else:
                    self.complete_objective()

    def get_current_objective(self):
        if self.current_step < len(self.objectives):
            return self.objectives[self.current_step]['description']
        else:
            return "Tous les objectifs sont complétés!"
    
    def get_completion_percentage(self):
        completed = sum(1 for obj in self.objectives if obj['completed'])
        return (completed / len(self.objectives)) * 100
    
    def get_clues_summary(self):
        if not self.clues_found:
            return "Aucun indice collecté pour le moment."
        return ", ".join(self.clues_found[-3:])  # Afficher les 3 derniers indices