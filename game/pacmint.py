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

#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
font = pygame.font.SysFont("Arial", 24)
def draw_button(text, x, y, width, height, color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surface, text_rect)


def main_menu():
    run = True
    while run:
        screen.fill(WHITE)
        draw_button("Créer une partie", 540, 200, 200, 50, GREEN)
        draw_button("Rejoindre une partie", 540, 300, 200, 50, BLUE)
        draw_button("Quitter", 540, 400, 200, 50, RED)

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
                        main_game()
                    elif 300 <= y <= 350:
                        pass
                    elif 400 <= y <= 450:
                        run = False
                        pygame.quit()
                        sys.exit()
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

        all_players_data["players"][current_player_id] = { # Mettre à jour les données pour tous les joueurs
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