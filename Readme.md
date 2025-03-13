# AI Detective Game

## Project Overview

This project is an interactive detective game that uses AI to investigate cases autonomously. The detective analyzes evidence, interrogates suspects, and makes deductions to solve mysteries. The game features:

- Procedural generation of mystery cases with different crimes, suspects, and motives
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

## Development Notes

The detective AI makes decisions based on:
- Contradictions between suspect statements
- Suspicious behavior during interrogation
- Evidence found at the crime scene
- Relationships between suspects and the victim

The visualization system faithfully represents the detective's thought process and movement throughout the building as it conducts its investigation.

## Future Improvements

Potential future improvements include:
- More complex case generation with multiple crimes
- Additional interrogation techniques
- Improved NPC behavior with more complex movement patterns
- Additional visual effects and animations
- Sound effects for different actions