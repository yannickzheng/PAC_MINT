from map import *
from classes.player import Player

def main ():
    player = Player(60,60)
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("PacMint")
    clock = pygame.time.Clock()
    map = create_map()
    map = generate_map_inside(map)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        player.move()
        screen.fill((0,0,0))
        drawing_map(screen, map)
        player.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    
if __name__ == "__main__":
    main()
