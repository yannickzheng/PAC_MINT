import pygame
import random
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from game.player import Player, PacMan, Ghost
from game.core.assets import load_game_assets
from game.map import MAP_SURFACE, MAP_DATA
from game.ui.components import display_loading_screen, draw_button, game_over, you_win
from game.utils.helpers import distance, is_wall_at_position
from game.api import submit_score  # ✅ AJOUT

import pygame
import random
import requests  # ✅
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from game.player import Player, PacMan, Ghost
from game.core.assets import load_game_assets
from game.map import MAP_SURFACE, MAP_DATA
from game.ui.components import display_loading_screen, draw_button, game_over, you_win
from game.utils.helpers import distance, is_wall_at_position


def send_score_to_server(user_id, role, score, outcome):
    try:
        url = "http://localhost:8080/api/submit_score/"  # ✅ Corrigé ici
        payload = {
            "user_id": user_id,
            "role": role,
            "score": score,
            "outcome": outcome
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Score envoyé avec succès au serveur.")
        else:
            print(f"❌ Échec de l'envoi du score ({response.status_code}):\n{response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion au serveur: {e}")


def offline_game(screen, font, coin_image, fruit_image, coin_size, fruit_size, role, user_id=None):  # ✅ user_id
    assets = load_game_assets()
    coin_offset = assets['coin_offset']
    fruit_offset = assets['fruit_offset']
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    spawn_pos = (CELL_SIZE * 9, CELL_SIZE * 10)
    pacman = PacMan("127.0.0.1", 0, spawn_pos)
    pacman.id = "pacman"

    ghost_positions = [
        (WIDTH // 2 - 20, HEIGHT // 2 - 20),
        (WIDTH // 2 + 20, HEIGHT // 2 - 20),
        (WIDTH // 2 - 20, HEIGHT // 2 + 20),
        (WIDTH // 2 + 20, HEIGHT // 2 + 20)
    ]
    ghosts = []
    players = {"pacman": pacman}

    for i, pos in enumerate(ghost_positions):
        if not (role == "fantome" and i == 0):
            g = Ghost("127.0.0.1", 0, pos)
            g.id = f"ghost{i + 1}"
            ghosts.append(g)
            players[g.id] = g

    playerControlled = pacman if role == "pacman" else ghosts[0]

    coins = []
    fruits = []
    for y in range(len(MAP_DATA)):
        for x in range(len(MAP_DATA[y])):
            if MAP_DATA[y][x] == 2:
                coins.append((x * CELL_SIZE, y * CELL_SIZE))
            elif MAP_DATA[y][x] == 4:
                fruits.append((x * CELL_SIZE, y * CELL_SIZE))

    pygame.time.delay(500)

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if pacman.lives <= 0:
            if role == "pacman":
                game_over(playerControlled.score, screen, font)
                if user_id:
                    send_score_to_server(user_id, "Pacman", playerControlled.score, "lose")
            else:
                you_win(playerControlled.score, screen, font)
                if user_id:
                    send_score_to_server(user_id, "Fantome", playerControlled.score, "win")
            return

        if pacman.ghosts_eaten >= 15:
            if role == "pacman":
                you_win(playerControlled.score, screen, font)
                if user_id:
                    send_score_to_server(user_id, "Pacman", playerControlled.score, "win")
            else:
                game_over(playerControlled.score, screen, font)
                if user_id:
                    send_score_to_server(user_id, "Fantome", playerControlled.score, "lose")
            return

        if role == "pacman":
            playerControlled.move(players, controlled=True)
            for g in ghosts:
                g.move(players, controlled=False)
        elif role == "fantome":
            pacman.pacman_ai_move(players, coins, fruits, ghosts)
            for g in ghosts:
                g.move(players, controlled=(g is playerControlled))

        if role == "pacman":
            playerControlled.check_collision_with_items(coins, fruits)
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

        if role == "pacman":
            if playerControlled.invincible:
                playerControlled.invincibility_timer -= 1
                if playerControlled.invincibility_timer <= 0:
                    playerControlled.invincible = False
            if playerControlled.super_power_active:
                playerControlled.super_power_timer -= 1
                if playerControlled.super_power_timer <= 0:
                    playerControlled.super_power_active = False

        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))

        for coin in coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))
        for fruit in fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))

        for ghost in ghosts:
            ghost.update_eaten_state()
        if role == "fantome":
            playerControlled.update_eaten_state()

        if role == "pacman":
            playerControlled.draw(screen, controlled=True)
            for g in ghosts:
                g.draw(screen, controlled=False)
        else:
            pacman.draw(screen, controlled=True)
            for g in ghosts:
                g.draw(screen, controlled=False)
            playerControlled.draw(screen, controlled=True)

        score_text = font.render(f"Score: {playerControlled.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Vies: {playerControlled.lives}", True, (255, 255, 255))
        screen.blit(lives_text, (WIDTH - 100, 10))
        ghosts_eaten_text = font.render(f"Fantômes mangés: {pacman.ghosts_eaten}/15", True, (255, 255, 255))
        screen.blit(ghosts_eaten_text, (WIDTH - 220, 30))

        pygame.display.flip()
        clock.tick(60)

    return

