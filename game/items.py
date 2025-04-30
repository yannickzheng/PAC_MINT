import pygame
import os
import sys

from common.global_variable import CELL_SIZE
from map import MAP_DATA



def resource_path(relative_path): #dupliqué car pas envie de faire un import circulaire
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


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





class ItemManager:
    def __init__(self):
        self.coins = []
        self.fruits = []
        self.load_items()

    def load_items(self):
        """Initialise les pièces et les cerises sur la carte."""
        for y in range(len(MAP_DATA)):
            for x in range(len(MAP_DATA[y])):
                if MAP_DATA[y][x] == 2:
                    self.coins.append((x * CELL_SIZE, y * CELL_SIZE))
                elif MAP_DATA[y][x] == 4:
                    self.fruits.append((x * CELL_SIZE, y * CELL_SIZE))

    def draw_items(self, screen):
        """Affiche les pièces et les cerises sur la carte."""
        coin_offset = (CELL_SIZE - small_size) // 2
        fruit_offset = (CELL_SIZE - fruit_size) // 2  #  Ajusté pour la nouvelle taille

        for coin in self.coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))

        for fruit in self.fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))

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

        for fruit in self.fruits[:]:
            fruit_rect = pygame.Rect(fruit[0], fruit[1], CELL_SIZE, CELL_SIZE)
            if player_rect.colliderect(fruit_rect):
                self.fruits.remove(fruit)  #  Supprime le fruit immédiatement
                player.score += 50  # Pac-Man gagne 50 points
                player.activate_super_power()  # ACTIVE DIRECTEMENT LE SUPER POUVOIR
                MAP_DATA[fruit[1] // CELL_SIZE][fruit[0] // CELL_SIZE] = 0


