# AI Detective Game

## Project Overview

This project is an interactive detective game that uses AI to investigate cases autonomously. The detective analyzes evidence, interrogates suspects, and makes deductions to solve mysteries. The game features:

- Procedural generation of mystery cases with different types of crimes, locations, and motives
- AI detective that interrogates suspects and analyzes contradictions
- Visual representation of the investigation process in a building with multiple floors
- Autonomous movement of the detective between floors using an elevator
- Interactive dialogue system showing the detective's interrogation process
- Analysis and deduction visualization
- Case conclusion with confidence measurements

## Project Team

- Mathieu Rio
- Arthur Bourdin
- Rémi Maigrot

## Assets

The graphical assets in the Content folder (excluding music) were created by Grainbox:
https://github.com/Grainbox

## Project Structure

The project is organized into several key files:

```
├── main.py                  # Main entry point
├── generate_and_play.py     # Case generation and visualization launcher
├── detective_game.py        # Main game class and visualization
├── case_processor.py        # Handles case data and investigation logic
├── assets.py                # Manages game assets and sprites
├── movement_system.py       # Handles character movement
├── utils.py                 # Utility functions
├── detective.py             # AI detective algorithm
├── create_plot.py           # Mystery case generator
├── content/                 # Game assets (images, sounds)
└── case_history/            # Generated case files
```

## How to Run the Game

### From Existing Case File

To run the game with an existing case file:

```bash
python main.py
```

Or specify a specific case file:

```bash
python main.py path/to/case_file.json
```

### Generate New Case and Play

To generate a new case and then optionally visualize it:

```bash
python generate_and_play.py
```

## Game Controls

| Key       | Function                                      |
|-----------|-----------------------------------------------|
| SPACE     | Manual intervention (advance dialogue/deduction) |
| F         | Toggle fast mode (speeds up simulation)       |
| H         | Show/hide help screen                         |
| ESC       | Exit the game                                 |

## AI Detective System

### Overview of the AI Approach

The detective in this game uses a hybrid AI system combining rule-based reasoning with statistical analysis and behavioral detection. The system is designed to mimic the deductive reasoning of a human detective by analyzing statements, identifying contradictions, evaluating suspect behavior, and weighing evidence.

### Key AI Components

1. **Rule-Based Reasoning**
   
   The core of the detective AI uses rule-based reasoning to identify contradictions and inconsistencies in suspect statements:

   ```python
   def find_contradictions(statements):
       contradictions = []
       # Check alibis against each other
       for name1, statement1 in statements.items():
           for name2, statement2 in statements.items():
               if name1 != name2:
                   # Check if one suspect claims to have seen another at a time/place 
                   # that contradicts their alibi
                   if name2 in statement1.get('saw_other_suspects', {}):
                       sighting = statement1['saw_other_suspects'][name2]
                       if sighting['time'] == statement2['alibi_time'] and \
                          sighting['location'] != statement2['alibi_location']:
                           contradictions.append({
                               'type': 'alibi_contradiction',
                               'details': f"{name1} saw {name2} at {sighting['location']} during {sighting['time']}, " \
                                         f"but {name2} claims to be at {statement2['alibi_location']}"
                           })
       return contradictions
   ```

2. **Suspicion Scoring System**
   
   The AI assigns suspicion scores to each suspect based on various factors:

   ```python
   def calculate_suspicion(suspect, statements, contradictions, evidence):
       score = 0.0
       
       # Contradictions increase suspicion
       for contradiction in contradictions:
           if suspect['name'] in contradiction['details']:
               score += 1.5
       
       # Suspicious behavior during interrogation
       if 'nervous' in suspect.get('personality', []):
           score += 0.8
       if 'deceptive' in suspect.get('personality', []):
           score += 1.2
           
       # Motive increases suspicion
       if 'motive' in suspect:
           score += 1.0
           
       # Connection to evidence
       for item in evidence:
           if item in statements[suspect['name']].get('mentioned_items', []):
               score += 0.7
               
       return score
   ```

