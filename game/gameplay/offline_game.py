import pygame
import random
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE, BLUE, CYAN
from game.player import Player, PacMan, Ghost
from game.core.assets import load_game_assets
from game.map import MAP_SURFACE, MAP_DATA
from game.ui.components import display_loading_screen, draw_button, game_over
from game.utils.helpers import distance, is_wall_at_position
import os


def offline_game(screen, font, coin_image, fruit_image, coin_size, fruit_size, role):
    """Mode de jeu hors ligne sans besoin de serveur"""
    assets = load_game_assets()
    coin_offset = assets['coin_offset']
    fruit_offset = assets['fruit_offset']

    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    # Création du joueur contrôlé (instanciation de la bonne classe)
    spawn_pos = (CELL_SIZE * 9, CELL_SIZE * 10)
    if role == "pacman":
        playerControlled = PacMan("127.0.0.1", 0, spawn_pos)
    else:
        playerControlled = Ghost("127.0.0.1", 0, spawn_pos)
    playerControlled.id = "playerControlled"

    # Création des 4 fantômes IA (autres fantômes non contrôlés par le joueur)
    ghost_positions = [
        (WIDTH // 2 - 100, HEIGHT // 2 - 100),
        (WIDTH // 2 + 100, HEIGHT // 2 - 100),
        (WIDTH // 2 - 100, HEIGHT // 2 + 100),
        (WIDTH // 2 + 100, HEIGHT // 2 + 100)
    ]
    ghosts = []
    players = {playerControlled.id: playerControlled}  # Le joueur contrôlé est 'playerControlled'
    for i, pos in enumerate(ghost_positions):
        # si le joueur contrôle un fantôme, on ne recrée pas le même
        if not (role == "fantome" and i == 0):
            g = Ghost("127.0.0.1", 0, pos)
            g.id = f"ghost{i + 1}"
            ghosts.append(g)
            players[g.id] = g

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

        # Vérifier si PacMan a perdu toutes ses vies
        if playerControlled.lives <= 0:
            game_over(playerControlled.score, screen, font)
            return

        # Déplacement du joueur (si c'est PacMan ou un fantôme, selon le rôle)
        if role == "pacman":
            playerControlled.move(players, controlled=True)  # PacMan contrôlé par l'utilisateur
        else:  # Fantôme contrôlé par l'utilisateur
            # Le joueur peut choisir un seul fantôme à contrôler
            for ghost in ghosts:
                if ghost.id == playerControlled.id:  # Si le fantôme contrôlé par l'utilisateur
                    ghost.move(players, controlled=True)
                else:
                    ghost.move(players)  # IA pour les autres fantômes

        # Vérification des collisions avec les pièces
        for coin in coins[:]:
            if distance(playerControlled.x, playerControlled.y, coin[0], coin[1]) < CELL_SIZE // 2:
                playerControlled.score += 10
                coins.remove(coin)

        # Vérification des collisions avec les fruits
        for fruit in fruits[:]:
            if distance(playerControlled.x, playerControlled.y, fruit[0], fruit[1]) < CELL_SIZE // 2:
                playerControlled.score += 50
                fruits.remove(fruit)
                # Activation du super pouvoir lors de la collecte d'un fruit
                playerControlled.activate_super_power()

        # Vérification des collisions avec les fantômes
        # Si on est en mode PacMan → collisions PacMan vs fantômes
        if role == "pacman":
            for ghost in ghosts:
                if distance(playerControlled.x, playerControlled.y, ghost.x, ghost.y) < CELL_SIZE and not playerControlled.invincible:
                    if playerControlled.super_power_active:
                        playerControlled.eat_ghost(ghost, players)
                        playerControlled.score += 200
                    else:
                        playerControlled.lose_life()
                        playerControlled.invincible = True
                        playerControlled.invincibility_timer = 180

        # Mise à jour des timers (uniquement pour PacMan)
        if role == "pacman":
            if playerControlled.invincible:
                playerControlled.invincibility_timer -= 1
                if playerControlled.invincibility_timer <= 0:
                    playerControlled.invincible = False
            if playerControlled.super_power_active:
                playerControlled.super_power_timer -= 1
                if playerControlled.super_power_timer <= 0:
                    playerControlled.super_power_active = False

        # Affichage du jeu
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))

        # Affichage des pièces et fruits
        for coin in coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))

        for fruit in fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))

        # Affichage des joueurs
        for ghost in ghosts:
            ghost.update_eaten_state()

        # 🎨 Affichage de PacMan puis de tous les fantômes
        playerControlled.draw(screen)
        for ghost in ghosts:
            ghost.draw(screen)

        # Affichage du score et des vies
        score_text = font.render(f"Score: {playerControlled.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        lives_text = font.render(f"Vies: {playerControlled.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (WIDTH - 180, 10))

        pygame.display.flip()
        clock.tick(60)

    return
