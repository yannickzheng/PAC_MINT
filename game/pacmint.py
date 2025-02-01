import pygame
from global_variable import WIDTH, HEIGHT
from reseaux import Network
from player import Player, str_to_tuple, tuple_to_str
from map import MAP_SURFACE
import json

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")

def main():
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

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        current_player = players[current_player_id]
        current_player.move()

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



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
