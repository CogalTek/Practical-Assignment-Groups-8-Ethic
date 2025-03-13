import pygame
import random
import math
from src.assets import load_images, get_player, update_rect
from src.movement_system import MovementSystem
from src.case_processor import CaseProcessor
from src.utils import draw_text

class DetectiveGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Detective AI Investigation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        # Main systems
        self.movement = MovementSystem()
        self.case_processor = CaseProcessor()
        
        # Load resources
        self.images = load_images()
        self.player_id = get_player(self.images)
        self.init_elevator_sound()
        
        # Game states
        self.running = True
        self.active_npc = None
        self.dialogue_active = False
        self.game_phase = "exploration"  # exploration, deduction, conclusion
        self.target_npc = None
        self.current_dialogue = []
        self.dialogue_progress = 0
        self.last_dialogue_time = 0
        self.dialogue_speed = 1000  # Milliseconds between dialogues
        self.current_deduction = None
        self.deductions = []
        self.conclusion = None
        self.show_controls = False
        self.fast_mode = False
        self.last_floor_change = 0
        self.interrogated_npcs = []
        
        # Initialize active NPCs
        self.active_npcs = []

    def init_elevator_sound(self):
        pygame.mixer.init()
        try:
            self.elevator_sound = pygame.mixer.Sound("./content/ascenseur.wav")
            self.movement.set_elevator_sound(self.elevator_sound)
        except pygame.error:
            self.elevator_sound = None

    def load_case(self, json_data):
        """Load case data and initialize the game"""
        num_suspects = self.case_processor.load_case(json_data)
        
        # Activate NPCs for this case
        self.active_npcs = self.case_processor.get_active_npcs()
        
        # Make sure detective starts at ground floor
        self.images[self.player_id]["floor"] = 0
        self.images[self.player_id]["position"] = (300, self.movement.floor_positions[0])
        
        # Update NPCs with their floors and guilt values
        for npc_id in self.active_npcs:
            if npc_id in self.images:
                # NPC floor based on ID (npc01 -> floor 1)
                npc_number = int(npc_id[3:])
                correct_floor = npc_number
                
                # Set floor and Y position
                self.images[npc_id]["floor"] = correct_floor
                self.images[npc_id]["position"] = (
                    self.images[npc_id]["position"][0],
                    self.movement.floor_positions[correct_floor]
                )
                
                # Update guilt value
                self.images[npc_id]["guilt"] = self.case_processor.get_suspect_guilt(npc_id)
        
        # Start in exploration phase
        self.game_phase = "exploration"
        self.set_next_target()

    def set_next_target(self):
        """Set the next NPC to interrogate"""
        npc_id, question, answer = self.case_processor.get_next_dialogue()
        
        if npc_id:
            self.target_npc = npc_id
            
            # Get suspect name for this NPC
            suspect_name = None
            if npc_id in self.case_processor.npc_to_suspect:
                suspect_name = self.case_processor.npc_to_suspect[npc_id]
                
            self.current_dialogue = [
                f"Detective: {question}",
                f"{suspect_name if suspect_name else npc_id}: {answer}"
            ]
            
            # Add to interrogated NPCs list
            if npc_id not in self.interrogated_npcs:
                self.interrogated_npcs.append(npc_id)
                
        elif self.game_phase == "exploration":
            # Move to deduction phase
            self.game_phase = "deduction"
            # Move player to ground floor
            self.images[self.player_id]["floor"] = 0
            
            # Get all deductions
            deduction = self.case_processor.get_next_deduction()
            while deduction:
                self.deductions.append(deduction)
                deduction = self.case_processor.get_next_deduction()
                
            self.current_deduction = 0
        elif self.game_phase == "deduction" and self.current_deduction >= len(self.deductions):
            # Move to conclusion phase
            self.game_phase = "conclusion"
            self.conclusion = self.case_processor.get_conclusion()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.show_controls = not self.show_controls
                elif event.key == pygame.K_SPACE:
                    self.handle_space_press()
                elif event.key == pygame.K_f:
                    self.toggle_fast_mode()

    def handle_space_press(self):
        """Handle manual interaction with space bar"""
        if self.dialogue_active:
            self.dialogue_progress += 1
            if self.dialogue_progress >= len(self.current_dialogue):
                self.dialogue_active = False
                self.dialogue_progress = 0
                
                if self.active_npc == self.target_npc:
                    self.set_next_target()
        
        elif self.game_phase == "deduction":
            self.current_deduction += 1
            if self.current_deduction >= len(self.deductions):
                self.game_phase = "conclusion"
                self.conclusion = self.case_processor.get_conclusion()
        
        elif self.active_npc and self.active_npc == self.target_npc:
            self.dialogue_active = True
            self.dialogue_progress = 0
            self.last_dialogue_time = pygame.time.get_ticks()
    
    def toggle_fast_mode(self):
        """Toggle fast mode for simulation"""
        self.fast_mode = not self.fast_mode
    
    def update(self):
        player = self.images[self.player_id]
        
        # Ensure Y position matches floor
        expected_y = self.movement.floor_positions[player["floor"]]
        if abs(player["position"][1] - expected_y) > 2:
            player["position"] = (player["position"][0], expected_y)
        
        if not self.dialogue_active and self.game_phase in ["exploration", "deduction"]:
            # Autonomous detective movement
            self.move_detective_autonomously()
            
            # Update active NPC
            self.active_npc = None
            
            # Check for collisions with NPCs
            player_rect = pygame.Rect(player["position"], (50, 50))
            for npc_id in self.active_npcs:
                npc = self.images.get(npc_id)
                if not npc:
                    continue
                    
                if npc.get('floor') != player.get('floor'):
                    continue
                    
                npc_rect = pygame.Rect(npc["position"], (50, 50))
                
                if player_rect.colliderect(npc_rect):
                    self.active_npc = npc_id
                    # Auto-start dialogue with target NPC
                    if self.active_npc == self.target_npc and not self.dialogue_active:
                        self.start_dialogue_automatically()
                    break
        
        # Update NPCs
        self.update_npcs()
                    
        # Update collision rects
        update_rect(self.images)
        
        # Auto-advance dialogue
        self.advance_dialogue_automatically()
        
        # Auto-advance deductions
        self.advance_deduction_automatically()
    
    def update_npcs(self):
        """Update all NPCs"""
        for npc_id in self.active_npcs:
            npc = self.images.get(npc_id)
            if npc and not self.dialogue_active:
                # Ensure NPC stays at assigned floor
                npc_number = int(npc_id[3:])
                correct_floor = npc_number
                
                # Fix Y position if needed
                expected_y = self.movement.floor_positions[correct_floor]
                actual_y = npc["position"][1]
                
                if abs(actual_y - expected_y) > 2:
                    npc["position"] = (npc["position"][0], expected_y)
                
                # Ensure floor number is correct
                if npc.get('floor') != correct_floor:
                    npc['floor'] = correct_floor
                    
                # Update behavior
                self.update_npc_behavior(npc)
    
    def update_npc_behavior(self, npc):
        """Update NPC behavior"""
        current_time = pygame.time.get_ticks()
        
        # Ensure NPC stays on its floor
        npc_id = npc.get("id", "")
        if npc_id.startswith("npc"):
            npc_number = int(npc_id[3:])
            npc_floor = npc_number
            
            # Fix Y position if needed
            if npc.get("floor") != npc_floor:
                npc["floor"] = npc_floor
                npc["position"] = (npc["position"][0], self.movement.floor_positions[npc_floor])
        
        # States management: idle, walking
        if "last_state_change" not in npc:
            npc["last_state_change"] = current_time
            npc["state"] = "idle"
            npc["target_pos"] = None
            npc["wait_time"] = random.randint(3000, 7000)
        
        # State transitions
        time_since_change = current_time - npc["last_state_change"]
        
        if npc["state"] == "idle" and time_since_change > npc["wait_time"]:
            # Switch to walking
            npc["state"] = "walking"
            
            # Choose target position on same floor
            floor_y = self.movement.floor_positions[npc["floor"]]
            npc["target_pos"] = (random.randint(100, 500), floor_y)
            npc["last_state_change"] = current_time
        
        elif npc["state"] == "walking":
            # Move toward target
            if npc["target_pos"]:
                # Calculate distance to target
                dx = npc["target_pos"][0] - npc["position"][0]
                dy = npc["target_pos"][1] - npc["position"][1]
                distance = math.hypot(dx, dy)
                
                # Guilt affects speed and movement
                speed_factor = 0.8 + (npc.get("guilt", 0.1) * 0.5)
                jitter = npc.get("guilt", 0.1) * 2.0
                
                # Add random movement for stressed NPCs
                dx += random.uniform(-jitter, jitter)
                dy += random.uniform(-jitter, jitter)
                
                # If arrived at destination
                if distance < 5:
                    npc["state"] = "idle"
                    npc["wait_time"] = random.randint(3000, 7000)
                    npc["last_state_change"] = current_time
                else:
                    # Move toward target
                    speed = 2.0 * speed_factor
                    new_x = npc["position"][0] + (dx / distance) * speed
                    new_y = self.movement.floor_positions[npc["floor"]]
                    npc["position"] = (new_x, new_y)
                    
                    # Animation based on direction
                    if dx > 0:
                        npc["index"] = 5  # Right
                    elif dx < 0:
                        npc["index"] = 1  # Left
                    else:
                        npc["index"] = 3  # Face
    
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
                    if player["position"][0] < elevator_x:
                        player["position"] = (player["position"][0] + 3, player["position"][1])
                        player["index"] = 5  # Right
                    else:
                        player["position"] = (player["position"][0] - 3, player["position"][1])
                        player["index"] = 1  # Left
                else:
                    # Go down one floor
                    if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                        self.movement.change_floor(player, -1)
                        self.last_floor_change = pygame.time.get_ticks()
            return
        
        # Find target floor
        target_npc = self.images.get(self.target_npc)
        if not target_npc:
            return
            
        target_floor = target_npc["floor"]
        
        # If not on the right floor, use elevator
        if player["floor"] != target_floor:
            elevator_x = 265
            if abs(player["position"][0] - elevator_x) > 5:
                if player["position"][0] < elevator_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Right
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Left
            else:
                # At elevator, change floor
                player["position"] = (elevator_x, player["position"][1])
                
                # Determine direction
                direction = 1 if target_floor > player["floor"] else -1
                
                if pygame.time.get_ticks() - getattr(self, "last_floor_change", 0) > 1000:
                    self.movement.change_floor(player, direction)
                    self.last_floor_change = pygame.time.get_ticks()
        else:
            # On right floor, move toward target
            target_x = target_npc["position"][0]
            if abs(player["position"][0] - target_x) > 30:
                if player["position"][0] < target_x:
                    player["position"] = (player["position"][0] + 3, player["position"][1])
                    player["index"] = 5  # Right
                else:
                    player["position"] = (player["position"][0] - 3, player["position"][1])
                    player["index"] = 1  # Left
            else:
                # Close enough, stay still
                player["index"] = 3  # Face
    
    def start_dialogue_automatically(self):
        """Auto-start dialogue when detective meets target"""
        current_time = pygame.time.get_ticks()
        if hasattr(self, "last_dialogue_end") and current_time - self.last_dialogue_end < 1500:
            return
            
        self.dialogue_active = True
        self.dialogue_progress = 0
        self.last_dialogue_time = current_time
        
    def advance_dialogue_automatically(self):
        """Auto-advance dialogue after delay"""
        if not self.dialogue_active:
            return
            
        current_time = pygame.time.get_ticks()
        dialogue_delay = 500 if self.fast_mode else 2000
        
        if current_time - self.last_dialogue_time > dialogue_delay:
            self.dialogue_progress += 1
            self.last_dialogue_time = current_time
            
            if self.dialogue_progress >= len(self.current_dialogue):
                self.dialogue_active = False
                self.dialogue_progress = 0
                self.last_dialogue_end = current_time
                
                if self.active_npc == self.target_npc:
                    self.set_next_target()
    
    def advance_deduction_automatically(self):
        """Auto-advance deductions"""
        if self.game_phase != "deduction" or len(self.deductions) == 0:
            return
            
        current_time = pygame.time.get_ticks()
        deduction_delay = 800 if self.fast_mode else 3000
        
        if not hasattr(self, "last_deduction_time") or current_time - self.last_deduction_time > deduction_delay:
            self.current_deduction += 1
            self.last_deduction_time = current_time
            
            if self.current_deduction >= len(self.deductions):
                self.game_phase = "conclusion"
                self.conclusion = self.case_processor.get_conclusion()
    
    def render(self):
        # Background
        self.screen.fill((0, 0, 0))
        
        # Draw background image
        bg = self.images.get("background", {})
        self.screen.blit(bg.get("image", None), bg.get("position", (0, 0)))
        
        # Draw floor labels
        floors = ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor", "4th Floor", "5th Floor"]
        for i, y in enumerate(self.movement.floor_positions):
            draw_text(self.screen, floors[i], (20, y - 20), color=(200, 200, 200))
        
        # Draw current floor indicator
        current_floor = self.images[self.player_id]["floor"]
        draw_text(self.screen, f"Current Floor: {floors[current_floor]}", (380, 20), color=(255, 255, 0))
        
        # Draw entities on current floor only
        for entity_id, entity in self.images.items():
            if entity_id == "background":
                continue
                
            if entity_id not in ["background", self.player_id] and entity_id not in self.active_npcs:
                continue
                
            if entity.get('floor', -1) == current_floor:
                self.screen.blit(entity["image"], entity["position"])
                
                # Target indicator
                if entity_id == self.target_npc:
                    pygame.draw.circle(
                        self.screen, 
                        (0, 255, 0), 
                        (entity["position"][0] + 25, entity["position"][1] - 15), 
                        8
                    )
                
                # Interactive NPC indicator
                if entity.get('npc', False) and entity_id == self.active_npc:
                    pygame.draw.circle(
                        self.screen, 
                        (255, 255, 0), 
                        (entity["position"][0] + 25, entity["position"][1] - 10), 
                        5
                    )
        
        # UI elements
        self.render_ui()
        
        # Dialogue or deductions
        if self.dialogue_active:
            self.render_dialogue()
        elif self.game_phase == "deduction" and len(self.deductions) > 0:
            self.render_deduction()
        elif self.game_phase == "conclusion" and self.conclusion:
            self.render_conclusion()
            
        # Controls
        if self.show_controls:
            self.render_controls()
            
        pygame.display.flip()
    
    def render_ui(self):
        # Interface bar
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 650, 600, 50))
        
        # Current phase
        phase_text = {
            "exploration": "Phase: Investigation",
            "deduction": "Phase: Deduction",
            "conclusion": "Phase: Conclusion"
        }.get(self.game_phase, "Phase: Investigation")
        
        draw_text(self.screen, phase_text, (10, 655), color=(255, 255, 255))
        
        # Interrogation counter
        interrogation_count = f"Interrogated: {len(self.interrogated_npcs)}/{len(self.active_npcs)}"
        draw_text(self.screen, interrogation_count, (200, 655), color=(255, 200, 0))
        
        # Status with suspect name
        status_text = ""
        if self.game_phase == "exploration":
            if self.dialogue_active and self.target_npc:
                suspect_name = self.case_processor.npc_to_suspect.get(self.target_npc, self.target_npc)
                status_text = f"Interrogating: {suspect_name}"
            elif self.target_npc:
                suspect_name = self.case_processor.npc_to_suspect.get(self.target_npc, self.target_npc)
                if self.images[self.player_id]["floor"] != self.images.get(self.target_npc, {}).get("floor", -1):
                    status_text = f"Going to: {suspect_name}"
                else:
                    status_text = f"Approaching: {suspect_name}"
            else:
                status_text = "Returning to ground floor"
        elif self.game_phase == "deduction":
            status_text = f"Analysis: ({self.current_deduction + 1}/{len(self.deductions)})"
        elif self.game_phase == "conclusion":
            status_text = "Concluding investigation"
            
        draw_text(self.screen, status_text, (350, 655), color=(200, 200, 200))
    
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
                words = text.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if len(test_line) < 60:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                for i, line in enumerate(lines):
                    draw_text(self.screen, line, (70, 500 + i * 25))
    
    def render_deduction(self):
        # Deduction panel
        pygame.draw.rect(self.screen, (40, 40, 60, 230), (50, 100, 500, 500))
        pygame.draw.rect(self.screen, (200, 200, 220), (50, 100, 500, 500), 2)
        
        # Title
        draw_text(self.screen, "Detective Analysis", (200, 120), font=self.title_font, color=(255, 255, 0))
        
        # Display current deductions
        if self.current_deduction < len(self.deductions):
            y_pos = 170
            for i in range(max(0, self.current_deduction - 8), self.current_deduction + 1):
                if i < len(self.deductions):
                    deduction = self.deductions[i]
                    
                    # Highlight current deduction
                    color = (255, 255, 255)
                    if i == self.current_deduction:
                        color = (0, 255, 0)
                        
                    # Add bullet prefix
                    prefix = "• "
                    
                    # Split text into lines
                    text = prefix + deduction
                    words = text.split()
                    lines = []
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        if len(test_line) < 60:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    for line in lines:
                        draw_text(self.screen, line, (70, y_pos), color=color)
                        y_pos += 25
                        
            # Progress indicator
            progress_text = f"Deduction {self.current_deduction + 1}/{len(self.deductions)}"
            draw_text(self.screen, progress_text, (70, 550), color=(200, 200, 200))
    
    def render_conclusion(self):
        # Conclusion panel
        pygame.draw.rect(self.screen, (40, 40, 60, 230), (50, 100, 500, 500))
        pygame.draw.rect(self.screen, (200, 200, 220), (50, 100, 500, 500), 2)
        
        # Title
        draw_text(self.screen, "Case Conclusion", (200, 120), font=self.title_font, color=(255, 215, 0))
        
        # Details
        y_pos = 180
        
        # Culprit
        culprit_text = f"The culprit is: {self.conclusion['culprit']}"
        draw_text(self.screen, culprit_text, (100, y_pos), color=(255, 100, 100))
        y_pos += 40
        
        # Confidence
        confidence = self.conclusion["confidence"] * 100
        confidence_text = f"Confidence in this conclusion: {confidence:.1f}%"
        draw_text(self.screen, confidence_text, (100, y_pos), color=(255, 255, 255))
        y_pos += 40
        
        # Result
        result_text = "Investigation successful!" if self.conclusion["correct"] else "Investigation failed!"
        result_color = (0, 255, 0) if self.conclusion["correct"] else (255, 0, 0)
        draw_text(self.screen, result_text, (100, y_pos), font=self.title_font, color=result_color)
        y_pos += 60
        
        # End message
        end_message = "The detective correctly identified the culprit!" if self.conclusion["correct"] else "The detective was wrong about the culprit."
        draw_text(self.screen, end_message, (100, y_pos), color=(255, 255, 255))
        y_pos += 40
        
        # Instructions
        draw_text(self.screen, "Press ESC to exit", (220, 500), color=(200, 200, 200))
    
    def render_controls(self):
        help_text = [
            "Controls:",
            "SPACE: Manual intervention",
            "F: Speed up/slow down",
            "H: Show/hide help",
            "ESC: Exit"
        ]
        
        # Semi-transparent background
        help_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 180))
        self.screen.blit(help_surface, (150, 200))
        
        # Help text
        for i, line in enumerate(help_text):
            draw_text(self.screen, line, (170, 210 + i * 25), color=(220, 220, 220))
            
        # Fast mode status
        mode_text = "Fast Mode: ON" if self.fast_mode else "Fast Mode: OFF"
        draw_text(self.screen, mode_text, (170, 210 + len(help_text) * 25), 
                 color=(255, 200, 0) if self.fast_mode else (180, 180, 180))
    
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