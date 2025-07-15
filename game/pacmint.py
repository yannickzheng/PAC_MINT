import os
import sys

import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from common.global_variable import HEIGHT, WIDTH
from game.core.assets import load_game_assets
from game.gameplay.offline_game import offline_game
from game.gameplay.online_game import main_game
from game.menus.main_menu import main_menu, select_online_role, select_role
from game.menus.online_menu import create_game, join_game, online_menu
from game.utils.helpers import preload_assets

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")
font = pygame.font.SysFont("Arial", 24)

# Load resources
assets = load_game_assets()


def main():
    """Main game function"""
    # Précharger les assets
    preload_assets(screen, font)

    while True:
        # Menu principal
        choice, role = main_menu(screen, assets["background_image"], font)

        if choice == "offline":
            # Mode hors ligne
            offline_game(
                screen,
                font,
                assets["coin_image"],
                assets["fruit_image"],
                assets["coin_size"],
                assets["fruit_size"],
                role,
            )

        elif choice == "online":
            # Mode en ligne - navigation dans les sous-menus
            while True:
                online_choice = online_menu(screen, assets["background_image"], font)
                if online_choice == "create":
                    # Créer une partie
                    role = select_online_role(screen, font)
                    if role == "back":
                        continue
                    else:
                        main_game(
                            is_created_game=True,
                            game_code=None,
                            screen=screen,
                            font=font,
                            coin_image=assets["coin_image"],
                            fruit_image=assets["fruit_image"],
                            coin_offset=assets["coin_offset"],
                            fruit_offset=assets["fruit_offset"],
                            role=role,
                        )
                elif online_choice == "join":
                    # Rejoindre une partie
                    join_result = join_game(screen, assets["background_image"], font)
                    if join_result == "back":
                        continue
                    elif join_result:  # Code de partie saisi
                        role = select_online_role(screen, font)
                        if role == "back":
                            continue
                        else:
                            main_game(
                                is_created_game=False,
                                game_code=join_result,
                                screen=screen,
                                font=font,
                                coin_image=assets["coin_image"],
                                fruit_image=assets["fruit_image"],
                                coin_offset=assets["coin_offset"],
                                fruit_offset=assets["fruit_offset"],
                                role=role,
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
