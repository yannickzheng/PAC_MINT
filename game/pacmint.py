import pygame
from global_variable import  WIDTH, HEIGHT
from reseaux import Network
from player import Player, str_to_tuple, tuple_to_str
from map import MAP_SURFACE


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")

#Permet d'avoir la map sous forme de variable globale pour les autres fichiers


def main():
    clock = pygame.time.Clock()
    n = Network()

    position_debut = str_to_tuple(n.get_pos())
    player = Player(position_debut[0], position_debut[1])
    player2 = Player(0, 0)

    run = True
    while run:
        coord_player2 = str_to_tuple(n.send(tuple_to_str((player.x, player.y))))
        player2.x = coord_player2[0]
        player2.y = coord_player2[1]
        player2.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        player.move()
        player2.move()
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        player.spawn(screen, player.get_img())
        player2.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
