import random
import re
import string
import json
import os
import math
from collections import defaultdict, Counter

# NLP utilities for the detective
class SimpleNLP:
    def __init__(self):
        self.stopwords = set([
            "a", "an", "the", "this", "that", "these", "those",
            "is", "am", "are", "was", "were", "be", "been", "being",
            "and", "or", "but", "if", "then", "else", "when", "where", "why",
            "how", "all", "any", "both", "each", "few", "more", "most", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "can", "will", "just", "should", "now"
        ])
        
        # Load sentiment words if available
        self.positive_words = set(["good", "great", "excellent", "positive", "helpful", "nice", "kind", "honest", "trustworthy"])
        self.negative_words = set(["bad", "terrible", "awful", "negative", "unhelpful", "mean", "cruel", "dishonest", "suspicious", "nervous", "liar"])
        
        # Load previously saved case histories for training
        self.case_history = self._load_case_history()
        
    def _load_case_history(self):
        """Load previous case histories for learning"""
        history = []
        if os.path.exists("case_history"):
            for filename in os.listdir("case_history"):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join("case_history", filename), 'r') as f:
                            case_data = json.load(f)
                            history.append(case_data)
                    except:
                        pass
        return history
    
    def analyze_sentiment(self, text):
        """A simple sentiment analysis function"""
        text = text.lower()
        words = self._tokenize(text)
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        if positive_count > negative_count:
            return "positive", positive_count / (positive_count + negative_count + 1e-10)
        elif negative_count > positive_count:
            return "negative", negative_count / (positive_count + negative_count + 1e-10)
        else:
            return "neutral", 0.5
    
    def get_key_entities(self, text):
        """Extract potentially important entities from text"""
        # Very simple entity extraction - look for capitalized words or 
        # words that might be suspicious items, locations, etc.
        important_categories = [
            "knife", "gun", "weapon", "blood", "money", "wallet", "jewelry", 
            "door", "window", "car", "phone", "computer", "note", "letter",
            "home", "house", "apartment", "office", "park", "restaurant", "hotel",
            "angry", "fight", "argument", "scream", "yell", "threat", "kill", "murder",
            "steal", "robbery", "theft"
        ]
        
        words = self._tokenize(text)
        entities = []
        
        for word in words:
            # Check if it's capitalized (might be a name)
            if word and word[0].isupper():
                entities.append(word)
            
            # Check if it's a potentially important word
            if word.lower() in important_categories:
                entities.append(word)
        
        return list(set(entities))
    
    def find_contradictions(self, statements):
        """Find contradictions between different statements"""
        contradictions = []
        
        # Extract time and location information from each statement
        person_locations = {}
        
        # Process each person's statement
        for person, statement in statements.items():
            # Record their claimed alibi
            person_locations[person] = {
                "self_reported": {
                    "time": statement["alibi_time"],
                    "location": statement["alibi_location"]
                },
                "observed_by_others": []
            }
            
            # Record where this person claimed to see others
            for other_person, observation in statement["saw_other_suspects"].items():
                if other_person not in person_locations:
                    person_locations[other_person] = {"self_reported": {}, "observed_by_others": []}
                
                person_locations[other_person]["observed_by_others"].append({
                    "observer": person,
                    "time": observation["time"],
                    "location": observation["location"]
                })
        
        # Check for direct contradictions
        for person, locations in person_locations.items():
            if not locations["self_reported"]:
                continue
                
            self_time = locations["self_reported"]["time"]
            self_location = locations["self_reported"]["location"]
            
            for observation in locations["observed_by_others"]:
                obs_time = observation["time"]
                obs_location = observation["location"]
                observer = observation["observer"]
                
                # If times match but locations differ
                if self_time == obs_time and self_location != obs_location:
                    contradictions.append({
                        "type": "location_contradiction",
                        "subject": person,
                        "reporter": observer,
                        "details": f"{person} claims to be at {self_location} during {self_time}, but {observer} says they were at {obs_location}"
                    })
        
        return contradictions
    
    def extract_key_facts(self, statement):
        """Extract key facts from a statement"""
        facts = []
        
        # Extract alibi information
        if statement["alibi_time"] and statement["alibi_location"]:
            facts.append(f"Was at {statement['alibi_location']} during {statement['alibi_time']}")
            
            if statement["alibi_witness"]:
                facts.append(f"Alibi witness: {statement['alibi_witness']}")
        
        # Extract information about other suspects
        for other, observation in statement["saw_other_suspects"].items():
            facts.append(f"Saw {other} at {observation['location']} during {observation['time']}")
            if observation["details"]:
                facts.append(f"Observed that {other} {observation['details']}")
        
        # Extract what they heard or saw
        for observation in statement["heard_or_saw"]:
            facts.append(f"{observation['type'].capitalize()} {observation['details']}")
        
        # Extract relationship to victim
        if "attitude_to_victim" in statement:
            facts.append(f"Attitude toward victim: {statement['attitude_to_victim']}")
        
        return facts
    
    def _tokenize(self, text):
        """Simple tokenization function"""
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words and remove stopwords
        words = [word for word in text.split() if word not in self.stopwords]
        return words
    
    def calculate_suspicion_score(self, suspect_name, case_data, contradictions):
        """Calculate a suspicion score for a suspect based on contradictions and patterns"""
        score = 0
        
        # Add points for direct contradictions
        for contradiction in contradictions:
            if contradiction["subject"] == suspect_name:
                score += 3
        
        # Add points for lacking an alibi witness
        if not case_data["statements"][suspect_name]["alibi_witness"]:
            score += 1
        
        # Add points for being near the crime scene
        if case_data["statements"][suspect_name]["alibi_location"] == case_data["crime"]["location"]:
            score += 2
        
        # Add points for being at the crime time
        if case_data["statements"][suspect_name]["alibi_time"] == case_data["crime"]["time"]:
            score += 2
        
        # Check case history for similar patterns if we have previous cases
        for past_case in self.case_history:
            if past_case["correct"]:  # Only learn from correct past cases
                culprit = past_case["case"]["culprit"]["name"]
                culprit_statement = past_case["case"]["statements"][culprit]
                suspect_statement = case_data["statements"][suspect_name]
                
                # Check for similar alibi patterns
                if culprit_statement["alibi_witness"] == suspect_statement["alibi_witness"]:
                    score += 0.5
                
                if culprit_statement["alibi_time"] == suspect_statement["alibi_time"]:
                    score += 0.3
        
        return score

