from common.global_variable import WIDTH, HEIGHT, CELL_SIZE, MAP_WIDTH, MAP_HEIGHT, WALL_COLOR, PATH_COLOR, DEFAULT_COLOR
import pygame
import random

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

#  fonction pour générer des murs continus dans la map

def generate_map_walls(map):
    # Génération de plusieurs murs continus tout en laissant des ouvertures
    for y in range(5, 30):
        if y != 17:
            map[y][10] = 1  # Mur vertical avec ouverture

    for x in range(10, 50):
        if x != 30:
            map[15][x] = 1  # Mur horizontal avec ouverture

    for y in range(10, 25):
        if y != 18:
            map[y][30] = 1  # Mur vertical avec ouverture

    for x in range(5, 40):
        if x != 20:
            map[5][x] = 1  # Mur horizontal avec ouverture

    for y in range(20, 35):
        if y != 28:
            map[y][50] = 1  # Mur vertical avec ouverture

    for x in range(20, 60):
        if x != 45:
            map[25][x] = 1  # Mur horizontal avec ouverture

    for y in range(5, 20):
        if y != 12:
            map[y][60] = 1  # Mur vertical avec ouverture

    for x in range(15, 55):
        if x != 35:
            map[10][x] = 1  # Mur horizontal avec ouverture

    for y in range(8, 28):
        if y != 22:
            map[y][40] = 1  # Mur vertical avec ouverture

    for x in range(10, 45):
        if x != 25:
            map[30][x] = 1  # Mur horizontal avec ouverture

    for y in range(12, 34):
        if y != 27:
            map[y][20] = 1  # Mur vertical avec ouverture

    return map

def generate_items(map):
    """Ajoute des pièces (2) et des fruits (4) sur les chemins de la carte."""
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x] == 0:  # On place des objets seulement sur les chemins
                if random.random() < 0.01:  # 1% de chance de générer une cerise
                    map[y][x] = 4
                else:
                    map[y][x] = 2  # Sinon on place une pièce par défaut
    return map



MAP_SURFACE = create_map_surface((generate_map_walls(generate_map_inside(create_map()))))
MAP_DATA = generate_items(generate_map_walls(generate_map_inside(create_map())))
