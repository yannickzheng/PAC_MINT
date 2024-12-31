from map import *
from classes.player import Player, tuple_to_str, str_to_tuple
from reseaux import Network

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("PacMint")
def main():
    clock = pygame.time.Clock()
    map = generate_map_inside(create_map())
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
        drawing_map(screen, map)
        player.draw(screen)
        player2.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()