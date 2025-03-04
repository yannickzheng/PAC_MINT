#Un item est un objet que PacMan peut ramasser.
#Il s'agit de soit d'une pièce qui augmente son score
#ou d'un super pouvoir qui lui permet de manger les fantômes pendant un certain temps.
#soit une pièce soit un super pouvoir, type : boost ou non boost (si c'est un super pouvoir alors
    #il est boost),
    #Pour le système de super pouvoir, on peut utiliser un système de tick, quand PacMan ramasse un super
    #pouvoir, on va attribuer la possibilité à pacman de manger les fantômes pendant un certain nombre de ticks
import pygame
import os
from global_variable import CELL_SIZE
from map import MAP_DATA, MAP_SURFACE

coin_size = CELL_SIZE*0.65
cherry_size = CELL_SIZE // 2

small_size = CELL_SIZE // 4

coin_image = pygame.image.load(os.path.join("images", "piece.png"))
coin_image = pygame.transform.scale(coin_image, (coin_size, coin_size))

cherry_image = pygame.image.load(os.path.join("images", "cerise.png"))
cherry_size = int(CELL_SIZE * 1.2)  #  Ajustement à 80% de la taille d'une case
cherry_image = pygame.transform.scale(cherry_image, (cherry_size, cherry_size))





class ItemManager:
    def __init__(self):
        self.coins = []
        self.cherries = []
        self.load_items()

    def load_items(self):
        """Initialise les pièces et les cerises sur la carte."""
        for y in range(len(MAP_DATA)):
            for x in range(len(MAP_DATA[y])):
                if MAP_DATA[y][x] == 2:
                    self.coins.append((x * CELL_SIZE, y * CELL_SIZE))
                elif MAP_DATA[y][x] == 4:
                    self.cherries.append((x * CELL_SIZE, y * CELL_SIZE))

    def draw_items(self, screen):
        """Affiche les pièces et les cerises sur la carte."""
        coin_offset = (CELL_SIZE - small_size) // 2
        cherry_offset = (CELL_SIZE - cherry_size) // 2  #  Ajusté pour la nouvelle taille

        for coin in self.coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))

        for cherry in self.cherries:
            screen.blit(cherry_image, (cherry[0] + cherry_offset, cherry[1] + cherry_offset))

    def check_collision(self, player):
        """Gère la collecte des pièces et des cerises uniquement pour Pac-Man."""

        #  Si le joueur est un fantôme, il ne collecte rien
        if player.is_phantom:
            return

        player_rect = pygame.Rect(
            player.x + player.size // 6,
            player.y + player.size // 6,
            player.size // 2,
            player.size // 2
        )

        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin[0], coin[1], CELL_SIZE, CELL_SIZE)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)
                player.score += 10
                MAP_DATA[coin[1] // CELL_SIZE][coin[0] // CELL_SIZE] = 0
                break

        for cherry in self.cherries[:]:
            cherry_rect = pygame.Rect(cherry[0], cherry[1], CELL_SIZE, CELL_SIZE)
            if player_rect.colliderect(cherry_rect):
                self.cherries.remove(cherry)
                player.score += 50
                MAP_DATA[cherry[1] // CELL_SIZE][cherry[0] // CELL_SIZE] = 0
