import random
import datetime
from collections import defaultdict

# Personality traits for NPCs
PERSONALITY_TRAITS = [
    "nervous", "confident", "arrogant", "humble", "secretive", 
    "talkative", "quiet", "suspicious", "helpful", "deceptive",
    "short-tempered", "patient", "emotional", "logical", "forgetful"
]

# Occupations for NPCs
OCCUPATIONS = [
    "doctor", "lawyer", "teacher", "chef", "artist", 
    "writer", "engineer", "scientist", "business owner", "accountant",
    "police officer", "librarian", "musician", "gardener", "shop clerk",
    "retired", "student", "private investigator", "journalist", "taxi driver"
]

# Crime types
CRIME_TYPES = [
    "murder", "theft", "blackmail", "kidnapping", "assault",
    "vandalism", "forgery", "fraud", "arson", "burglary"
]

# Locations
LOCATIONS = [
    "mansion", "apartment", "restaurant", "office", "park",
    "museum", "library", "theater", "hotel", "university campus",
    "art gallery", "bank", "shopping mall", "train station", "café"
]

# Time periods
TIME_PERIODS = [
    "early morning", "mid-morning", "noon", "afternoon", "evening",
    "night", "midnight", "dawn", "dusk", "late night"
]

# Motives
MOTIVES = [
    "revenge", "jealousy", "money", "love", "hatred",
    "power", "fear", "blackmail", "accident", "mistaken identity",
    "protecting someone", "covering up another crime", "mental instability"
]

# Relationships
RELATIONSHIPS = [
    "friends", "enemies", "colleagues", "neighbors", "family members",
    "romantic partners", "former partners", "strangers", "business partners",
    "client and service provider", "teacher and student", "distant relatives"
]

# Items that could be evidence
EVIDENCE_ITEMS = [
    "knife", "gun", "poison", "rope", "broken glass",
    "blood stains", "fingerprints", "footprints", "torn piece of clothing", 
    "handwritten note", "photograph", "electronic device", "keys", "wallet", "ID card"
]

def generate_name():
    """Generate a random name for an NPC"""
    first_names = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
        "Emma", "Olivia", "Noah", "Liam", "Jacob", "Mason", "William", "Ethan", "Michael", "Alexander"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
        "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King"
    ]
    
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_time_alibi(crime_time):
    """Generate a time alibi that may or may not overlap with the crime time"""
    time_periods = ["early morning", "mid-morning", "noon", "afternoon", "evening", "night", "midnight"]
    crime_index = time_periods.index(crime_time) if crime_time in time_periods else random.randint(0, len(time_periods)-1)
    
    # For guilty person: create an alibi that's close to but not at crime time
    if random.random() < 0.7:  # 70% chance to have a gap or suspicious alibi
        if crime_index > 0:
            return time_periods[crime_index - 1]
        else:
            return time_periods[crime_index + 1]
    else:  # Sometimes create a directly conflicting alibi (they say they were there)
        return crime_time

def generate_location_alibi(crime_location):
    """Generate a location alibi that may or may not be near the crime scene"""
    if random.random() < 0.3:  # 30% chance to be at a nearby location
        nearby_locations = [loc for loc in LOCATIONS if loc != crime_location]
        return random.choice(nearby_locations[:3])
    else:
        return random.choice(LOCATIONS)

