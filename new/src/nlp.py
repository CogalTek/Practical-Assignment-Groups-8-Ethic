import random
import numpy as np
from collections import defaultdict
import re

class NPCBrain:
    def __init__(self):
        self.knowledge = {
            'npc01': {
                'clues': [
                    "J'ai entendu du bruit à l'étage 5 hier soir.",
                    "Le voisin du 3ème étage semble suspect, il sort rarement.",
                    "Je n'ai rien à voir avec cette histoire, j'étais absent."
                ],
                'trust': 0.3,
                'guilt': 0.1,
                'personality': 'nerveux',
                'keywords': ['bruit', 'étage', 'suspect', 'voisin', 'absent']
            },
            'npc02': {
                'clues': [
                    "Celui qui habite au 5ème étage possède une arme.",
                    "J'ai vu quelqu'un monter rapidement au grenier la nuit dernière.",
                    "La clé du grenier a disparu récemment, c'est étrange."
                ],
                'trust': 0.5,
                'guilt': 0.2,
                'personality': 'bavard',
                'keywords': ['arme', 'grenier', 'clé', 'disparu', 'étrange']
            },
            'npc03': {
                'clues': [
                    "En tant que concierge, je peux vous dire que la clé est cachée quelque part au 1er étage.",
                    "J'ai vu quelqu'un cacher une arme au 5ème étage.",
                    "Méfiez-vous du voisin du 4ème, il ment constamment."
                ],
                'trust': 0.7,
                'guilt': 0.8,
                'personality': 'serviable',
                'keywords': ['clé', 'arme', 'concierge', 'méfiez', 'ment']
            },
            'npc04': {
                'clues': [
                    "Je n'ai rien vu, laissez-moi tranquille.",
                    "Le concierge est louche, il se promène partout la nuit.",
                    "Je crois avoir entendu un bruit de dispute à l'étage 5."
                ],
                'trust': 0.4,
                'guilt': 0.4,
                'personality': 'méfiant',
                'keywords': ['rien', 'concierge', 'louche', 'dispute', 'bruit']
            },
            'npc05': {
                'clues': [
                    "Je suis innocent! Je n'ai rien fait!",
                    "J'ai perdu ma clé, quelqu'un a dû me la voler.",
                    "Le concierge ment, ne lui faites pas confiance!"
                ],
                'trust': 0.2,
                'guilt': 0.6,
                'personality': 'paniqué',
                'keywords': ['innocent', 'clé', 'voler', 'concierge', 'ment']
            }
        }
        
        # Stockage de l'historique des conversations pour chaque PNJ
        self.conversation_history = defaultdict(list)
        
        # Compteur d'interactions pour simuler l'apprentissage
        self.interaction_count = defaultdict(int)
        
        # Niveau de confiance avec le joueur (simulé)
        self.player_trust = defaultdict(lambda: 0.3)
        
        # Mots-clés importants pour l'enquête
        self.important_keywords = ['arme', 'clé', 'grenier', 'suspect', 'coupable', 'indice', 'nuit', 'bruit']

    def process_input(self, npc_id, text):
        # Si le texte est vide (premier contact), retourner une salutation
        if not text:
            return self.get_greeting(npc_id)
        
        # Convertir en minuscules pour la détection des mots-clés
        text = text.lower()
        
        # Ajouter à l'historique des conversations
        self.conversation_history[npc_id].append(text)
        
        # Incrémenter le compteur d'interactions
        self.interaction_count[npc_id] += 1
        
        # Simuler l'augmentation de la confiance avec le joueur
        if len(text) > 10:  # Si le joueur pose une question élaborée
            self.player_trust[npc_id] += 0.05
            self.player_trust[npc_id] = min(self.player_trust[npc_id], 1.0)
        
        # Détection de mots-clés
        npc_data = self.knowledge[npc_id]
        
        # Vérifier si on a mentionné un autre PNJ
        mentioned_npc = self.detect_other_npcs(text)
        if mentioned_npc:
            return self.talk_about_other_npc(npc_id, mentioned_npc)
        
        # Vérifier les mots-clés importants
        for keyword in self.important_keywords:
            if keyword in text:
                return self.provide_clue(npc_id, keyword)
        
        # Vérifier les mots-clés spécifiques à ce PNJ
        for keyword in npc_data['keywords']:
            if keyword in text:
                return self.provide_clue(npc_id, keyword)
        
        # Si la confiance est suffisante, donner un indice aléatoire
        if self.player_trust[npc_id] > 0.7 and random.random() < 0.3:
            return random.choice(npc_data['clues'])
        
        # Réponse générique basée sur la personnalité
        return self.generate_generic_response(npc_id)
    
    def get_greeting(self, npc_id):
        personality = self.knowledge[npc_id]['personality']
        
        greetings = {
            'nerveux': "Euh... bonjour? Que voulez-vous?",
            'bavard': "Ah! Bonjour! Vous enquêtez sur ce qui s'est passé?",
            'serviable': "Bonjour, je peux vous aider?",
            'méfiant': "Qu'est-ce que vous voulez?",
            'paniqué': "Oh! Vous m'avez fait peur! Que voulez-vous?"
        }
        
        return greetings.get(personality, "Bonjour.")
    
    def detect_other_npcs(self, text):
        for i in range(1, 6):
            if f"npc0{i}" in text or f"voisin {i}" in text or f"personne {i}" in text:
                return f"npc0{i}"
        return None
    
    def talk_about_other_npc(self, speaker_id, mentioned_npc):
        # Relations entre PNJs
        relations = {
            'npc01': {'npc02': 'neutre', 'npc03': 'méfiant', 'npc04': 'amical', 'npc05': 'hostile'},
            'npc02': {'npc01': 'neutre', 'npc03': 'amical', 'npc04': 'hostile', 'npc05': 'méfiant'},
            'npc03': {'npc01': 'hostile', 'npc02': 'amical', 'npc04': 'méfiant', 'npc05': 'neutre'},
            'npc04': {'npc01': 'amical', 'npc02': 'hostile', 'npc03': 'neutre', 'npc05': 'méfiant'},
            'npc05': {'npc01': 'méfiant', 'npc02': 'neutre', 'npc03': 'hostile', 'npc04': 'amical'}
        }
        
        relation = relations[speaker_id][mentioned_npc]
        guilt = self.knowledge[mentioned_npc]['guilt']
        
        responses = {
            'amical': [
                f"C'est quelqu'un de bien, je ne pense pas qu'il soit impliqué.",
                f"On s'entend bien, mais j'ai remarqué qu'il agissait bizarrement récemment."
            ],
            'neutre': [
                f"Je ne le connais pas très bien pour être honnête.",
                f"On se croise parfois dans l'ascenseur, rien de plus."
            ],
            'méfiant': [
                f"Je ne lui fais pas vraiment confiance...",
                f"Il y a quelque chose d'étrange chez lui, surveillez-le."
            ],
            'hostile': [
                f"Ne me parlez pas de cette personne!",
                f"Je suis sûr qu'il cache quelque chose, méfiez-vous!"
            ]
        }
        
        # Si le PNJ mentionné a une forte culpabilité et que le speaker le connaît bien
        if guilt > 0.6 and relation in ['méfiant', 'hostile']:
            return f"Je l'ai vu agir de façon suspecte. Vous devriez l'interroger davantage."
        
        return random.choice(responses[relation])
    
    def provide_clue(self, npc_id, keyword):
        npc_data = self.knowledge[npc_id]
        guilt = npc_data['guilt']
        trust_level = self.player_trust[npc_id]
        
        # Si le PNJ est coupable, il peut mentir ou détourner l'attention
        if guilt > 0.5 and random.random() > trust_level:
            return self.generate_deceptive_response(npc_id, keyword)
        
        # Chercher un indice pertinent pour ce mot-clé
        matching_clues = [clue for clue in npc_data['clues'] if keyword in clue.lower()]
        
        if matching_clues:
            return random.choice(matching_clues)
        elif self.interaction_count[npc_id] > 3:  # Après plusieurs interactions
            return random.choice(npc_data['clues'])  # Donner un indice aléatoire
        else:
            return f"À propos de '{keyword}'... je ne sais pas grand-chose à ce sujet."
    
    def generate_deceptive_response(self, npc_id, keyword):
        deceptive_responses = [
            f"Je ne sais rien à propos de {keyword}.",
            f"Pourquoi vous intéressez-vous à {keyword}? C'est suspect...",
            f"Vous devriez plutôt demander au voisin du dessus, il sait des choses.",
            f"Je préfère ne pas parler de ça.",
            f"Regardez ailleurs, je ne suis pas impliqué dans cette histoire."
        ]
        return random.choice(deceptive_responses)
    
    def generate_generic_response(self, npc_id):
        personality = self.knowledge[npc_id]['personality']
        
        responses = {
            'nerveux': [
                "Je... je ne sais pas trop...",
                "Vous me mettez mal à l'aise avec ces questions.",
                "Je préfère ne pas m'en mêler."
            ],
            'bavard': [
                "Oh, j'aurais bien aimé pouvoir vous aider davantage!",
                "J'ai tellement de choses à vous raconter, mais pas sur ce sujet précis.",
                "Vous savez, il se passe des choses étranges dans cet immeuble..."
            ],
            'serviable': [
                "Je vais essayer de vous aider du mieux que je peux.",
                "Posez-moi des questions plus précises, peut-être?",
                "Si je peux vous être utile, n'hésitez pas."
            ],
            'méfiant': [
                "Pourquoi toutes ces questions?",
                "Je ne suis pas sûr de pouvoir vous faire confiance.",
                "Qu'est-ce que j'y gagne à vous aider?"
            ],
            'paniqué': [
                "Oh mon dieu, je ne sais pas quoi vous dire!",
                "Tout ça me stresse énormément!",
                "Je ne veux pas avoir de problèmes!"
            ]
        }
        
        return random.choice(responses.get(personality, ["Je n'ai rien à dire sur ce sujet."]))