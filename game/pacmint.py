import pygame

from global_variable import WIDTH, HEIGHT, WHITE, BLUE, CYAN, PURPLE
from server.reseaux import Network
from player import Player
from map import MAP_SURFACE
from items import ItemManager
from pygame import mixer

import json

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")

font = pygame.font.SysFont("Arial", 24)

image = pygame.image.load("images/background2.png")


# musique
mixer.init()

#mixer.music.load("sound/background_sound.mp3")
mixer.music.load("sound/Rick Astley.mp3")
mixer.music.set_volume(0.10)
mixer.music.play(-1)

button_click = mixer.Sound("sound/button_click.mp3")
button_click.set_volume(5)


def draw_button(text, x, y, width, height, base_color, glow_color, screen):
    # permet de vérifier la position de la souris sur le bouton
    mouse_pos = pygame.mouse.get_pos()
    hover = (x <= mouse_pos[0] <= x + width) and (y <= mouse_pos[1] <= y + height)

    # ajout de l'effet de lumière autour du bouton
    if hover:
        for i in range(10):
            glow_radius = i * 2
            glow_surface = pygame.Surface((width + glow_radius * 2, height + glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, 50 - i * 5),
                             (0, 0, width + glow_radius * 2, height + glow_radius * 2), border_radius=10)
            screen.blit(glow_surface, (x - glow_radius, y - glow_radius))

    # dégradé de couleur du bouton
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        alpha = int(255 * (i / height))
        color = (*base_color, alpha)
        pygame.draw.line(button_surface, color, (0, i), (width, i))
    screen.blit(button_surface, (x, y))
    # ajoute un contour de lumière autour du bouton
    pygame.draw.rect(screen, glow_color, (x, y, width, height), 3, border_radius=10)
    # permet de centrer le texte dans le bouton
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def generate_code():
    pass


def create_game():
    run = True

    while run:
        screen.blit(image, (0, 0))
        draw_button("Générer un code", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Lancer la partie", 550, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 850, 600, 200, 50, BLUE, PURPLE, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # On arrête seulement la boucle, sans quitter pygame

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                button_click.play()

                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        generate_code()
                    elif 550 <= x <= 750:
                        main_game()  # Vérifier que main_game() ne ferme pas pygame
                    elif 850 <= x <= 1050:
                        main_menu()

        if not pygame.get_init():
            print("⚠ ERREUR: Pygame s'est arrêté avant l'affichage.")
            return

        pygame.display.flip()


def main_menu():
    run = True
    while run:
        screen.blit(image, (0, 0))
        draw_button("Créer une partie", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Rejoindre une partie", 550, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Quitter", 850, 600, 200, 50, BLUE, PURPLE, screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                button_click.play()
                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        create_game()
                    elif 550 <= x <= 750:
                        join_game()
                    elif 850 <= x <= 1050:
                        run = False
                        print("🔴 Pygame est en train de se fermer dans main_menu()")
                        pygame.quit()
                        sys.exit()


        pygame.display.flip()

def join_game():
    run = True
    while run:
        screen.blit(image, (0, 0))
        draw_button("Entrez le code", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 550, 600, 200, 50, BLUE, PURPLE, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                button_click.play()
                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        pass
                    elif 550 <= y <= 750:
                        main_menu()
        pygame.display.flip()

def main_game():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)

    clock = pygame.time.Clock()
    n = Network()

    # On va récupérer les données de tous les joueurs (par exemple leur position et leur rôle)
    all_players_data = json.loads(n.get_pos())
    current_player_id = all_players_data["current_player"]
    positions_and_roles = all_players_data["players"]

    # création de la liste des joueurs
    players = []
    for data in positions_and_roles:
        player = Player(data["pos"][0], data["pos"][1], data["roles"])
        players.append(player)
    # Initialisation de la police pour afficher le score
    item_manager = ItemManager()  # ✅ Création d'un objet ItemManager
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        current_player = players[current_player_id]
        current_player.move(players)
        item_manager.check_collision(current_player)  # ✅ Vérifie si Pac-Man mange une pièce

        all_players_data["players"][current_player_id] = {  # Mettre à jour les données pour tous les joueurs
            "pos": current_player.coord,
            "roles": "PacMan" if current_player.is_pacman else "Fantôme"
        }
        # mise à jour des données du joueur en local et envoie au serveur ces données pour les synchroniser avec les autres joueurs
        response = n.send(json.dumps(all_players_data))
        updated_data = json.loads(response)
        # Met à jour les positions des autres joueurs
        for i, data in enumerate(updated_data["players"]):
            if i != current_player_id:
                players[i].x, players[i].y = data["pos"]
                players[i].update()
        # Afficher la carte et les joueurs
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        item_manager.draw_items(screen)  # ✅ Appel sur l'objet créé

        for player in players:
            player.draw(screen)

        # Afficher le score du joueur actuel
        score_text = font.render(f"Score: {current_player.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        # ✅ Affichage du nombre de vies en haut à droite
        lives_text = font.render(f"Vies: {current_player.lives}", True, (0, 0, 255))
        screen.blit(lives_text, (WIDTH - 180, 1))  # 📌 Position ajustée en haut à droite

        pygame.display.flip()
        clock.tick(60)
    print("🔴 Retour au menu principal depuis main_game()")
    return  # ✅ On revient au menu sans fermer Pygame


if __name__ == "__main__":
    main_menu()

    # Mettre le graphe de nos modèles avec Django extensions
