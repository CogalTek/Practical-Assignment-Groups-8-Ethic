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
        """Load case data from JSON"""
        if isinstance(json_data, str):
            try:
                self.case_data = json.loads(json_data)
            except:
                self.case_data = json_data
        else:
            self.case_data = json_data
            
        self.suspects = self.case_data["case"]["suspects"]
        self.create_suspect_mapping()
        return len(self.suspects)

    def create_suspect_mapping(self):
        """Map suspects to NPCs"""
        npc_ids = ["npc01", "npc02", "npc03", "npc04", "npc05"]
        
        suspects_to_use = self.suspects[:min(len(self.suspects), 5)]
        
        self.suspect_map = {}
        for idx, suspect in enumerate(suspects_to_use):
            self.suspect_map[suspect["name"]] = npc_ids[idx]
            
        self.npc_to_suspect = {npc_id: suspect["name"] for suspect, npc_id in zip(suspects_to_use, npc_ids[:len(suspects_to_use)])}
    
    def get_active_npcs(self):
        """Return list of active NPCs for this case"""
        return list(self.npc_to_suspect.keys())
    
    def get_suspect_guilt(self, npc_id):
        """Determine if an NPC is guilty"""
        if npc_id in self.npc_to_suspect:
            suspect_name = self.npc_to_suspect[npc_id]
            culprit_name = self.case_data["case"]["culprit"]["name"]
            return 1.0 if suspect_name == culprit_name else random.uniform(0.1, 0.5)
        return 0.0

    def get_crime_details(self):
        """Return crime details"""
        crime = self.case_data["case"]["crime"]
        return {
            "type": crime["crime_type"],
            "victim": crime["victim"],
            "location": crime["location"],
            "time": crime["time"]
        }
    
    def get_next_dialogue(self):
        """Get next interrogation dialogue"""
        if not self.interrogation_phase:
            return None, None, None
        
        if self.current_suspect_idx >= len(self.suspects):
            self.interrogation_phase = False
            self.deduction_phase = True
            return None, None, None
        
        suspect = self.suspects[self.current_suspect_idx]
        suspect_name = suspect["name"]
        interrogation = self.case_data["case"]["statements"].get(suspect_name, {})
        
        if not interrogation:
            self.current_suspect_idx += 1
            self.current_question_idx = 0
            return self.get_next_dialogue()
            
        suspect_logs = self.case_data["detective_reasoning"]["interrogation_log"].get(suspect_name, {})
        questions = suspect_logs.get("questions", [])
        answers = suspect_logs.get("answers", [])
        
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
        """Get next deduction statement"""
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
        """Get case conclusion"""
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