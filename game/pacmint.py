import pygame

from common.global_variable import WIDTH, HEIGHT, WHITE, BLUE, CYAN, PURPLE
from common.network import Network
from player import Player
from map import MAP_SURFACE
# from pygame import mixer

from common.protocols import Protocols

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

music_on = True
music_loaded = None

def init_music():
    global music_loaded
    if not pygame.mixer.get_init():
        mixer.init()
    mixer.music.set_volume(0.9)
    music_loaded = None

def play_music(path, volume=0.9):
    global music_loaded
    if music_loaded != path:
        mixer.music.load(path)
        music_loaded = path
    mixer.music.set_volume(volume)
    mixer.music.play(-1)
    if not music_on:
        mixer.music.pause()

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        mixer.music.unpause()
    else:
        mixer.music.pause()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")
font = pygame.font.SysFont("Arial", 24)
image = pygame.image.load("images/background2.png")

# musique
# mixer.init()

# mixer.music.load("sound/background_sound.mp3")
# mixer.music.set_volume(0.9)
# mixer.music.play(-1)
#
# button_click = mixer.Sound("sound/button_click.mp3")
# button_click.set_volume(-10)

init_music()
play_music("sound/background_sound.mp3", 0.9)

#image
from common.global_variable import CELL_SIZE

small_size = CELL_SIZE // 4  # Taille des pièces
cherry_size = CELL_SIZE // 2  #  Augmente la taille des cerises

coin_size = CELL_SIZE*0.65
fruit_size = CELL_SIZE // 2

coin_offset = (CELL_SIZE - small_size) // 2
fruit_offset = (CELL_SIZE - fruit_size) // 2  #  Ajusté pour la nouvelle taille

small_size = CELL_SIZE // 4

coin_image = pygame.image.load(os.path.join("images", "piece.png"))
coin_image = pygame.transform.scale(coin_image, (coin_size, coin_size))

fruit_image = pygame.image.load(os.path.join("images", "fraise.png"))
fruit_size = int(CELL_SIZE * 1.2)  #  Ajustement à 80% de la taille d'une case
fruit_image = pygame.transform.scale(fruit_image, (fruit_size, fruit_size))


def draw_button(text, x, y, width, height, base_color, glow_color, screen):
    # permet de vérifier la position de la souris sur le bouton
    mouse_pos = pygame.mouse.get_pos()
    hover = (x <= mouse_pos[0] <= x + width) and (y <= mouse_pos[1] <= y + height)

    # ajout de l'effet de lumière autour du bouton
    if hover:
        for i in range(10):
            glow_radius = i * 2
            glow_surface = pygame.Surface((width + glow_radius * 2, height + glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, 50 - i * 5),
                             (0, 0, width + glow_radius * 2, height + glow_radius * 2), border_radius=10)
            screen.blit(glow_surface, (x - glow_radius, y - glow_radius))

    # dégradé de couleur du bouton
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        alpha = int(255 * (i / height))
        color = (*base_color, alpha)
        pygame.draw.line(button_surface, color, (0, i), (width, i))
    screen.blit(button_surface, (x, y))
    # ajoute un contour de lumière autour du bouton
    pygame.draw.rect(screen, glow_color, (x, y, width, height), 3, border_radius=10)
    # permet de centrer le texte dans le bouton
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)


def create_game():
    game_code = None
    run = True

    while run:
        screen.blit(image, (0, 0))
        #draw_button("Générer un code", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Lancer la partie", 550, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 850, 600, 200, 50, BLUE, PURPLE, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # button_click.play()
                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        #Pas d'interet
                        game_code = None # Génération d'un code
                    elif 550 <= x <= 750:
                        #On lance la partie ici
                        #Le client demande au serveur de créer un code de partie, le serveur crée un code et l'envoit au client
                        main_game(is_created_game=True)

                    elif 850 <= x <= 1050:
                        main_menu()
        pygame.display.flip()


