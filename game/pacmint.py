import pygame

try:
    pygame.mixer.init()
except pygame.error:
    pass

from common.global_variable import WIDTH, HEIGHT, WHITE, BLUE, CYAN, PURPLE
from common.reseaux import Network
from player import Player
from map import MAP_SURFACE
from items import ItemManager
from pygame import mixer

import json

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PacMint")

font = pygame.font.SysFont("Arial", 24)

image = pygame.image.load("images/background2.png")

# musique
mixer.init()

mixer.music.load("sound/background_sound.mp3")
mixer.music.set_volume(0.9)
mixer.music.play(-1)

button_click = mixer.Sound("sound/button_click.mp3")
button_click.set_volume(5)


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


def generate_code():
    """Génère un code pour la partie"""
    n = Network()
    code = n.create_party()
    print(f"Code généré : {code}")
    return code

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
                button_click.play()
                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        #Pas d'interet
                        game_code = None # Génération d'un code
                    elif 550 <= x <= 750:
                        main_game(game_code)  # On lance une partie si un code a été généré

                    elif 850 <= x <= 1050:
                        main_menu()
        pygame.display.flip()


def main_menu():
    run = True
    while run:
        screen.blit(image, (0, 0))
        draw_button("Créer une partie", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Rejoindre une partie", 550, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Quitter", 850, 600, 200, 50, BLUE, PURPLE, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                button_click.play()
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
        pygame.display.flip()

def lobby():
    pass
def join_game():
    run = True
    while run:
        screen.blit(image, (0, 0))
        #game_code = "0399"
        #draw_button(f"Code: {game_code}", 250, 500, 400, 50, BLUE, CYAN, screen)
        draw_button("Rejoindre", 250, 600, 200, 50, BLUE, CYAN, screen)
        draw_button("Retour", 550, 600, 200, 50, BLUE, PURPLE, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                button_click.play()
                # Vérifier si un bouton est cliqué
                if 600 <= y <= 650:
                    if 250 <= x <= 450:
                        pass
                    elif 550 <= y <= 750:
                        main_menu()
        pygame.display.flip()

def main_game(game_code):
    print("Début de la fonction main_game()")

    mixer.init()

    mixer.music.load("sound/game_sound.mp3")
    mixer.music.set_volume(0.3)
    mixer.music.play(-1)
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)

    clock = pygame.time.Clock()

    n = Network()
    print("Connexion au serveur...")


    # Demander à l'utilisateur de créer ou rejoindre une partie
    game_code = n.create_party()
    print(f"Partie créée avec le code : {game_code}")

    """
    game_code = input("Entrez le code de la partie : ").strip().upper()
    if not n.join_party(game_code):
        print("Impossible de rejoindre la partie. Vérifiez le code.")
        return
    """

    # On va récupérer les données de tous les joueurs (par exemple leur position et leur rôle)
    print("demande position serveur")
    all_players_data = n.get_pos()
    print("Joueurs récupérés :", all_players_data)
    current_player_adresse = all_players_data["current_player"] # on récupère l'ip et le port tcp du joueur courant
    positions_and_roles = all_players_data["players"]

    # création de la liste des joueurs
    players = []
    for data in positions_and_roles:
        player = Player(data["pos"][0], data["pos"][1], data["roles"], data["ip"], data["tcp_port"])
        players.append(player)

    # Initialisation de la police pour afficher le score
    item_manager = ItemManager()
    run = True

    #Boucle principale du jeu
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        current_player = None
        for player in players:
            if player.ip == current_player_adresse[0] and player.tcp_port == current_player_adresse[1]:
                current_player = player
                break

        current_player.move(players)
        item_manager.check_collision(current_player)
        ###
        all_players_data["players"][0] = {  # Mettre à jour les données pour tous les joueurs ici on suppose que le joueur actuel est pacman
            "pos": current_player.coord,
            "roles": "PacMan" if current_player.is_pacman else "Fantôme"
        }
        # mise à jour des données du joueur en local et envoie au serveur ces données pour les synchroniser avec les autres joueurs
        response = n.send(json.dumps(all_players_data))
        updated_data = json.loads(response)["players"] # Format étrange ici
        # Met à jour les positions des autres joueurs
        for data in updated_data:
            # Chercher le joueur correspondant dans la liste des joueurs en fonction de l'IP et du port TCP
            if data["roles"] == "PacMan":
                for player in players:
                    if player.is_pacman:
                        # Mettre à jour la position du joueur
                        #player.x, player.y = data["pos"]
                        # Effectuer toute autre mise à jour relevant
                        #player.update()
                        pass

        # Afficher la carte et les joueurs
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        item_manager.draw_items(screen)

        for player in players:
            #Problème d'affiche, Pacman est affiché deux fois
            player.draw(screen, current_player)

        # Affiche le code de la partie sous le score
        game_code_text = font.render(f"Code de la partie: {game_code}", True, (255, 255, 0))
        screen.blit(game_code_text, (10, 40))

        # Afficher le score du joueur actuel
        score_text = font.render(f"Score: {current_player.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Vies: {current_player.lives}", True, (0, 0, 255))
        screen.blit(lives_text, (WIDTH - 180, 1))

        pygame.display.flip()
        clock.tick(60)
    return

if __name__ == "__main__":
    main_menu()

    # Mettre le graphe de nos modèles avec Django extensions