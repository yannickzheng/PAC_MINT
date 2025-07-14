import sys
import os
import pygame

# Chemin pour les imports relatifs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.api import login
from game.login_screen import login_screen
from common.global_variable import WIDTH, HEIGHT
from game.core.assets import load_game_assets
from game.menus.main_menu import main_menu, select_role, select_online_role
from game.menus.online_menu import online_menu, create_game, join_game
from game.gameplay.offline_game import offline_game
from game.gameplay.online_game import main_game
from game.utils.helpers import preload_assets

def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PacMint")
    font = pygame.font.SysFont("Arial", 24)

    # --- Connexion utilisateur ---
    user_id = None
    while user_id is None:
        username, password, user_id = login_screen(screen, font)
        user_id = login(username, password)
        if not user_id:
            show_error(screen, font, "Identifiants invalides. Réessaie.")

    print(f"Connexion réussie pour {username} (id: {user_id})")

    # Chargement des assets
    assets = load_game_assets()
    preload_assets(screen, font)

    # --- Boucle principale du jeu ---
    while True:
        choice, role = main_menu(screen, assets['background_image'], font)

        if choice == "offline":
            offline_game(
                screen, font,
                assets['coin_image'], assets['fruit_image'],
                assets['coin_size'], assets['fruit_size'],
                role,
                user_id=user_id
            )

        elif choice == "online":
            while True:
                online_choice = online_menu(screen, assets['background_image'], font)

                if online_choice == "create":
                    role = select_online_role(screen, font)
                    if role == "back":
                        continue
                    main_game(
                        is_created_game=True,
                        game_code=None,
                        screen=screen,
                        font=font,
                        coin_image=assets['coin_image'],
                        fruit_image=assets['fruit_image'],
                        coin_offset=assets['coin_offset'],
                        fruit_offset=assets['fruit_offset'],
                        role=role,
                        user_id=user_id
                    )

                elif online_choice == "join":
                    join_result = join_game(screen, assets['background_image'], font)
                    if join_result == "back":
                        continue
                    elif join_result:
                        role = select_online_role(screen, font)
                        if role == "back":
                            continue
                        main_game(
                            is_created_game=False,
                            game_code=join_result,
                            screen=screen,
                            font=font,
                            coin_image=assets['coin_image'],
                            fruit_image=assets['fruit_image'],
                            coin_offset=assets['coin_offset'],
                            fruit_offset=assets['fruit_offset'],
                            role=role,
                            user_id=user_id
                        )

                elif online_choice == "back":
                    break

        else:
            break

    pygame.quit()
    sys.exit()


def show_error(screen, font, message):
    """ Affiche un message d'erreur temporaire à l'écran """
    screen.fill((0, 0, 0))
    text_surface = font.render(message, True, (255, 0, 0))
    rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, rect)
    pygame.display.flip()
    pygame.time.wait(2000)  # Pause de 2 secondes


if __name__ == "__main__":
    main()
