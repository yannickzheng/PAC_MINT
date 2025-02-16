import pygame

from global_variable import WIDTH, HEIGHT
from server.reseaux import Network
from player import Player
from map import MAP_SURFACE
import json

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 255)
font = pygame.font.SysFont("Arial", 24)

image = pygame.image.load("images/background2.png")


def draw_button(text, x, y, width, height, base_color, glow_color, screen):
    """
    Dessine un bouton futuriste avec un effet de lumière et un dégradé.
    :param text: Texte du bouton
    :param x: Position x du bouton
    :param y: Position y du bouton
    :param width: Largeur du bouton
    :param height: Hauteur du bouton
    :param base_color: Couleur de base du bouton
    :param glow_color: Couleur de la lumière autour du bouton
    :param screen: Surface Pygame où dessiner le bouton
    """
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
    screen.fill((172, 172, 0))
    active = False
    run = True
    user_text = ""
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    # def draw_button(text, x, y, width, height, base_color, glow_color, screen):
    while run:
        screen.blit(image, (0, 0))
        draw_button("Générer un code", 540, 200, 200, 50, BLUE, CYAN, screen)
        draw_button("Entrez un code ", 540, 300, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 540, 400, 200, 50, BLUE, PURPLE, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(100, 100, 140, 32).collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        print(user_text)
                        user_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Vérifier si un bouton est cliqué
                if 540 <= x <= 740:
                    if 200 <= y <= 250:
                        generate_code()
                    elif 300 <= y <= 350:
                        pass
                    elif 400 <= y <= 450:
                        main_menu()
        # pygame.draw.rect(screen, color, (100, 100, 140, 32))
        # text_surface = font.render(user_text, True, (255, 255, 255))
        # screen.blit(text_surface, (100, 100))

        pygame.display.flip()


def main_menu():
    run = True
    while run:
        screen.blit(image, (0, 0))
        draw_button("Créer une partie", 540, 200, 200, 50, BLUE, CYAN, screen)
        draw_button("Rejoindre une partie", 540, 300, 200, 50, BLUE, CYAN, screen)
        draw_button("Quitter", 540, 400, 200, 50, BLUE, PURPLE, screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Vérifier si un bouton est cliqué
                if 540 <= x <= 740:
                    if 200 <= y <= 250:
                        create_game()
                    elif 300 <= y <= 350:
                        join_game()
                    elif 400 <= y <= 450:
                        run = False
                        pygame.quit()
                        sys.exit()
        pygame.display.flip()


def join_game():
    run = True
    while run:
        screen.blit(image, (0, 0))
        draw_button("Entrez le code", 540, 200, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 540, 300, 200, 50, BLUE, PURPLE, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Vérifier si un bouton est cliqué
                if 540 <= x <= 740:
                    if 200 <= y <= 250:
                        pass
                    elif 300 <= y <= 350:
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
    run = True
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        current_player = players[current_player_id]
        current_player.move(players)

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
        for player in players:
            player.draw(screen)

        # Afficher le score du joueur actuel
        score_text = font.render(f"Score: {current_player.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main_menu()

    # Mettre le graphe de nos modèles avec Django extensions