def main_menu():
    global music_on
    play_music("sound/background_sound.mp3", 0.9)
    if not music_on:
        mixer.music.pause()
    run = True
    while run:
        screen.blit(image, (0, 0))
        draw_button("Créer une partie", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Rejoindre une partie", 550, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Quitter", 850, 600, 200, 50, BLUE, PURPLE, screen)
        # bouton musique
        music_text = "Musique : ON" if music_on else "Musique : OFF"
        draw_button(music_text, 1050, 10, 180, 40, BLUE, CYAN, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # button_click.play()
                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        create_game()
                    elif 550 <= x <= 750:
                        join_game()
                    elif 850 <= x <= 1050:
                        run = False
                        pygame.quit()
                        sys.exit()
                # Gestion du bouton musique ---
                if 10 <= y <= 50 and 1050 <= x <= 1230:
                    toggle_music()
        pygame.display.flip()

def lobby():
    pass

def join_game():
    run = True
    game_code = ""
    input_active = False
    input_box = pygame.Rect(250, 600, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = BLUE

    while run:
        screen.blit(image, (0, 0))

        draw_button("Rejoindre", 550, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 850, 600, 200, 50, BLUE, PURPLE, screen)

        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(game_code, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # button_click.play()
                if input_box.collidepoint(event.pos):
                    input_active = not input_active
                else:
                    input_active = False
                color = color_active if input_active else color_inactive

                if 600 <= y <= 650:
                    if 550 <= x <= 750 and game_code:
                        main_game(is_created_game=False, game_code=game_code)
                        return game_code  # Retourne le code saisi
                    elif 850 <= x <= 1050:
                        main_menu()

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    main_game(is_created_game = False,game_code = game_code)
                    return game_code
                elif event.key == pygame.K_BACKSPACE:
                    game_code = game_code[:-1]
                else:
                    game_code += event.unicode

        pygame.display.flip()

def main_game(is_created_game, game_code = None):
    # mixer.init()
    # mixer.music.load("sound/game_sound.mp3")
    # mixer.music.set_volume(0.3)
    # mixer.music.play(-1)
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)

    clock = pygame.time.Clock()

    n = Network()

    if not is_created_game:

        response = n.send_command(Protocols.Request.JOIN_ROOM, game_code)
        print(response)
    #Si le joueur souhaite créer une partie, il envoie une demande au serveur
    if is_created_game:
        # Le client demande la création d'une partie au serveur
        print("Game started")
        response = n.send_command(Protocols.Request.CREATE_GAME)
        game_code = response.get("code", "")
        print(f"Code de la partie créée : {game_code}")

    # Le serveur envoie les positions initiales à chaque joueur
    #welcome = n.receive_j()
    welcome = n.receive_json()
    print("WELCOME reçu:", welcome)
    all_players_data = welcome
    print("fin")
    print("Joueurs récupérés :", all_players_data["players"])

    # création de la liste des joueurs
    players = {}
    current_player_id = all_players_data["current_player_id"]

    #On crée des classes pour chaque joueur en local
    for data in all_players_data["players"]:
        player = Player(ip=data["ip"], tcp_port=data["tcp_port"], role=data["roles"], position=tuple(data["pos"]))
        player.id = data["id"]
        player.score = data.get("score", 0)
        player.lives = data.get("lives", 3)
        players[player.id] = player

    coins = all_players_data.get("items", {}).get("coins", [])
    fruits = all_players_data.get("items", {}).get("fruits", [])

    run = True    #Boucle principale du jeu
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 10 <= y <= 50 and 1050 <= x <= 1230:
                    toggle_music()

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        current_player = players.get(current_player_id)
        current_player.move(players, controlled=True)

        # Envoie les nouvelles positions au serveur
        payload = {
            "players": [
                {
                    "id": current_player.id,
                    "pos": current_player.coord
                }
            ]
        }
        
        response = n.send_command(Protocols.Request.UPDATE_POSITION, payload)
        
        # Synchroniser l'état du jeu avec les données du serveur
        update_game_state_from_server(response, players, current_player_id, coins, fruits)
        
        # Afficher la carte et les joueurs
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        for coin in coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))

        for fruit in fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))

        #On affiche sur l'interface l'ensemble des joueurs
        for player in players.values():
            player.draw(screen, player)

        # Affiche le code de la partie sous le score
        game_code_text = font.render(f"Code de la partie: {game_code}", True, (255, 255, 0))
        screen.blit(game_code_text, (10, 40))

        # Afficher le score du joueur actuel
        score_text = font.render(f"Score: {current_player.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Vies: {current_player.lives}", True, (0, 0, 255))
        screen.blit(lives_text, (WIDTH - 180, 1))

        # Affiche le bouton musique en haut à droite
        music_text = "Musique : ON" if music_on else "Musique : OFF"
        draw_button(music_text, 1050, 10, 180, 40, BLUE, CYAN, screen)

        pygame.display.flip()
        clock.tick(60)
    return

def update_game_state_from_server(state, players, current_player_id, coins, fruits):
    """Synchronise l'état local du jeu avec les données du serveur"""
    # Mise à jour des items du jeu
    if state.get("action") == "welcome":
        coins[:] = state.get("items", {}).get("coins", [])
        fruits[:] = state.get("items", {}).get("fruits", [])
    elif state.get("items"):
        # Mise à jour des items (coins/fruits)
        if "coins" in state["items"]:
            coins[:] = state["items"]["coins"]
        if "fruits" in state["items"]:
            fruits[:] = state["items"]["fruits"]
    
    # Mise à jour des joueurs
    for data in state.get("players", []):
        pid = data["id"]
        if pid == current_player_id:
            # Notre joueur
            current_player = players[pid]
            current_player.score = data["score"]
            current_player.lives = data.get("lives", current_player.lives)
            current_player.invincible = data.get("invincible", False)
            if data.get("activate_super_power"):
                current_player.activate_super_power()
        elif pid in players:
            # Joueur existant
            players[pid].update_position(tuple(data["pos"]))
            players[pid].score = data.get("score", 0)
            players[pid].lives = data.get("lives", 3)
            players[pid].invincible = data.get("invincible", False)
        else:
            # Nouveau joueur
            new_player = Player(
                ip=data["ip"],
                tcp_port=data["tcp_port"],
                role=data["roles"],
                position=tuple(data["pos"])
            )
            new_player.id = pid
            new_player.score = data.get("score", 0)
            new_player.lives = data.get("lives", 3)
            new_player.invincible = data.get("invincible", False)
            players[pid] = new_player
            print(f"[CLIENT] Nouveau joueur ajouté : {pid}")

if __name__ == "__main__":
    main_menu()