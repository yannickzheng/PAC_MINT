import pygame
from global_variable import  WIDTH, HEIGHT
from reseaux import Network
from player import Player, str_to_tuple, tuple_to_str
from map import MAP_SURFACE


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")

#Permet d'avoir la map sous forme de variable globale pour les autres fichiers

import json
def main():
    clock = pygame.time.Clock()
    n = Network()
    all_players_data = json.loads(n.get_pos())
    current_player_id = all_players_data["current_player"]
    positions_and_roles = all_players_data["players"]


    # position_debut = str_to_tuple(n.get_pos())
    # player = Player(position_debut[0], position_debut[1])
    # player2 = Player(0, 0)

    run = True
    while run:
        # coord_player2 = str_to_tuple(n.send(tuple_to_str((player.x, player.y))))
        # player2.x = coord_player2[0]
        # player2.y = coord_player2[1]
        # player2.update()
        #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        #
        # player.move()
        # player2.move()
        # screen.fill((0, 0, 0))
        # screen.blit(MAP_SURFACE, (0, 0))
        # player.spawn(screen, player.get_img())
        # player2.draw(screen)
        # pygame.display.flip()
        # clock.tick(60)

        for player_pos_with_role in positions_and_roles:
            print(player_pos_with_role)
            player = Player(player_pos_with_role["pos"][0], player_pos_with_role["pos"][1], player_pos_with_role["roles"])
            player.move()
            print(all_players_data)
            all_players_data["players"][current_player_id] = {
                "pos": player.coord,
                "roles": "PacMan" if player.is_pacman else "Fantôme"
            }
            n.send(json.dumps(all_players_data))
            screen.fill((0, 0, 0))
            screen.blit(MAP_SURFACE, (0, 0))
            player.spawn(screen, player.get_img())
            player.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
