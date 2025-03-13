import pygame
import sys
import json
from detective_game import DetectiveGame

def main():
    # Vérifier les arguments de ligne de commande pour un fichier JSON
    case_file = "case.json"
    
    if len(sys.argv) > 1:
        case_file = sys.argv[1]
    
    try:
        # Charger le JSON du cas depuis un fichier
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = f.read()
            case_data = json.loads(case_data)
    except FileNotFoundError:
        print(f"Erreur: le fichier {case_file} n'a pas été trouvé.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erreur: le fichier {case_file} n'est pas un JSON valide.")
        sys.exit(1)
    
    # Si le fichier JSON existe mais qu'on veut utiliser les données intégrées dans le code
    if case_file == "embedded":
        with open("paste.txt", "r", encoding="utf-8") as f:
            case_data = f.read()
            case_data = json.loads(case_data)
    
    # Lancer le jeu avec le cas
    game = DetectiveGame()
    result = game.run(case_data)
    
    print("Résultat de l'enquête:", "Réussite" if result else "Échec")

if __name__ == "__main__":
    main()