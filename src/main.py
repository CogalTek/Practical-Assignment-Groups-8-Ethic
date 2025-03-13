import pygame
import sys
import json
from detective_game import DetectiveGame

def main():
    # Check for JSON file argument
    case_file = "case.json"  # Default file provided
    
    if len(sys.argv) > 1:
        case_file = sys.argv[1]
    
    try:
        # Load case data from file
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = f.read()
            case_data = json.loads(case_data)
    except FileNotFoundError:
        print(f"Error: file {case_file} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: file {case_file} is not valid JSON.")
        sys.exit(1)
    
    # Run game with case data
    game = DetectiveGame()
    result = game.run(case_data)
    
    print("Investigation result:", "Success" if result else "Failure")

if __name__ == "__main__":
    main()