def generate_statement(person, is_culprit, crime, all_suspects):
    """Generate a statement for a suspect that may include lies if they are the culprit"""
    other_suspects = [s for s in all_suspects if s['name'] != person['name']]
    
    # Basic truthful elements that everyone knows
    statement = {
        "knew_victim": random.random() < 0.7,
        "saw_other_suspects": {},
        "heard_or_saw": [],
        "alibi_time": "",
        "alibi_location": "",
        "alibi_witness": None
    }
    
    # Generate relationships and observations about other suspects
    for suspect in other_suspects:
        # Whether this person saw another suspect
        if random.random() < 0.6:
            statement["saw_other_suspects"][suspect["name"]] = {
                "time": random.choice(TIME_PERIODS),
                "location": random.choice(LOCATIONS),
                "details": f"Seemed {random.choice(PERSONALITY_TRAITS)}."
            }
    
    # Generate random observations/clues
    num_observations = random.randint(1, 3)
    for _ in range(num_observations):
        observation = {
            "type": random.choice(["saw", "heard", "found"]),
            "details": ""
        }
        
        if observation["type"] == "saw":
            if random.random() < 0.7:
                # Saw a person
                if other_suspects:
                    suspect = random.choice(other_suspects)
                    observation["details"] = f"{suspect['name']} at {random.choice(LOCATIONS)} during {random.choice(TIME_PERIODS)}"
                else:
                    observation["details"] = f"someone suspicious near {crime['location']}"
            else:
                # Saw an object
                observation["details"] = f"a {random.choice(EVIDENCE_ITEMS)} at {random.choice(LOCATIONS)}"
        
        elif observation["type"] == "heard":
            if random.random() < 0.5:
                # Heard a conversation
                if other_suspects and len(other_suspects) >= 2:
                    s1, s2 = random.sample(other_suspects, 2)
                    observation["details"] = f"{s1['name']} arguing with {s2['name']} about {random.choice(['money', 'jealousy', 'secrets', 'threats', 'the victim'])}"
                else:
                    observation["details"] = f"an argument near {crime['location']}"
            else:
                # Heard a sound
                observation["details"] = f"a {random.choice(['scream', 'gunshot', 'breaking glass', 'loud thud', 'door slam'])}"
        
        else:  # "found"
            observation["details"] = f"a {random.choice(EVIDENCE_ITEMS)} near {random.choice(LOCATIONS)}"
        
        statement["heard_or_saw"].append(observation)
    
    # Generate alibi
    if is_culprit:
        # The culprit will lie about their whereabouts
        statement["alibi_time"] = generate_time_alibi(crime["time"])
        statement["alibi_location"] = generate_location_alibi(crime["location"])
        
        # Decide whether they have a fake witness
        if random.random() < 0.4:  # 40% chance to claim a witness
            statement["alibi_witness"] = generate_name()
    else:
        # Innocent people generally tell the truth, but might not have perfect alibis
        statement["alibi_time"] = random.choice(TIME_PERIODS)
        statement["alibi_location"] = random.choice(LOCATIONS)
        
        # Decide whether they have a witness
        if random.random() < 0.75:  # 75% chance to have a witness
            statement["alibi_witness"] = generate_name()
    
    # Generate motive information (true for culprit, may be misleading for others)
    if is_culprit:
        statement["attitude_to_victim"] = "neutral"  # They'll lie about their feelings
    else:
        attitudes = ["positive", "neutral", "negative", "complicated"]
        statement["attitude_to_victim"] = random.choice(attitudes)
    
    return statement

def generate_dialogue_style(personality):
    """Generate dialogue style based on personality traits"""
    style = {
        "verbose": False,
        "formal": False,
        "uses_slang": False,
        "interrupts": False,
        "hesitant": False,
        "detailed": False
    }
    
    if "talkative" in personality:
        style["verbose"] = True
    
    if "arrogant" in personality:
        style["formal"] = True
    
    if any(trait in personality for trait in ["artist", "musician", "student"]):
        style["uses_slang"] = True
    
    if "short-tempered" in personality:
        style["interrupts"] = True
    
    if "nervous" in personality:
        style["hesitant"] = True
    
    if "logical" in personality:
        style["detailed"] = True
    
    return style

