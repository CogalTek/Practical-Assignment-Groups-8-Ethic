from src.create_plot import generate_case
import pygame
import random
import json
import os
from src.detective_game import DetectiveGame
from src.detective import investigate

def save_case_history(case_data, detective_reasoning, correct):
    """Save case data and detective reasoning for training purposes"""
    if not os.path.exists("case_history"):
        os.makedirs("case_history")
    
    history = {
        "case": case_data,
        "detective_reasoning": detective_reasoning,
        "correct": correct
    }
    
    # Generate a unique filename
    filename = f"case_history/case_{random.randint(1000, 9999)}.json"
    with open(filename, 'w') as f:
        json.dump(history, f, indent=4)
    
    print(f"Case history saved to {filename}")
    return filename

def main():
    # Generate a new mystery case
    print("Generating mystery case...")
    case_data = generate_case()
    
    # Display some basic information about the case
    print(f"\nMYSTERY CASE: {case_data['crime']['crime_type']}")
    print(f"Crime occurred at: {case_data['crime']['location']} at {case_data['crime']['time']}")
    print(f"Victim: {case_data['crime']['victim']}")
    print("\nSuspects:")
    for suspect in case_data['suspects']:
        print(f"- {suspect['name']}, {suspect['occupation']}")
    
    # Run the detective's investigation
    print("\nBeginning investigation...")
    culprit, reasoning = investigate(case_data)
    
    # Check if detective found the correct culprit
    correct = culprit == case_data['culprit']['name']
    
    # Display results
    print("\n--- INVESTIGATION RESULTS ---")
    print(f"Detective's conclusion: The culprit is {culprit}")
    print(f"Actual culprit: {case_data['culprit']['name']}")
    if correct:
        print("Detective was CORRECT!")
    else:
        print("Detective was WRONG!")
    
    # Save the case for training
    case_file = save_case_history(case_data, reasoning, correct)
    
    # Ask user if they want to visualize the investigation
    visualize = input("\nDo you want to visualize the investigation? (y/n): ")
    
    if visualize.lower() == 'y':
        print(f"Running visualization using case file: {case_file}")
        
        # Load the saved case data
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = json.load(f)
            
        # Run the game with the newly created case
        game = DetectiveGame()
        result = game.run(case_data)
        
        print("Visualization complete!")
        print("Investigation result:", "Success" if result else "Failure")
    
    return correct, case_data, reasoning

if __name__ == "__main__":
    main()