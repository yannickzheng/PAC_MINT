import pygame
from map import *
from classes.player import Player, convert_pos_to_str, convert_str_to_pos
from reseaux import Network

def main():
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("PacMint")
    clock = pygame.time.Clock()
    map = create_map()
    map = generate_map_inside(map)
    run = True
    n = Network()
    position_debut = convert_str_to_pos(n.get_pos())

    player = Player(position_debut[0], position_debut[1])
    player2 = Player(0, 0)
    while run:
        coord_player2 = convert_str_to_pos(n.send(convert_pos_to_str((player.x, player.y))))
        player2.x = coord_player2[0]
        player2.y = coord_player2[1]
        player2.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        try:
            player.move()
            player2.move()
            screen.fill((0, 0, 0))
            drawing_map(screen, map)
            player.draw(screen)
            pygame.display.flip()
            clock.tick(60)
        except Exception as e:
            print(f"Error during player movement or drawing: {e}")
            run = False
    pygame.quit()

if __name__ == "__main__":
    main()