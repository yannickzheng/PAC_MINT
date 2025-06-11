import pygame
from game.map import MAP_DATA
from common.global_variable import CELL_SIZE
from pygame import mixer
from game.ui.components import display_loading_screen

def is_wall_at_position(x, y):
    """Vérifie si la position contient un mur sur la carte"""
    # Conversion des coordonnées en indices de cellule dans la grille
    grid_x = x // CELL_SIZE
    grid_y = y // CELL_SIZE
    
    # Vérification des limites de la grille
    if grid_x < 0 or grid_x >= len(MAP_DATA[0]) or grid_y < 0 or grid_y >= len(MAP_DATA):
        return True  # En dehors de la carte, considéré comme un mur
    
    # Vérification si la cellule est un mur
    return MAP_DATA[grid_y][grid_x] == 1

def distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points"""
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def preload_assets(screen, font):
    """Précharge les ressources du jeu pour accélérer le démarrage"""
    display_loading_screen("Chargement des ressources...", screen, font)
    # Préchargement des images
    images = [
        "images/pacman - right.png",
        "images/pacman - left.png",
        "images/pacman - up.png",
        "images/pacman - down.png",
        "images/red_ghost.png",
        "images/Black Pacman.png",
        "images/Black Pacman-left.png",
        "images/Black Pacman-up.png",
        "images/Black Pacman-down.png"
    ]
    
    for img_path in images:
        pygame.image.load(img_path)
    
    # Préchargement des sons
    sounds = [
        "sound/button_click.mp3",
        "sound/game_sound.mp3",
        "sound/background_sound.mp3"
    ]
    
    for sound_path in sounds:
        try:
            if sound_path.endswith(".mp3"):
                mixer.Sound(sound_path)
        except:
            print(f"Impossible de charger le son: {sound_path}")
    
    # Attendre un peu pour que l'utilisateur puisse voir l'écran de chargement
    pygame.time.delay(500)
