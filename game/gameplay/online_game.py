import pygame
import sys
from common.global_variable import WIDTH, BLUE, CYAN
from common.network import Network
from common.protocols import Protocols
from game.player_online import Player
from game.map import MAP_SURFACE
from game.ui.chat_box import ChatBox
from game.ui.components import display_loading_screen, draw_button, game_over

def update_game_state_from_server(state, players, current_player_id, coins, fruits, chat_box=None):
    """Synchronise l'état local du jeu avec les données du serveur"""
    # Gestion des messages de chat
    if state.get("action") == "chat_message" and chat_box:
        chat_message = state.get("chat_message")
        if chat_message:
            chat_box.add_message(
                chat_message["player_name"],
                chat_message["message"],
                chat_message["timestamp"]
            )
        return
    
    # Mise à jour des items du jeu
    if state.get("action") == "welcome":
        coins[:] = state.get("items", {}).get("coins", [])
        fruits[:] = state.get("items", {}).get("fruits", [])
        # Charger l'historique du chat si disponible
        if chat_box and state.get("chat_history"):
            chat_box.messages = []  # Vider les messages existants
            for msg in state.get("chat_history", []):
                chat_box.add_message(
                    msg["player_name"],
                    msg["message"],
                    msg["timestamp"]
                )
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
            current_player.super_power_active = data.get("super_power_active", False)
            current_player.super_power_timer = data.get("super_power_timer", 0)
            if data.get("activate_super_power"):
                print(f"[CLIENT] Activation du super pouvoir reçue pour le joueur {pid}")
                current_player.activate_super_power()
        elif pid in players:
            # Joueur existant
            players[pid].update_position(tuple(data["pos"]))
            players[pid].score = data.get("score", 0)
            players[pid].lives = data.get("lives", 3)
            players[pid].invincible = data.get("invincible", False)
            players[pid].super_power_active = data.get("super_power_active", False)
            players[pid].super_power_timer = data.get("super_power_timer", 0)
            players[pid].direction = data.get("direction", "right")
            # Mettre à jour l'état mangé pour les fantômes
            if "fantome" in players[pid].role.lower():
                players[pid].is_eaten = data.get("is_eaten", False)
            # Gestion de l'état mangé pour les fantômes
            if hasattr(players[pid], 'is_eaten'):
                players[pid].is_eaten = data.get("is_eaten", False)
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
            new_player.super_power_active = data.get("super_power_active", False)
            new_player.super_power_timer = data.get("super_power_timer", 0)
            new_player.direction = data.get("direction", "right")
            # Ajouter l'état mangé pour les fantômes
            if "fantome" in new_player.role.lower():
                new_player.is_eaten = data.get("is_eaten", False)
            players[pid] = new_player
            print(f"[CLIENT] Nouveau joueur ajouté : {pid}")

def main_game(is_created_game, game_code, screen, font, coin_image, fruit_image, coin_offset, fruit_offset, role):
    """Fonction principale du jeu en ligne"""
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()
    
    # Afficher un écran de chargement pendant la connexion
    display_loading_screen("Connexion au serveur...", screen, font)
    
    n = Network()
    if not is_created_game:
        display_loading_screen("Connexion à la partie en cours...", screen, font)
        response = n.send_command(Protocols.Request.JOIN_ROOM, game_code)
        print(response)
    # Si le joueur souhaite créer une partie, il envoie une demande au serveur
    if is_created_game:
        # Le client demande la création d'une partie au serveur
        display_loading_screen("Création de la partie en cours...", screen, font)
        print("Game started")
        response = n.send_command(Protocols.Request.CREATE_GAME)
        game_code = response.get("code", "")
        print(f"Code de la partie créée : {game_code}")

    # Le serveur envoie les positions initiales à chaque joueur
    display_loading_screen("Chargement des données de jeu...", screen, font)
    welcome = n.receive_json()
    print("WELCOME reçu:", welcome)
    all_players_data = welcome
    print("fin")
    print("Joueurs récupérés :", all_players_data["players"])

    # création de la liste des joueurs
    players = {}
    current_player_id = all_players_data["current_player_id"]

    # On crée des classes pour chaque joueur en local
    for data in all_players_data["players"]:
        player = Player(ip=data["ip"], tcp_port=data["tcp_port"], role=data["roles"], position=tuple(data["pos"]))
        player.id = data["id"]
        player.score = data.get("score", 0)
        player.lives = data.get("lives", 3)
        players[player.id] = player

    coins = all_players_data.get("items", {}).get("coins", [])
    fruits = all_players_data.get("items", {}).get("fruits", [])

    # On initialise le chat
    chat_box = ChatBox(10, screen.get_height() - 210, 300, 200, font)
    
    if all_players_data.get("chat_history"):
        for msg in all_players_data.get("chat_history", []):
            chat_box.add_message(
                msg["player_name"],
                msg["message"],
                msg["timestamp"]
            )

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            chat_message = chat_box.handle_event(event)
            if chat_message:
                
                try:
                    response = n.send_command(Protocols.Request.SEND_CHAT_MESSAGE, chat_message)
                    # Traiter la réponse qui contient le message de chat pour l'expéditeur
                    if response:
                        update_game_state_from_server(response, players, current_player_id, coins, fruits, chat_box)
                        
                except Exception as e:
                    print(f"Erreur lors de l'envoi du message de chat: {e}")
            
            # Gestion de la visibilité du chat avec la touche TAB
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                chat_box.toggle_visibility()

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        current_player = players.get(current_player_id)

        # Si le joueur est Pacman et n'a plus de vies, afficher l'écran de Game Over
        if current_player.is_pacman and current_player.lives <= 0:
            game_over(current_player.score, screen, font)
            return  # Quitter la partie
        
        current_player.move(players, controlled=True)

        # Envoie les nouvelles positions au serveur
        payload = {
            "players": [
                {
                    "id": current_player.id,
                    "pos": current_player.coord,
                    "direction": getattr(current_player, 'direction', 'right')
                }
            ]
        }
        
        response = n.send_command(Protocols.Request.UPDATE_POSITION, payload)
        
        # Synchroniser l'état du jeu avec les données du serveur
        update_game_state_from_server(response, players, current_player_id, coins, fruits, chat_box)
        
        # Vérifier s'il y a des messages de chat entrants
        try:
            incoming_data = n.receive_json_non_blocking()
            if incoming_data:
                update_game_state_from_server(incoming_data, players, current_player_id, coins, fruits, chat_box)
        except Exception as e:
            print(f"Erreur lors de la réception des données: {e}")
        
        # Afficher la carte et les joueurs
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        for coin in coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))

        for fruit in fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))

        # On affiche sur l'interface l'ensemble des joueurs
        for player in players.values():
            player.draw(screen, current_player)

        # Affiche le code de la partie sous le score
        game_code_text = font.render(f"Code de la partie: {game_code}", True, (255, 255, 0))
        screen.blit(game_code_text, (10, 40))

        # Afficher le score du joueur actuel
        score_text = font.render(f"Score: {current_player.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f"Vies: {current_player.lives}", True, (0, 0, 255))
        screen.blit(lives_text, (WIDTH - 180, 1))

        # Dessiner le chat
        chat_box.draw(screen)

        pygame.display.flip()
        clock.tick(60)
    return
