import json
import random
import time

class CaseProcessor:
    def __init__(self):
        self.case_data = None
        self.suspects = []
        self.suspect_map = {}  # Maps suspects to NPCs
        self.current_suspect_idx = 0
        self.current_question_idx = 0
        self.interrogation_phase = True
        self.deduction_phase = False
        self.deduction_idx = 0
        self.conclusion_shown = False

    def load_case(self, json_data):
        """Charge les données d'enquête à partir d'un fichier JSON"""
        if isinstance(json_data, str):
            try:
                self.case_data = json.loads(json_data)
            except:
                print("Erreur de parsing JSON, essai avec le contenu brut")
                self.case_data = json_data
        else:
            self.case_data = json_data
            
        self.suspects = self.case_data["case"]["suspects"]
        self.create_suspect_mapping()
        return len(self.suspects)  # Retourne le nombre de suspects

    def create_suspect_mapping(self):
        """Associe chaque suspect à un NPC du jeu"""
        # Nous allons assigner les suspects aux NPCs 01 à 05
        npc_ids = ["npc01", "npc02", "npc03", "npc04", "npc05"]
        
        # Limiter aux 5 premiers suspects si nécessaire
        suspects_to_use = self.suspects[:min(len(self.suspects), 5)]
        
        print(f"Mapping de {len(suspects_to_use)} suspects aux NPCs...")
        
        # Créer le mapping
        self.suspect_map = {}
        for idx, suspect in enumerate(suspects_to_use):
            self.suspect_map[suspect["name"]] = npc_ids[idx]
            print(f"Suspect '{suspect['name']}' assigné à {npc_ids[idx]}, qui est à l'étage {idx+1}")
            
        # Créer aussi un mapping inverse (de NPC à suspect)
        self.npc_to_suspect = {npc_id: suspect["name"] for suspect, npc_id in zip(suspects_to_use, npc_ids[:len(suspects_to_use)])}
    
    def get_active_npcs(self):
        """Retourne la liste des NPCs actifs dans cette enquête"""
        return list(self.npc_to_suspect.keys())
    
    def get_suspect_guilt(self, npc_id):
        """Détermine si un NPC est coupable"""
        if npc_id in self.npc_to_suspect:
            suspect_name = self.npc_to_suspect[npc_id]
            culprit_name = self.case_data["case"]["culprit"]["name"]
            return 1.0 if suspect_name == culprit_name else random.uniform(0.1, 0.5)
        return 0.0

    def get_crime_details(self):
        """Retourne les détails du crime"""
        crime = self.case_data["case"]["crime"]
        return {
            "type": crime["crime_type"],
            "victim": crime["victim"],
            "location": crime["location"],
            "time": crime["time"]
        }
    
    def get_next_dialogue(self):
        """Récupère le prochain dialogue d'interrogation"""
        if not self.interrogation_phase:
            return None, None, None
        
        if self.current_suspect_idx >= len(self.suspects):
            self.interrogation_phase = False
            self.deduction_phase = True
            return None, None, None
        
        suspect = self.suspects[self.current_suspect_idx]
        suspect_name = suspect["name"]
        interrogation = self.case_data["case"]["statements"].get(suspect_name, {})
        
        # S'il n'y a pas d'interrogatoire pour ce suspect, passer au suivant
        if not interrogation:
            self.current_suspect_idx += 1
            self.current_question_idx = 0
            return self.get_next_dialogue()
            
        suspect_logs = self.case_data["detective_reasoning"]["interrogation_log"].get(suspect_name, {})
        questions = suspect_logs.get("questions", [])
        answers = suspect_logs.get("answers", [])
        
        # S'il n'y a plus de questions pour ce suspect
        if self.current_question_idx >= len(questions):
            self.current_suspect_idx += 1
            self.current_question_idx = 0
            return self.get_next_dialogue()
        
        current_question = questions[self.current_question_idx]
        current_answer = answers[self.current_question_idx]
        
        npc_id = self.suspect_map.get(suspect_name)
        self.current_question_idx += 1
        
        return npc_id, current_question, current_answer
    
    def get_next_deduction(self):
        """Récupère le prochain élément de déduction"""
        if not self.deduction_phase:
            return None
            
        deductions = self.case_data["detective_reasoning"]["deduction_log"]
        
        if self.deduction_idx >= len(deductions):
            self.deduction_phase = False
            return None
            
        deduction = deductions[self.deduction_idx]
        self.deduction_idx += 1
        return deduction
    
    def get_conclusion(self):
        """Récupère la conclusion de l'enquête"""
        if self.conclusion_shown:
            return None
            
        culprit = self.case_data["case"]["culprit"]["name"]
        confidence = self.case_data["detective_reasoning"]["confidence"]
        correct = self.case_data["correct"]
        
        self.conclusion_shown = True
        return {
            "culprit": culprit,
            "confidence": confidence,
            "correct": correct
        }