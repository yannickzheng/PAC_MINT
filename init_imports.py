"""
Configuration simple et robuste des imports pour PAC_MINT
Ce module doit être importé en premier dans les points d'entrée
"""

import sys
import os


def init_project_imports():
    """
    Configure les imports du projet de manière robuste
    Fonctionne peu importe l'IDE ou la façon de lancer le programme
    """
    # Obtenir le répertoire du fichier actuel
    current_file_dir = os.path.dirname(os.path.abspath(__file__))

    # Le répertoire racine du projet (où se trouve ce fichier)
    project_root = current_file_dir

    # Ajouter le répertoire racine au début du PYTHONPATH
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


# Appel automatique lors de l'import
init_project_imports()