class DetectiveAgent:
    def __init__(self):
        self.nlp = SimpleNLP()
        self.current_case = None
        self.interrogation_log = {}
        self.deduction_log = []
        self.suspicion_scores = {}
    
    def investigate(self, case_data):
        """Main investigation function"""
        self.current_case = case_data
        self.interrogation_log = {}
        self.deduction_log = []
        
        print("Detective beginning investigation...")
        
        # First, gather basic case information
        self._analyze_crime_scene()
        
        # Interrogate each suspect
        for suspect in case_data["suspects"]:
            print(f"\nInterrogating {suspect['name']}...")
            self._interrogate_suspect(suspect)
        
        # Analyze statements for contradictions
        contradictions = self._analyze_statements()
        
        # Calculate suspicion scores
        self._calculate_suspicion()
        
        # Make final deduction
        culprit, confidence = self._make_deduction()
        
        print(f"\nDetective's conclusion: {culprit} committed the crime (confidence: {confidence:.2f})")
        
        # Compile reasoning and return result
        reasoning = {
            "interrogation_log": self.interrogation_log,
            "deduction_log": self.deduction_log,
            "suspicion_scores": self.suspicion_scores,
            "contradictions": contradictions,
            "confidence": confidence
        }
        
        return culprit, reasoning
    
    def _analyze_crime_scene(self):
        """Analyze the crime scene"""
        crime = self.current_case["crime"]
        
        self.deduction_log.append(f"Crime: {crime['crime_type']} at {crime['location']} during {crime['time']}")
        self.deduction_log.append(f"Victim: {crime['victim']}")
        self.deduction_log.append(f"Evidence found: {', '.join(crime['evidence'])}")
    
    def _interrogate_suspect(self, suspect):
        """Conduct an interrogation with a suspect"""
        suspect_name = suspect["name"]
        statement = self.current_case["statements"][suspect_name]
        dialogue_style = self.current_case["dialogue_styles"][suspect_name]
        
        # Initialize interrogation log
        self.interrogation_log[suspect_name] = {
            "questions": [],
            "answers": [],
            "observations": [],
            "key_facts": []
        }
        
        # First question - basic alibi
        self._ask_question(suspect_name, "Where were you at the time of the incident?")
        self._record_answer(suspect_name, 
                           f"I was at {statement['alibi_location']} during {statement['alibi_time']}." + 
                           (f" {statement['alibi_witness']} can confirm this." if statement['alibi_witness'] else ""))
        
        # Record observation about their demeanor
        if "nervous" in suspect["personality"]:
            self._record_observation(suspect_name, "Suspect appears nervous during questioning")
        elif "confident" in suspect["personality"]:
            self._record_observation(suspect_name, "Suspect appears very confident and composed")
        
        # Ask about the victim
        self._ask_question(suspect_name, "What was your relationship with the victim?")
        
        victim_response = f"My relationship with the victim was {statement['attitude_to_victim']}."
        if statement["knew_victim"]:
            victim_response += " I knew them as " + suspect["relationship_to_victim"] + "."
        else:
            victim_response += " I barely knew them."
        
        self._record_answer(suspect_name, victim_response)
        
        # Ask about other suspects they might have seen
        if statement["saw_other_suspects"]:
            other_names = list(statement["saw_other_suspects"].keys())
            self._ask_question(suspect_name, f"Did you see any of the other suspects around the time of the incident?")
            
            answer = "Yes, I did. "
            for other in other_names:
                obs = statement["saw_other_suspects"][other]
                answer += f"I saw {other} at {obs['location']} during {obs['time']}. {obs['details']} "
            
            self._record_answer(suspect_name, answer)
        else:
            self._ask_question(suspect_name, "Did you see anyone suspicious around the time of the incident?")
            self._record_answer(suspect_name, "No, I didn't see anyone suspicious.")
        
        # Ask about what they heard or saw
        if statement["heard_or_saw"]:
            self._ask_question(suspect_name, "Did you notice anything unusual that day?")
            
            answer = "Actually, yes. "
            for obs in statement["heard_or_saw"]:
                answer += f"I {obs['type']} {obs['details']}. "
            
            self._record_answer(suspect_name, answer)
        
        # Extract key facts from their statements
        key_facts = self.nlp.extract_key_facts(statement)
        for fact in key_facts:
            self.interrogation_log[suspect_name]["key_facts"].append(fact)
    
    def _ask_question(self, suspect_name, question):
        """Ask a question to a suspect"""
        self.interrogation_log[suspect_name]["questions"].append(question)
    
    def _record_answer(self, suspect_name, answer):
        """Record a suspect's answer"""
        self.interrogation_log[suspect_name]["answers"].append(answer)
        
        # Also analyze sentiment and key entities in the answer
        sentiment, confidence = self.nlp.analyze_sentiment(answer)
        if sentiment != "neutral" and confidence > 0.7:
            self._record_observation(suspect_name, f"Suspect's response seemed {sentiment} (confidence: {confidence:.2f})")
        
        entities = self.nlp.get_key_entities(answer)
        if entities:
            self._record_observation(suspect_name, f"Key entities mentioned: {', '.join(entities)}")
    
    def _record_observation(self, suspect_name, observation):
        """Record an observation about a suspect"""
        self.interrogation_log[suspect_name]["observations"].append(observation)
    
    def _analyze_statements(self):
        """Analyze all statements for contradictions and inconsistencies"""
        print("\nAnalyzing statements for contradictions...")
        contradictions = self.nlp.find_contradictions(self.current_case["statements"])
        
        # Log all contradictions found
        for c in contradictions:
            self.deduction_log.append(f"Contradiction found: {c['details']}")
            print(f"  - {c['details']}")
        
        return contradictions
    
    def _calculate_suspicion(self):
        """Calculate suspicion scores for each suspect"""
        print("\nCalculating suspicion scores...")
        
        contradictions = self.nlp.find_contradictions(self.current_case["statements"])
        
        for suspect in self.current_case["suspects"]:
            name = suspect["name"]
            score = self.nlp.calculate_suspicion_score(name, self.current_case, contradictions)
            
            # Additional factors:
            # 1. Suspicious behavior during interrogation
            for observation in self.interrogation_log[name]["observations"]:
                if "nervous" in observation.lower() or "suspicious" in observation.lower():
                    score += 1
                if "confident" in observation.lower() and "too confident" not in observation.lower():
                    score -= 0.5
            
            # 2. Relationship with victim
            statement = self.current_case["statements"][name]
            if statement["attitude_to_victim"] == "negative":
                score += 1
            elif statement["attitude_to_victim"] == "positive":
                score -= 0.5
            
            # 3. Consistency with evidence found
            for observation in statement["heard_or_saw"]:
                for evidence in self.current_case["crime"]["evidence"]:
                    if evidence.lower() in observation["details"].lower():
                        score += 0.5
            
            # Store the final suspicion score
            self.suspicion_scores[name] = score
            print(f"  - {name}: {score:.2f}")
            self.deduction_log.append(f"Suspicion score for {name}: {score:.2f}")
    
    def _make_deduction(self):
        """Make a final deduction about who the culprit is"""
        print("\nMaking final deduction...")
        
        # Find the suspect with the highest suspicion score
        culprit = max(self.suspicion_scores.items(), key=lambda x: x[1])
        culprit_name = culprit[0]
        highest_score = culprit[1]
        
        # Calculate confidence based on difference between highest and second highest score
        scores = sorted(self.suspicion_scores.values(), reverse=True)
        if len(scores) > 1:
            score_diff = scores[0] - scores[1]
            confidence = min(1.0, max(0.5, 0.5 + score_diff / 5.0))
        else:
            confidence = 0.5
        
        # Record reasoning
        reasons = []
        
        # 1. Contradictions
        contradictions = self.nlp.find_contradictions(self.current_case["statements"])
        culprit_contradictions = [c for c in contradictions if c["subject"] == culprit_name]
        if culprit_contradictions:
            reason = f"{culprit_name}'s statement contradicts others: "
            reason += ", ".join([c["details"] for c in culprit_contradictions[:2]])
            reasons.append(reason)
        
        # 2. Alibi issues
        statement = self.current_case["statements"][culprit_name]
        if not statement["alibi_witness"]:
            reasons.append(f"{culprit_name} has no alibi witness")
        
        if statement["alibi_time"] == self.current_case["crime"]["time"] and statement["alibi_location"] != self.current_case["crime"]["location"]:
            reasons.append(f"{culprit_name} claims to be away from the crime scene, but evidence suggests otherwise")
        
        # 3. Suspicious behavior
        for observation in self.interrogation_log[culprit_name]["observations"]:
            if "nervous" in observation.lower() or "suspicious" in observation.lower():
                reasons.append(f"{culprit_name} showed suspicious behavior: {observation}")
                break
        
        # Log the reasoning
        self.deduction_log.append(f"Deduction: {culprit_name} is the culprit (confidence: {confidence:.2f})")
        for reason in reasons:
            self.deduction_log.append(f"Reason: {reason}")
        
        return culprit_name, confidence

def investigate(case_data):
    """Main function to investigate a case"""
    detective = DetectiveAgent()
    return detective.investigate(case_data)

if __name__ == "__main__":
    # Test with a sample case
    import create_plot
    case_data = create_plot.generate_case()
    culprit, reasoning = investigate(case_data)
    
    print("\n--- INVESTIGATION RESULTS ---")
    print(f"Detective's conclusion: The culprit is {culprit}")
    print(f"Actual culprit: {case_data['culprit']['name']}")
    
    if culprit == case_data['culprit']['name']:
        print("Detective was CORRECT!")
    else:
        print("Detective was WRONG!")