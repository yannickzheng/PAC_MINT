import pygame
import random
pygame.init()

height = 800
width = 850
cell_size = 30
map_width = (width) // cell_size
map_height = height // cell_size
def create_map():
    map = [[2] * map_width for _ in range(map_height)]

    #Remplis les bords de la map
    for x in range(map_width):
        map[0][x] = 1
        map[map_height - 1][x] = 1
    for y in range(map_height):
        map[y][0] = 1
        map[y][map_width - 1] = 1
    return map


def drawing_map(screen, map):
    for y in range(map_height):
        for x in range(map_width):
            if map[y][x] == 1: #Mur
                pygame.draw.rect(screen, (192, 168, 1), (x * cell_size, y * cell_size, cell_size, cell_size))
            elif map[y][x] == 0: #Chemin
                pygame.draw.rect(screen, (100,140,140), (x * cell_size, y * cell_size, cell_size, cell_size))
            else : #Pas encore attribué
                pygame.draw.rect(screen, (0,0,0), (x * cell_size, y * cell_size, cell_size, cell_size))
#Génère le contenu du labyrinthe
def generate_map_inside(map):
    for y in range(3, 18):
        map[y][3] = 0
        map[y][3] = 0
        map[y][3] = 0
        map[y][3] = 0

    return map

screen = pygame.display.set_mode((width, height))
map = create_map()
drawing_map(screen, generate_map_inside(map))
pygame.display.flip()
while True :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


