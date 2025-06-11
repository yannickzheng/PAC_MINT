import pygame
import sys
import os

# Ajout du chemin pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.global_variable import WIDTH, HEIGHT
from game.core.music import init_music, play_music
from game.core.assets import load_game_assets
from game.menus.main_menu import main_menu
from game.menus.online_menu import online_menu, create_game, join_game
from game.gameplay.offline_game import offline_game
from game.gameplay.online_game import main_game
from game.utils.helpers import preload_assets

# Initialisation de pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")
font = pygame.font.SysFont("Arial", 24)

# Initialisation de la musique
init_music()
play_music("sound/background_sound.mp3", 0.9)

# Chargement des ressources
assets = load_game_assets()

def main():
    """Fonction principale du jeu - identique à l'original"""
    # Précharger les assets
    preload_assets(screen, font)
    
    while True:
        # Menu principal
        choice = main_menu(screen, assets['background_image'], font)
        
        if choice == "offline":
            # Mode hors ligne
            offline_game(
                screen, font, 
                assets['coin_image'], assets['fruit_image'],
                assets['coin_size'], assets['fruit_size']
            )
        
        elif choice == "online":
            # Mode en ligne - navigation dans les sous-menus
            while True:
                online_choice = online_menu(screen, assets['background_image'], font)
                
                if online_choice == "create":
                    # Créer une partie
                    create_choice = create_game(screen, assets['background_image'], font)
                    if create_choice == "start":
                        main_game(
                            is_created_game=True, 
                            game_code=None,
                            screen=screen, 
                            font=font,
                            coin_image=assets['coin_image'],
                            fruit_image=assets['fruit_image'],
                            coin_offset=assets['coin_offset'],
                            fruit_offset=assets['fruit_offset']
                        )
                    elif create_choice == "back":
                        continue
                
                elif online_choice == "join":
                    # Rejoindre une partie
                    join_result = join_game(screen, assets['background_image'], font)
                    if join_result == "back":
                        continue
                    elif join_result:  # Code de partie saisi
                        main_game(
                            is_created_game=False, 
                            game_code=join_result,
                            screen=screen, 
                            font=font,
                            coin_image=assets['coin_image'],
                            fruit_image=assets['fruit_image'],
                            coin_offset=assets['coin_offset'],
                            fruit_offset=assets['fruit_offset']
                        )
                
                elif online_choice == "back":
                    break
        
        else:
            # Quitter le jeu
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