def create_contradictions(culprit, statements, crime):
    """Create deliberate contradictions in the culprit's statement"""
    # Find statements from other suspects that contradict the culprit
    contradictions = []
    
    culprit_statement = statements[culprit["name"]]
    
    # Create alibi contradictions
    for suspect_name, statement in statements.items():
        if suspect_name == culprit["name"]:
            continue
            
        # Check if anyone saw the culprit somewhere else during their claimed alibi
        if culprit["name"] in statement["saw_other_suspects"]:
            observation = statement["saw_other_suspects"][culprit["name"]]
            if observation["time"] == culprit_statement["alibi_time"] and observation["location"] != culprit_statement["alibi_location"]:
                contradictions.append({
                    "type": "location_contradiction",
                    "details": f"{suspect_name} claims to have seen {culprit['name']} at {observation['location']} during {observation['time']}, but {culprit['name']} claims to have been at {culprit_statement['alibi_location']}"
                })
    
    # Create evidence contradictions
    for suspect_name, statement in statements.items():
        if suspect_name == culprit["name"]:
            continue
            
        # Check if someone found evidence that contradicts the culprit
        for observation in statement["heard_or_saw"]:
            if "culprit" in observation["details"].lower() or culprit["name"] in observation["details"]:
                contradictions.append({
                    "type": "evidence_contradiction",
                    "details": f"{suspect_name} {observation['type']} {observation['details']}, which contradicts {culprit['name']}'s alibi"
                })
    
    # If we don't have enough natural contradictions, create some
    if len(contradictions) < 2:
        # Pick a random suspect to have seen the culprit near the crime scene
        other_suspects = [name for name in statements.keys() if name != culprit["name"]]
        if other_suspects:
            witness = random.choice(other_suspects)
            
            # Add a new observation to the witness's statement
            statements[witness]["heard_or_saw"].append({
                "type": "saw",
                "details": f"{culprit['name']} near {crime['location']} around {crime['time']}"
            })
            
            contradictions.append({
                "type": "witness_contradiction",
                "details": f"{witness} saw {culprit['name']} near the crime scene, contradicting their alibi"
            })
    
    return contradictions

def generate_case():
    """Generate a complete mystery case"""
    # Create basic crime details
    crime = {
        "crime_type": random.choice(CRIME_TYPES),
        "victim": generate_name(),
        "location": random.choice(LOCATIONS),
        "time": random.choice(TIME_PERIODS),
        "evidence": [random.choice(EVIDENCE_ITEMS) for _ in range(random.randint(2, 4))]
    }
    
    # Create suspects (3-4 suspects)
    num_suspects = random.randint(3, 4)
    suspects = []
    
    for _ in range(num_suspects):
        suspect = {
            "name": generate_name(),
            "occupation": random.choice(OCCUPATIONS),
            "personality": random.sample(PERSONALITY_TRAITS, random.randint(2, 3)),
            "relationship_to_victim": random.choice(RELATIONSHIPS)
        }
        suspects.append(suspect)
    
    # Choose a culprit
    culprit = random.choice(suspects)
    culprit["motive"] = random.choice(MOTIVES)
    
    # Generate statements for each suspect
    statements = {}
    for suspect in suspects:
        is_culprit = suspect["name"] == culprit["name"]
        statements[suspect["name"]] = generate_statement(suspect, is_culprit, crime, suspects)
    
    # Create dialogue styles for each suspect
    dialogue_styles = {}
    for suspect in suspects:
        dialogue_styles[suspect["name"]] = generate_dialogue_style(suspect["personality"])
    
    # Create deliberate contradictions for the culprit
    contradictions = create_contradictions(culprit, statements, crime)
    
    # Compile the full case
    case = {
        "crime": crime,
        "suspects": suspects,
        "culprit": culprit,
        "statements": statements,
        "dialogue_styles": dialogue_styles,
        "contradictions": contradictions
    }
    
    return case

if __name__ == "__main__":
    # Generate and print a sample case
    case = generate_case()
    print("=== MYSTERY CASE ===")
    print(f"Crime: {case['crime']['crime_type']}")
    print(f"Victim: {case['crime']['victim']}")
    print(f"Location: {case['crime']['location']}")
    print(f"Time: {case['crime']['time']}")
    print(f"Culprit: {case['culprit']['name']} (Motive: {case['culprit']['motive']})")
    print("\n=== SUSPECTS ===")
    for suspect in case['suspects']:
        print(f"- {suspect['name']}, {suspect['occupation']}")
    
    print("\n=== CONTRADICTIONS ===")
    for c in case['contradictions']:
        print(f"- {c['details']}")