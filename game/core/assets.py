import pygame
import os
from common.global_variable import CELL_SIZE

def load_game_assets():
    """Charge toutes les ressources du jeu"""
    # Images des pièces et fruits
    coin_size = int(CELL_SIZE * 0.65)
    fruit_size = int(CELL_SIZE)

    coin_offset = (CELL_SIZE - coin_size) // 2
    fruit_offset = (CELL_SIZE - fruit_size) // 2
    
    coin_image = pygame.image.load(os.path.join("images", "piece.png"))
    coin_image = pygame.transform.scale(coin_image, (coin_size, coin_size))
    
    fruit_image = pygame.image.load(os.path.join("images", "fraise.png"))
    fruit_image = pygame.transform.scale(fruit_image, (fruit_size, fruit_size))
    
    # Image de fond
    background_image = pygame.image.load("images/background2.png")
    
    return {
        'coin_image': coin_image,
        'fruit_image': fruit_image,
        'coin_size': coin_size,
        'fruit_size': fruit_size,
        'coin_offset': coin_offset,
        'fruit_offset': fruit_offset,
        'background_image': background_image
    }