3. **Behavioral Analysis**
   
   The AI analyzes suspect behavior during interrogation, looking for signs of nervousness, deception, or evasiveness:

   ```python
   def analyze_behavior(responses, personality):
       behavior_score = 0.0
       
       # Check for hesitation patterns
       hesitation_words = ['um', 'uh', 'well', 'actually', 'you see', 'I think']
       for response in responses:
           for word in hesitation_words:
               if word in response.lower():
                   behavior_score += 0.2
       
       # Check for question evasion
       direct_questions = [q for q in questions if '?' in q]
       direct_answers = [len(r.split()) > 3 for r in responses[:len(direct_questions)]]
       evasion_rate = 1 - (sum(direct_answers) / len(direct_questions))
       behavior_score += evasion_rate * 1.5
       
       # Adjust based on known personality
       if 'nervous' in personality and behavior_score > 1.0:
           behavior_score *= 0.7  # Nervous people may show signs without being guilty
       
       return behavior_score
   ```

4. **Evidence Correlation**
   
   The AI correlates evidence found at the crime scene with suspect statements:

   ```python
   def correlate_evidence(evidence, statements):
       correlation = {}
       
       for suspect_name, statement in statements.items():
           correlation[suspect_name] = 0.0
           
           # Check for knowledge of evidence they shouldn't have
           for item in evidence:
               if item in statement.get('knows_about', []) and not statement.get('has_legitimate_knowledge_of', {}).get(item, False):
                   correlation[suspect_name] += 1.2
                   
           # Check for evidence mentioned in statements
           for observation in statement.get('heard_or_saw', []):
               if observation['details'] in evidence:
                   correlation[suspect_name] -= 0.5  # Openly mentioning evidence may indicate innocence
                   
       return correlation
   ```

5. **Confidence Calculation**
   
   The AI determines its confidence level in identifying the culprit:

   ```python
   def calculate_confidence(top_suspect_score, second_suspect_score, contradictions_found):
       # Base confidence on the gap between top suspects
       if second_suspect_score == 0:
           score_ratio = 1.0
       else:
           score_ratio = top_suspect_score / second_suspect_score
           
       # Adjust based on contradictions
       contradiction_factor = min(1.0, len(contradictions_found) * 0.15)
       
       # Final confidence calculation
       confidence = (0.5 * score_ratio) + (0.5 * contradiction_factor)
       
       # Normalize to 0-1 range
       return min(1.0, max(0.1, confidence))
   ```

### Detective's Investigation Process

The AI detective follows these steps to solve a case:

1. **Initial Evidence Collection**
   - The detective examines the crime scene evidence
   - Information about the victim, crime location, and timeline is established

2. **Suspect Interrogation Strategy**
   - The detective prioritizes suspects based on their relationship to the victim
   - Questions are tailored to probe for inconsistencies and gauge reactions
   - Each interrogation builds on knowledge gained from previous ones

