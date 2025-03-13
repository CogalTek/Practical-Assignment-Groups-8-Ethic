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
    
    def find_contradictions(self, statements, interrogation_log=None):
        """Find contradictions between different statements with improved detection"""
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
        
        # Check for contradictions in alibis
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
        
        # Check for contradictions in observations
        # This looks for cases where two people claim to have seen a third person at different places at the same time
        for person in person_locations:
            observers = defaultdict(list)  # Time -> list of (observer, location)
            
            # Collect all observations for this person
            for other_person, statement in statements.items():
                if person in statement["saw_other_suspects"]:
                    obs = statement["saw_other_suspects"][person]
                    observers[obs["time"]].append((other_person, obs["location"]))
            
            # Check if anyone reported conflicting locations for the same time
            for time, observations in observers.items():
                if len(observations) >= 2:
                    # Check for contradictions
                    locations = [obs[1] for obs in observations]
                    if len(set(locations)) > 1:  # Different locations reported
                        details = f"Conflicting reports for {person} at {time}: "
                        for observer, location in observations:
                            details += f"{observer} saw them at {location}; "
                        
                        contradictions.append({
                            "type": "multiple_witness_contradiction",
                            "subject": person,
                            "time": time,
                            "details": details.strip("; ")
                        })
        
        # Check for contradictions with crime scene evidence
        if interrogation_log:
            for person, log in interrogation_log.items():
                for i, question in enumerate(log["questions"]):
                    if i < len(log["answers"]) and "evidence" in question.lower():
                        # Check if they denied knowledge but someone else saw them with the evidence
                        answer = log["answers"][i]
                        if "no" in answer.lower() or "don't know" in answer.lower() or "haven't seen" in answer.lower():
                            evidence_item = question.split("about a ")[1].split(" related")[0] if "about a " in question else ""
                            
                            # Check if someone else saw them with this evidence
                            for other_person, other_statement in statements.items():
                                if other_person == person:
                                    continue
                                    
                                for obs in other_statement["heard_or_saw"]:
                                    if evidence_item.lower() in obs["details"].lower() and person.lower() in obs["details"].lower():
                                        contradictions.append({
                                            "type": "evidence_contradiction",
                                            "subject": person,
                                            "reporter": other_person,
                                            "details": f"{person} denied knowledge of the {evidence_item}, but {other_person} {obs['type']} them with it: {obs['details']}"
                                        })
        
        # Also include observations from interrogations that were marked as contradictions
        if interrogation_log:
            for person, log in interrogation_log.items():
                for observation in log["observations"]:
                    if "contradiction" in observation.lower():
                        contradictions.append({
                            "type": "interrogation_contradiction",
                            "subject": person,
                            "details": observation
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
        """Conduct an enhanced interrogation with a suspect"""
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
        
        # Première phase: questions de base
        # 1. Question sur l'alibi
        self._ask_question(suspect_name, "Where were you at the time of the incident?")
        self._record_answer(suspect_name, 
                           f"I was at {statement['alibi_location']} during {statement['alibi_time']}." + 
                           (f" {statement['alibi_witness']} can confirm this." if statement['alibi_witness'] else ""))
        
        # Enregistrer l'observation sur leur comportement
        if "nervous" in suspect["personality"]:
            self._record_observation(suspect_name, "Suspect appears nervous during questioning")
        elif "confident" in suspect["personality"]:
            self._record_observation(suspect_name, "Suspect appears very confident and composed")
        
        # 2. Question sur la relation avec la victime
        self._ask_question(suspect_name, "What was your relationship with the victim?")
        
        victim_response = f"My relationship with the victim was {statement['attitude_to_victim']}."
        if statement["knew_victim"]:
            victim_response += f" I knew them as {suspect['relationship_to_victim']}."
        else:
            victim_response += " I barely knew them."
        
        self._record_answer(suspect_name, victim_response)
        
        # 3. Questions générales sur les autres suspects
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
        
        # 4. Questions sur ce qu'ils ont vu ou entendu
        if statement["heard_or_saw"]:
            self._ask_question(suspect_name, "Did you notice anything unusual that day?")
            
            answer = "Actually, yes. "
            for obs in statement["heard_or_saw"]:
                answer += f"I {obs['type']} {obs['details']}. "
            
            self._record_answer(suspect_name, answer)
        
        # Deuxième phase: questions plus ciblées sur les autres suspects
        # Si nous avons déjà interrogé d'autres suspects, posons des questions sur leurs alibis
        for other_suspect in self.current_case["suspects"]:
            other_name = other_suspect["name"]
            
            # Ne pas poser de questions sur eux-mêmes
            if other_name == suspect_name:
                continue
                
            # Vérifier si nous avons déjà interrogé cet autre suspect
            if other_name in self.interrogation_log:
                other_statement = self.current_case["statements"][other_name]
                
                # Question spécifique sur l'alibi de l'autre suspect
                self._ask_question(suspect_name, 
                                  f"Did you happen to see {other_name} at {other_statement['alibi_location']} during {other_statement['alibi_time']}?")
                
                # Génération de la réponse en fonction de ce qu'ils ont déclaré voir
                if other_name in statement["saw_other_suspects"]:
                    obs = statement["saw_other_suspects"][other_name]
                    if obs["time"] == other_statement["alibi_time"] and obs["location"] == other_statement["alibi_location"]:
                        answer = f"Yes, I did see {other_name} there at that time."
                    else:
                        answer = f"No, I didn't see {other_name} there. "
                        answer += f"I saw them at {obs['location']} during {obs['time']} instead."
                        
                        # Marquer cette incohérence dans le journal d'observation
                        self._record_observation(suspect_name, 
                                               f"Contradicts {other_name}'s alibi claiming to be at {other_statement['alibi_location']} during {other_statement['alibi_time']}")
                else:
                    # Générer aléatoirement une réponse s'ils n'ont pas mentionné cette personne avant
                    if random.random() < 0.3:  # 30% de chance de créer un nouveau témoignage
                        saw_location = other_statement["alibi_location"] if random.random() < 0.7 else random.choice(
                            [loc for loc in self.current_case["crime"]["location"] if loc != other_statement["alibi_location"]])
                        
                        answer = f"Actually, now that you mention it, I think I did see {other_name} at {saw_location} around that time."
                        
                        # Ajouter cette nouvelle observation à leur déclaration
                        statement["saw_other_suspects"][other_name] = {
                            "time": other_statement["alibi_time"],
                            "location": saw_location,
                            "details": f"Just briefly saw them there."
                        }
                        
                        # Vérifier s'il y a une contradiction
                        if saw_location != other_statement["alibi_location"]:
                            self._record_observation(suspect_name, 
                                                   f"New contradiction: claims to have seen {other_name} at {saw_location}, not at their claimed alibi location {other_statement['alibi_location']}")
                    else:
                        answer = f"No, I don't recall seeing {other_name} there at that time."
                
                self._record_answer(suspect_name, answer)
        
        # Troisième phase: questions sur des éléments spécifiques de la scène de crime
        # Question sur des preuves spécifiques
        for evidence in self.current_case["crime"]["evidence"]:
            self._ask_question(suspect_name, f"Do you know anything about a {evidence} related to this case?")
            
            # Vérifier si l'une de leurs observations mentionne cette preuve
            evidence_mentioned = False
            for obs in statement["heard_or_saw"]:
                if evidence.lower() in obs["details"].lower():
                    self._record_answer(suspect_name, f"Yes, I {obs['type']} {obs['details']}.")
                    evidence_mentioned = True
                    break
            
            if not evidence_mentioned:
                # S'ils sont le coupable, ils pourraient être nerveux en parlant de preuves
                if suspect_name == self.current_case["culprit"]["name"] and random.random() < 0.7:
                    self._record_answer(suspect_name, f"No, I know nothing about any {evidence}.")
                    self._record_observation(suspect_name, f"Seemed uncomfortable when asked about the {evidence}")
                else:
                    self._record_answer(suspect_name, f"No, I haven't seen or heard anything about a {evidence}.")
        
        # Question finale sur leur théorie du crime
        self._ask_question(suspect_name, "Do you have any theory about who might be responsible for this incident?")
        
        # Si c'est le coupable, ils accuseront quelqu'un d'autre
        if suspect_name == self.current_case["culprit"]["name"]:
            other_suspects = [s["name"] for s in self.current_case["suspects"] if s["name"] != suspect_name]
            accused = random.choice(other_suspects) if other_suspects else "someone else"
            
            theory = f"I think {accused} might be involved. "
            # Ajouter une fausse raison
            theories = [
                f"They seemed very suspicious that day.",
                f"I heard they had a grudge against the victim.",
                f"They were seen near the crime scene.",
                f"Someone told me they've been acting strange lately."
            ]
            theory += random.choice(theories)
            
            self._record_answer(suspect_name, theory)
            self._record_observation(suspect_name, "Quickly deflected blame to another person")
        else:
            # S'ils ne sont pas coupables, réponses variées
            theories = [
                "I really don't know who could have done this.",
                "I have no idea, everyone seemed normal to me that day.",
                "I'm not sure, but something strange was definitely going on.",
                "I'd rather not speculate without evidence."
            ]
            self._record_answer(suspect_name, random.choice(theories))
        
        # Extraire les faits clés de leurs déclarations
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
        contradictions = self.nlp.find_contradictions(self.current_case["statements"], self.interrogation_log)
        
        # Log all contradictions found
        for c in contradictions:
            self.deduction_log.append(f"Contradiction found: {c['details']}")
            print(f"  - {c['details']}")
        
        return contradictions
    
    def _calculate_suspicion(self):
        """Calculate improved suspicion scores for each suspect"""
        print("\nCalculating suspicion scores...")
        
        contradictions = self.nlp.find_contradictions(self.current_case["statements"], self.interrogation_log)
        
        for suspect in self.current_case["suspects"]:
            name = suspect["name"]
            score = 0  # Commencer à zéro et accumuler des preuves
            
            # 1. Nombre de contradictions directes
            suspect_contradictions = [c for c in contradictions if c["subject"] == name]
            contradiction_count = len(suspect_contradictions)
            score += contradiction_count * 2  # Chaque contradiction compte double
            
            if contradiction_count > 0:
                self.deduction_log.append(f"{name} has {contradiction_count} contradictions in their statements")
                print(f"  - {name} has {contradiction_count} contradictions")
            
            # 2. Facteurs liés à l'alibi
            statement = self.current_case["statements"][name]
            
            # Absence de témoin pour l'alibi
            if not statement["alibi_witness"]:
                score += 1.5
                self.deduction_log.append(f"{name} has no alibi witness")
            
            # Proximité avec le lieu du crime
            # Plus de points si l'alibi est près du lieu du crime ou à l'heure du crime
            if statement["alibi_location"] == self.current_case["crime"]["location"]:
                score += 2
                self.deduction_log.append(f"{name} was near the crime scene")
            
            if statement["alibi_time"] == self.current_case["crime"]["time"]:
                score += 1.5
                self.deduction_log.append(f"{name} was present during the time of the crime")
            
            # 3. Comportement suspect pendant l'interrogatoire
            suspicious_behavior = False
            defensive_behavior = False
            
            for observation in self.interrogation_log[name]["observations"]:
                if any(word in observation.lower() for word in ["nervous", "uncomfortable", "hesitant", "suspicious"]):
                    suspicious_behavior = True
                    score += 1.5
                
                if any(word in observation.lower() for word in ["deflected", "blame", "accuse", "defensive"]):
                    defensive_behavior = True
                    score += 1.2
            
            if suspicious_behavior:
                self.deduction_log.append(f"{name} showed suspicious behavior during questioning")
            
            if defensive_behavior:
                self.deduction_log.append(f"{name} was defensive or deflected blame")
            
            # 4. Relation avec la victime
            if statement["attitude_to_victim"] == "negative":
                score += 1.5
                self.deduction_log.append(f"{name} had a negative relationship with the victim")
            elif statement["attitude_to_victim"] == "neutral" and statement["knew_victim"]:
                # Parfois les coupables prétendent être neutres pour cacher leurs sentiments
                score += 0.5
            
            # 5. Accusations des autres
            accused_by_others = 0
            for other_suspect in self.current_case["suspects"]:
                other_name = other_suspect["name"]
                if other_name == name:
                    continue
                    
                # Vérifier si d'autres personnes ont accusé ce suspect
                if other_name in self.interrogation_log:
                    for i, question in enumerate(self.interrogation_log[other_name]["questions"]):
                        if "theory" in question.lower() and i < len(self.interrogation_log[other_name]["answers"]):
                            answer = self.interrogation_log[other_name]["answers"][i]
                            if name in answer:
                                accused_by_others += 1
                                self.deduction_log.append(f"{name} was accused by {other_name}")
            
            score += accused_by_others * 0.7  # Chaque accusation ajoute des points
            
            # 6. Connaissances spécifiques sur les preuves
            knows_evidence = False
            for i, question in enumerate(self.interrogation_log[name]["questions"]):
                if "evidence" in question.lower() and i < len(self.interrogation_log[name]["answers"]):
                    answer = self.interrogation_log[name]["answers"][i]
                    if "yes" in answer.lower() and any(evidence.lower() in answer.lower() for evidence in self.current_case["crime"]["evidence"]):
                        knows_evidence = True
                        # C'est suspect s'ils connaissent trop de détails sur les preuves
                        score += 0.8
                        self.deduction_log.append(f"{name} had specific knowledge about evidence")
            
            # 7. Appliquer l'apprentissage des cas précédents
            history_score = 0
            for past_case in self.nlp.case_history:
                if "correct" in past_case and past_case["correct"]:  # Seulement apprendre des cas correctement résolus
                    culprit = past_case["case"]["culprit"]["name"]
                    culprit_statement = past_case["case"]["statements"][culprit]
                    suspect_statement = self.current_case["statements"][name]
                    
                    # Vérifier des modèles d'alibi similaires
                    if not culprit_statement["alibi_witness"] and not suspect_statement["alibi_witness"]:
                        history_score += 0.3
                    
                    # Vérifier des modèles de comportement similaires
                    if culprit_statement["attitude_to_victim"] == suspect_statement["attitude_to_victim"]:
                        history_score += 0.2
            
            score += history_score
            
            # Enregistrer le score final de suspicion
            self.suspicion_scores[name] = score
            print(f"  - {name}: {score:.2f}")
            self.deduction_log.append(f"Final suspicion score for {name}: {score:.2f}")
    
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
        contradictions = self.nlp.find_contradictions(self.current_case["statements"], self.interrogation_log)
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
        
        # 4. Accusation patterns
        if self.suspicion_scores[culprit_name] > 5 and any("deflected blame" in obs for obs in self.interrogation_log[culprit_name]["observations"]):
            reasons.append(f"{culprit_name} deflected blame to others, a common tactic of the guilty")
        
        # 5. Evidence knowledge
        evidence_knowledge = False
        for i, question in enumerate(self.interrogation_log[culprit_name]["questions"]):
            if "evidence" in question.lower() and i < len(self.interrogation_log[culprit_name]["answers"]):
                answer = self.interrogation_log[culprit_name]["answers"][i]
                if "yes" in answer.lower() and any(ev.lower() in answer.lower() for ev in self.current_case["crime"]["evidence"]):
                    evidence_knowledge = True
                    reasons.append(f"{culprit_name} had suspicious knowledge about crime scene evidence")
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