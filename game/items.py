
#Un item est un objet que PacMan peut ramasser.
#Il s'agit de soit d'une pièce qui augmente son score
#ou d'un super pouvoir qui lui permet de manger les fantômes pendant un certain temps.
#soit une pièce soit un super pouvoir, type : boost ou non boost (si c'est un super pouvoir alors
    #il est boost),
    #Pour le système de super pouvoir, on peut utiliser un système de tick, quand PacMan ramasse un super
    #pouvoir, on va attribuer la possibilité à pacman de manger les fantômes pendant un certain nombre de ticks

import pygame
import os
from common.global_variable import CELL_SIZE
from game.map import MAP_DATA

small_size = CELL_SIZE // 4  # Taille des pièces
cherry_size = CELL_SIZE // 2  #  Augmente la taille des cerises

coin_size = CELL_SIZE*0.65
fruit_size = CELL_SIZE // 2

small_size = CELL_SIZE // 4

coin_image = pygame.image.load(os.path.join("images", "piece.png"))
coin_image = pygame.transform.scale(coin_image, (coin_size, coin_size))

fruit_image = pygame.image.load(os.path.join("images", "fraise.png"))
fruit_size = int(CELL_SIZE * 1.2)  #  Ajustement à 80% de la taille d'une case
fruit_image = pygame.transform.scale(fruit_image, (fruit_size, fruit_size))

class ServerItemManager:
    def __init__(self):
        self.coins = []
        self.fruits = []
        self.load_items()

    def load_items(self):
        for y in range(len(MAP_DATA)):
            for x in range(len(MAP_DATA[y])):
                if MAP_DATA[y][x] == 2:
                    self.coins.append((x * CELL_SIZE, y * CELL_SIZE))
                elif MAP_DATA[y][x] == 4:
                    self.fruits.append((x * CELL_SIZE, y * CELL_SIZE))

    def check_collision(self, player):
        px, py = player.position
        size = CELL_SIZE // 2

        collected = {"coins": [], "fruits": []}

        player_rect = (px + size // 2, py + size // 2, size, size)

        def rects_overlap(a, b):
            return (a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and
                    a[1] < b[1] + b[3] and a[1] + a[3] > b[1])

        for coin in self.coins[:]:
            coin_rect = (coin[0], coin[1], CELL_SIZE, CELL_SIZE)
            if rects_overlap(player_rect, coin_rect):
                self.coins.remove(coin)
                collected["coins"].append(coin)

        for fruit in self.fruits[:]:
            fruit_rect = (fruit[0], fruit[1], CELL_SIZE, CELL_SIZE)
            if rects_overlap(player_rect, fruit_rect):
                self.fruits.remove(fruit)
                collected["fruits"].append(fruit)

        return collected