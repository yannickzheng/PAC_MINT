import pygame
import random
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE, BLUE, CYAN
from game.player import Player
from game.map import MAP_SURFACE, MAP_DATA
from game.ui.components import display_loading_screen, draw_button, game_over
from game.utils.helpers import distance, is_wall_at_position
import os

def offline_game(screen, font, coin_image, fruit_image, coin_size, fruit_size):
    """Mode de jeu hors ligne sans besoin de serveur"""
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()
    
    # Calculer les offsets identiques à la version online
    coin_offset = (CELL_SIZE - coin_size) // 2
    fruit_offset = (CELL_SIZE - fruit_size) // 2
    
    display_loading_screen("Préparation du jeu hors ligne...", screen, font)
    
    # Création d'un joueur Pacman pour le mode hors ligne
    pacman = Player("127.0.0.1", 0, "PacMan", (WIDTH // 2, HEIGHT // 2))
    pacman.id = "player1"
    pacman.lives = 3
    pacman.score = 0
    
    # Création d'un fantôme contrôlé par l'IA
    ghost_positions = [
        (WIDTH // 2 - 100, HEIGHT // 2 - 100),
        (WIDTH // 2 + 100, HEIGHT // 2 - 100),
        (WIDTH // 2 - 100, HEIGHT // 2 + 100),
        (WIDTH // 2 + 100, HEIGHT // 2 + 100)
    ]
    ghosts = []
    players = {pacman.id: pacman}
    for i, pos in enumerate(ghost_positions):
        ghost = Player("127.0.0.1", 0, "Fantôme", pos)
        ghost.id = f"ghost{i + 1}"
        ghosts.append(ghost)
        players[ghost.id] = ghost
    
    # Génération des pièces et fruits pour le mode hors ligne identique au serveur
    coins = []
    fruits = []
    for y in range(len(MAP_DATA)):
        for x in range(len(MAP_DATA[y])):
            if MAP_DATA[y][x] == 2:
                coins.append((x * CELL_SIZE, y * CELL_SIZE))
            elif MAP_DATA[y][x] == 4:
                fruits.append((x * CELL_SIZE, y * CELL_SIZE))
    
    pygame.time.delay(500)  # Petit délai pour l'affichage de l'écran de chargement
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # Vérifier si Pacman a perdu toutes ses vies
        if pacman.lives <= 0:
            game_over(pacman.score, screen, font)
            return
        
        # Déplacement du joueur Pacman
        pacman.move(players, controlled=True)

        # Tous les fantômes utilisent leur IA intégrée
        for ghost in ghosts:
            ghost.move(players)
        
        # Vérification des collisions avec les pièces
        for coin in coins[:]:
            if distance(pacman.x, pacman.y, coin[0], coin[1]) < CELL_SIZE // 2:
                pacman.score += 10
                coins.remove(coin)
        
        # Vérification des collisions avec les fruits
        for fruit in fruits[:]:
            if distance(pacman.x, pacman.y, fruit[0], fruit[1]) < CELL_SIZE // 2:
                pacman.score += 50
                fruits.remove(fruit)
                # Activation du super pouvoir lors de la collecte d'un fruit
                pacman.activate_super_power()
        
        # Vérification des collisions avec les fantômes
        if distance(pacman.x, pacman.y, ghost.x, ghost.y) < CELL_SIZE and not pacman.invincible:
            if pacman.super_power_active:
                # Le fantôme retourne à sa position de départ
                ghost.x, ghost.y = WIDTH//2 - 100, HEIGHT//2 - 100
                pacman.score += 200
            else:
                # Pacman perd une vie
                pacman.lose_life()
                pacman.invincible = True
                pacman.invincibility_timer = 180  # 3 secondes d'invincibilité
        
        # Mise à jour des timers
        if pacman.invincible:
            pacman.invincibility_timer -= 1
            if pacman.invincibility_timer <= 0:
                pacman.invincible = False
        
        if pacman.super_power_active:
            pacman.super_power_timer -= 1
            if pacman.super_power_timer <= 0:
                pacman.super_power_active = False
        
        # Affichage du jeu
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        
        # Affichage des pièces et fruits
        for coin in coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))
        
        for fruit in fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))
        
        # Affichage des joueurs
        for player in players.values():
            player.draw(screen, pacman)
        
        # Affichage du score et des vies
        score_text = font.render(f"Score: {pacman.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        lives_text = font.render(f"Vies: {pacman.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (WIDTH - 180, 10))
        


        pygame.display.flip()
        clock.tick(60)
    
    return