3. **Contradiction Analysis**
   - Statements from different suspects are cross-referenced
   - Temporal and spatial contradictions are identified (e.g., alibis that don't match witness accounts)
   - Contradictions are weighted based on their significance to the case

4. **Behavioral Observation**
   - The detective monitors suspects for signs of deception
   - Nervousness, confidence, and hesitation are factored into suspicion scoring
   - Baseline personality traits are considered to avoid false positives

5. **Evidence Mapping**
   - Evidence is mapped to suspect statements and movements
   - Access to the crime scene and murder weapon are particularly important
   - Specialized knowledge about the crime is weighted heavily

6. **Suspicion Scoring**
   - All factors are combined into a comprehensive suspicion score
   - Scores are normalized to allow comparison between suspects
   - The highest scoring suspect is identified as the primary culprit

7. **Confidence Assessment**
   - The detective evaluates how certain it is of its conclusion
   - The gap between the top suspect and others affects confidence
   - The number and quality of contradictions found influence certainty

8. **Deduction Presentation**
   - The detective presents its reasoning step by step
   - Key evidence and contradictions are highlighted
   - The final culprit is named with a confidence percentage

### AI Implementation Decisions

1. **Why Rule-Based Over Machine Learning**

   We chose a rule-based approach with statistical elements instead of a pure machine learning approach for several reasons:

   - **Interpretability**: The detective's reasoning process needs to be transparent and explainable
   - **Controlled randomness**: The system allows for varying solutions without unpredictable results
   - **Resource efficiency**: No need for training data or computationally expensive models
   - **Domain knowledge integration**: Detective heuristics can be directly encoded in rules

2. **Suspicion Scoring Design**

   The suspicion scoring system is designed to mimic human detective work:

   - Multiple small pieces of evidence can accumulate against a suspect
   - A single major contradiction can significantly increase suspicion
   - Behavior during questioning affects perception of guilt
   - Motive and opportunity are weighted as important factors

3. **Confidence Calibration**

   The AI's confidence reporting is calibrated to:

   - Express higher confidence when evidence strongly points to one suspect
   - Reduce confidence when multiple suspects have similar suspicion levels
   - Increase with the number of contradictions found (more evidence = more confidence)
   - Never reach 100% certainty unless there is overwhelming evidence

4. **NPC Guilty Behavior**

   In the visualization, NPCs exhibit behaviors influenced by their guilt level:

   ```python
   def update_npc_behavior(self, npc):
       # ... state management ...
       
       # Guilt affects speed and movement
       speed_factor = 0.8 + (npc.get("guilt", 0.1) * 0.5)
       jitter = npc.get("guilt", 0.1) * 2.0
       
       # Add random movement for stressed NPCs
       dx += random.uniform(-jitter, jitter)
       dy += random.uniform(-jitter, jitter)
   ```

   This creates visual cues for the player to observe behavior that the detective AI is analyzing.

### Technical Challenges and Solutions

1. **Balancing Detective Performance**

   Creating an AI detective that is neither too perfect nor too incompetent required careful tuning:
   - Some randomness is introduced in suspicion scoring
   - Contradictions vary in how obvious they are to detect
   - Red herrings are included to occasionally mislead the AI

2. **Procedural Case Generation**

   Generating interesting and solvable cases is challenging:
   - Each case must have sufficient clues to reach a conclusion
   - Contradictions must be logical and consistent
   - Varied case types keep the game interesting
   - The guilty suspect must leave detectable evidence

3. **Investigation Visualization**

   Translating the detective's internal logic into visible actions required:
   - A step-by-step deduction presentation
   - Visualization of the detective's movement between suspects
   - Clear representation of the interrogation process
   - Dynamic dialogue that reflects the AI's thought process

### Future AI Enhancements

Potential AI improvements include:

1. **Learning from Past Cases**
   - Implementing a simple learning mechanism to improve performance over time
   - Adjusting suspicion weights based on success/failure in previous cases

2. **More Complex Deduction Chains**
   - Adding multi-step logical inference
   - Incorporating more advanced temporal reasoning

3. **Suspect Relationship Analysis**
   - Adding analysis of relationships between suspects
   - Detecting collusion and false alibis between connected suspects

4. **Adaptive Questioning**
   - Developing more dynamic questioning based on previous responses
   - Adding follow-up questions when inconsistencies are detected

## Key Components

### Detective Game Class

The `DetectiveGame` class is the core of the visualization system:

```python
class DetectiveGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Detective AI Investigation")
        self.clock = pygame.time.Clock()
        # ... initialization of game states and systems
        
    def run(self, json_data):
        """Run game with specified case"""
        self.load_case(json_data)
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        return self.conclusion["correct"] if self.conclusion else False
```

### Autonomous Detective Movement

One of the key features is the detective's ability to move autonomously between floors to interrogate suspects:

```python
def move_detective_autonomously(self):
    """Move detective autonomously toward target"""
    player = self.images[self.player_id]
    
    # Fix Y position if needed
    expected_y = self.movement.floor_positions[player["floor"]]
    if abs(player["position"][1] - expected_y) > 2:
        player["position"] = (player["position"][0], expected_y)
    
    # Return to ground floor if no target or in deduction phase
    if not self.target_npc or self.game_phase == "deduction":
        if player["floor"] != 0:
            # Move toward elevator
            elevator_x = 265
            if abs(player["position"][0] - elevator_x) > 5:
                # ... movement logic ...
            else:
                # Go down one floor
                if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                    self.movement.change_floor(player, -1)
                    self.last_floor_change = pygame.time.get_ticks()
        return
    
    # ... more movement logic ...
```

### Case Processing

The `CaseProcessor` handles the interrogation sequence, extracting dialogues from the JSON data:

```python
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
    
    # ... dialogue extraction logic ...
    
    return npc_id, current_question, current_answer
```

### Game Phases

The game progresses through three main phases:

1. **Exploration Phase**: The detective moves between floors to interrogate suspects
2. **Deduction Phase**: The detective returns to the ground floor and presents deductions
3. **Conclusion Phase**: The detective announces the culprit and the confidence level

```python
def set_next_target(self):
    """Set the next NPC to interrogate"""
    npc_id, question, answer = self.case_processor.get_next_dialogue()
    
    if npc_id:
        # ... interrogation setup ...
    elif self.game_phase == "exploration":
        # Move to deduction phase
        self.game_phase = "deduction"
        self.images[self.player_id]["floor"] = 0
        
        # Get all deductions
        # ...
    elif self.game_phase == "deduction" and self.current_deduction >= len(self.deductions):
        # Move to conclusion phase
        self.game_phase = "conclusion"
        self.conclusion = self.case_processor.get_conclusion()
```

### Elevator System

The movement system handles the detective's ability to change floors using the elevator:

```python
def change_floor(self, entity, direction):
    new_floor = entity["floor"] + direction
    if 0 <= new_floor < len(self.floor_positions):
        entity["floor"] = new_floor
        entity["position"] = (entity["position"][0], self.floor_positions[entity["floor"]])
        if self.elevator_sound:
            self.elevator_sound.play()
```

### NPC Behavior

NPCs move naturally on their floor, with their behavior affected by their guilt level:

```python
def update_npc_behavior(self, npc):
    """Update NPC behavior"""
    # ... state management ...
    
    if npc["state"] == "walking":
        # Move toward target
        if npc["target_pos"]:
            # ... movement calculations ...
            
            # Guilt affects speed and movement
            speed_factor = 0.8 + (npc.get("guilt", 0.1) * 0.5)
            jitter = npc.get("guilt", 0.1) * 2.0
            
            # Add random movement for stressed NPCs
            dx += random.uniform(-jitter, jitter)
            dy += random.uniform(-jitter, jitter)
            
            # ... more movement code ...
```

### Dialogue System

The game features an automatic dialogue system that displays the detective's interrogation process:

```python
def render_dialogue(self):
    # Dialogue panel
    pygame.draw.rect(self.screen, (40, 40, 40, 200), (50, 450, 500, 180))
    pygame.draw.rect(self.screen, (200, 200, 200), (50, 450, 500, 180), 2)
    
    # Display current dialogue
    if 0 <= self.dialogue_progress < len(self.current_dialogue):
        current_text = self.current_dialogue[self.dialogue_progress]
        
        # Split speaker and text
        parts = current_text.split(": ", 1)
        if len(parts) >= 2:
            speaker, text = parts
            # Speaker name in color
            draw_text(self.screen, speaker + ":", (70, 470), color=(255, 255, 0))
            
            # Text with line wrapping
            # ... text wrapping logic ...
```

### Case Generation

The system includes a case generator that creates unique mysteries:

```python
def main():
    # Generate a new mystery case
    print("Generating mystery case...")
    case_data = create_plot.generate_case()
    
    # ... display case info ...
    
    # Run the detective's investigation
    print("\nBeginning investigation...")
    culprit, reasoning = detective.investigate(case_data)
    
    # ... save case and visualize if requested ...
```

## Floor System

The game uses a multi-floor building structure:

- **Ground Floor (Floor 0)**: Y-position 552, starting point for the detective
- **1st Floor (Floor 1)**: Y-position 461
- **2nd Floor (Floor 2)**: Y-position 387
- **3rd Floor (Floor 3)**: Y-position 314
- **4th Floor (Floor 4)**: Y-position 241
- **5th Floor (Floor 5)**: Y-position 168

Each floor can have NPCs (suspects) that the detective needs to interrogate.

## Fast Mode

The game includes a fast mode (toggled with F key) that speeds up:
- Dialogue progression
- Detective movement 
- Deduction presentation

This is useful for quickly viewing the entire investigation process.

## Assets Management

The game manages sprite animations and character appearances:

```python
def update_rect(images):
    for key in images:
        img_data = images[key]
        if "sprite" in img_data:
            sprite_w, sprite_h = img_data["sprite"]
            index = img_data["index"]
            
            original = img_data["_original"]
            sprite_rect = pygame.Rect(
                index * sprite_w,
                0,
                sprite_w,
                sprite_h
            )
            img_data["image"] = original.subsurface(sprite_rect)
            # Update collision rect
            img_data["rect"] = pygame.Rect(
                img_data["position"][0], 
                img_data["position"][1],
                50,  # Collision width
                66   # Collision height
            )
    return images
```

## Technical Implementation

The game combines traditional game development with AI algorithms:

1. **Pygame**: Used for rendering, input handling, and game loop
2. **AI Detective Algorithm**: Analyzes statements, finds contradictions, and makes deductions
3. **JSON Case Format**: Standardized format for case information and detective reasoning
4. **Autonomous Movement System**: Handles pathfinding and character animation
5. **State Machine**: Manages game phases and transitions