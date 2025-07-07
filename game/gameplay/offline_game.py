import pygame
import random
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE, BLUE, CYAN
from game.player import Player, PacMan, Ghost
from game.core.assets import load_game_assets
from game.map import MAP_SURFACE, MAP_DATA
from game.ui.components import display_loading_screen, draw_button, game_over, you_win
from game.utils.helpers import distance, is_wall_at_position



def offline_game(screen, font, coin_image, fruit_image, coin_size, fruit_size, role):
    """Mode de jeu hors ligne sans besoin de serveur"""
    assets = load_game_assets()
    coin_offset = assets['coin_offset']
    fruit_offset = assets['fruit_offset']

    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    # ——— On instancie un seul PacMan, qu'on utilisera pour IA ou contrôle ———
    spawn_pos = (CELL_SIZE * 9, CELL_SIZE * 10)
    pacman = PacMan("127.0.0.1", 0, spawn_pos)
    pacman.id = "pacman"

    # Création des 4 fantômes IA (autres fantômes non contrôlés par le joueur)
    ghost_positions = [
        (WIDTH // 2 - 20, HEIGHT // 2 - 20),
        (WIDTH // 2 + 20, HEIGHT // 2 - 20),
        (WIDTH // 2 - 20, HEIGHT // 2 + 20),
        (WIDTH // 2 + 20, HEIGHT // 2 + 20)
    ]

    # ——— On décide quel objet est contrôlé par l'utilisateur ———
    if role == "pacman":
        playerControlled = pacman
        controlled_key = "pacman"
    else:
        ghost_spawn_pos = ghost_positions[0]
        playerControlled = Ghost("127.0.0.1", 0, ghost_spawn_pos)
        playerControlled.id = "playerControlled"
        controlled_key = "ghost_player"


    # ——— On monte le dictionnaire de tous les joueurs ———
    players = {
        "pacman": pacman,
        controlled_key: playerControlled
    }
    # Si on contrôle PacMan, players contient deux fois la même référence : c'est ok


    ghosts = []
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
        if pacman.lives <= 0:
            if role == "pacman":
                game_over(playerControlled.score, screen, font)
            else:
                you_win(playerControlled.score, screen, font)
            return

        # Déplacement du joueur (si c'est PacMan ou un fantôme, selon le rôle)
        if role == "pacman":
            playerControlled.move(players, controlled=True)  # PacMan contrôlé par l'utilisateur
            for g in ghosts:
                g.move(players, controlled=False)
        else:
            # 1) PacMan IA
            pacman.pacman_ai_move(players, coins, fruits, ghosts)
            # 2) On déplace les fantômes
            for g in ghosts:
                g.move(players, controlled=False)
            playerControlled.move(players, controlled=True)

        # Vérification des collisions
        if role == "pacman":
            # 1) COLLISIONS PACMAN vs COINS & FRUITS
            playerControlled.check_collision_with_items(coins, fruits)
            # 2) COLLISIONS PACMAN <=> FANTOMES
            playerControlled.check_collision_with_ghosts(ghosts, players)

        elif role == "fantome":
            pacman.check_collision_with_ghosts(ghosts, players)
            pacman.check_collision_with_items(coins, fruits)
            playerControlled.check_collision_with_pacman(pacman, players)
            if pacman.invincible:
                pacman.invincibility_timer -= 1
                if pacman.invincibility_timer <= 0:
                    pacman.invincible = False
            if pacman.super_power_active:
                pacman.super_power_timer -= 1
                if pacman.super_power_timer <= 0:
                    pacman.super_power_active = False

        # Mise à jour des timers
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
        if role == "fantome":
            playerControlled.update_eaten_state()

        # Affichage de PacMan puis de tous les fantômes
        if role == "pacman":
            # 1) PacMan contrôlé
            playerControlled.draw(screen, controlled=True)

            # 2) Les 4 fantômes (IA)
            for g in ghosts:
                g.draw(screen, controlled=False)
        else:
          # 1) PacMan en IA
            pacman.draw(screen, controlled=True)
          # 2) Les fantômes IA
            for g in ghosts:
                g.draw(screen, controlled=False)
          # 3) Le fantôme contrôlé
            playerControlled.draw(screen, controlled=True)

        # Affichage du score et des vies
        score_text = font.render(f"Score: {playerControlled.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        lives_text = font.render(f"Vies: {playerControlled.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (WIDTH - 180, 10))

        pygame.display.flip()
        clock.tick(60)

    return
