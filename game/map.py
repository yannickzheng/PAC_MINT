from global_variable import WIDTH, HEIGHT, CELL_SIZE, MAP_WIDTH, MAP_HEIGHT, WALL_COLOR, PATH_COLOR, DEFAULT_COLOR
import pygame

def create_map():
    map = [[0] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    # Remplit les bords de la map
    for x in range(MAP_WIDTH):
        map[0][x] = 1
        map[MAP_HEIGHT - 1][x] = 1
    for y in range(MAP_HEIGHT):
        map[y][0] = 1
        map[y][MAP_WIDTH - 1] = 1
    return map

def generate_map_inside(map):
    # Génère le contenu du labyrinthe
    for y in range(3, 18):
        for x in range(3, 4):
            map[y][x] = 0
    return map

def create_map_surface(map):
    map_surface = pygame.Surface((WIDTH, HEIGHT)) # Crée une surface
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if map[y][x] == 1: # Si c'est un mur
                pygame.draw.rect(map_surface, WALL_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif map[y][x] == 0: # Si c'est un chemin
                pygame.draw.rect(map_surface, PATH_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else: # Si c'est une case non assignée
                pygame.draw.rect(map_surface, DEFAULT_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    return map_surface

MAP_SURFACE = create_map_surface(generate_map_inside(create_map()))
MAP_DATA = generate_map_inside(create_map())