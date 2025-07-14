import pygame
import sys
from common.global_variable import WIDTH, CELL_SIZE
from common.network import Network
from common.protocols import Protocols
from game.player import Player, PacMan, Ghost
from game.map import MAP_SURFACE
from game.ui.chat_box import ChatBox
from game.ui.components import display_loading_screen, game_over, you_win
from game.menus.main_menu import select_online_role

import logging
logger = logging.getLogger(__name__)



def update_game_state_from_server(state, players, current_player_id, coins, fruits, role_to_player_id, player_id_to_role, chat_box=None):
    """Synchronise l'état local du jeu avec les données du serveur
    role_to_player_id et player_id_to_role sont des dicts partagés !"""
    if role_to_player_id is not None and player_id_to_role is not None:
        for data in state.get("players", []):
            role = data["roles"].lower()
            pid = data["id"]
            role_to_player_id[role] = pid
            player_id_to_role[pid] = role
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
        #print(f"[DEBUG][SYNC] Serveur dit pour {data['id']} (role={data['roles']}): is_eaten={data.get('is_eaten')}")
        pid = data["id"]
        role = data["roles"].lower()

        # 1. S'il existe déjà, MAJ des attributs uniquement
        if pid in players:
            player = players[pid]
            # PATCH: gestion de la position
            if isinstance(player, Ghost) and player.is_eaten:
                # 1. Ne synchronise la position QUE si on reçoit l'info du serveur que le fantôme est ARRIVÉ au respawn (is_eaten passe à False)
                if not data.get("is_eaten", False):  # Le serveur dit que le fantôme n'est plus mangé
                    player.update_position(data["pos"])
                    player.is_eaten = False
                    player.respawn_target = None
                # Sinon, laisse le client animer le déplacement localement (voir point suivant)
            elif pid == current_player_id:
                if hasattr(player, "is_eaten") and player.is_eaten:
                    # Même logique pour le joueur contrôlé
                    if not data.get("is_eaten", False):
                        player.update_position(data["pos"])
                        player.is_eaten = False
                        player.respawn_target = None
                    # Sinon: NE RIEN FAIRE, laisse l'animation locale gérer
                else:
                    sx, sy = data["pos"]
                    dx = abs(sx - player.x)
                    dy = abs(sy - player.y)
                    if dx > CELL_SIZE * 2 or dy > CELL_SIZE * 2:
                        print("[PATCH][SYNC] Correction brutale position joueur (rollback)")
                        player.update_position(data["pos"])
                    # Sinon: on garde la position locale (pour la fluidité)
            else:
                player.update_position(tuple(data["pos"]))

            # ---- ATTRIBUTS TOUJOURS À JOUR (score, vie etc) ----
            player.score = data.get("score", 0)
            player.lives = data.get("lives", getattr(player, "lives", 3))
            player.invincible = data.get("invincible", False)
            player.invincibility_timer = data.get("invincibility_timer", 0)
            player.super_power_active = data.get("super_power_active", False)
            player.super_power_timer = data.get("super_power_timer", 0)
            player.direction = data.get("direction", "right")

            if hasattr(player, "ghosts_eaten"):
                player.ghosts_eaten = data.get("ghosts_eaten", 0)
            if hasattr(player, "is_eaten"):
                before = player.is_eaten
                player.is_eaten = data.get("is_eaten", False)
                after = player.is_eaten
                #print(f"[DEBUG][SYNC] Fantôme {pid}: is_eaten avant={before} → après={after}, id mémoire={id(player)}")
            if hasattr(player, "respawn_target"):
                player.respawn_target = data.get("respawn_target", None)

            if pid == current_player_id and data.get("activate_super_power"):
                print(f"[CLIENT] Activation du super pouvoir reçue pour le joueur {pid}")
                player.activate_super_power()

            continue  # <--- FINI pour ce joueur, on ne fait pas le else suivant !

        # 2. Sinon, NOUVEAU joueur : on instancie la bonne classe
        if "pacman" in role:
            new_player = PacMan(
                ip=data["ip"],
                tcp_port=data["tcp_port"],
                position=tuple(data["pos"])
            )
        elif "fantome" in role:
            new_player = Ghost(
                ip=data["ip"],
                tcp_port=data["tcp_port"],
                position=tuple(data["pos"])
            )

        else:
            print(f"Rôle inconnu {role}, joueur ignoré !")
            continue

        new_player.id = pid
        new_player.score = data.get("score", 0)
        if hasattr(new_player, "lives"):
            new_player.lives = data.get("lives", 3)
        if hasattr(new_player, "invincible"):
            new_player.invincible = data.get("invincible", False)
        if hasattr(new_player, "super_power_active"):
            new_player.super_power_active = data.get("super_power_active", False)
        if hasattr(new_player, "super_power_timer"):
            new_player.super_power_timer = data.get("super_power_timer", 0)
        new_player.direction = data.get("direction", "right")
        if hasattr(new_player, "is_eaten"):
            new_player.is_eaten = data.get("is_eaten", False)

        players[pid] = new_player
        role_to_player_id[role] = pid
        player_id_to_role[pid] = role

        print(f"[CLIENT] Nouveau joueur ajouté : {pid}")

    # Nettoyage : supprimer les joueurs qui ne sont plus envoyés par le serveur
    player_ids_from_server = {data["id"] for data in state.get("players", [])}
    for pid in list(players):
        if pid not in player_ids_from_server:
            del players[pid]
            if player_id_to_role and pid in player_id_to_role:
                role = player_id_to_role.pop(pid)
                if role_to_player_id and role in role_to_player_id and role_to_player_id[role] == pid:
                    del role_to_player_id[role]
            print(f"[CLIENT] Joueur {pid} supprimé (parti ou déconnecté)")
    """for pid, player in players.items():
        if "fantome" in player.role.lower():
            print(f"[DEBUG][LOCAL] Instance {pid} (role={player.role}): is_eaten={player.is_eaten}, id mémoire={id(player)}, objet={repr(player)}")
            print(f"[DEBUG][LOCAL] Instance {pid} (role={player.role}): is_eaten={player.is_eaten}, id mémoire={id(player)}")"""


def main_game(is_created_game, game_code, screen, font, coin_image, fruit_image, coin_offset, fruit_offset, role):
    """Fonction principale du jeu en ligne"""
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 24)
    clock = pygame.time.Clock()

    # Afficher un écran de chargement pendant la connexion
    display_loading_screen("Connexion au serveur...", screen, font)

    if not is_created_game:
        taken_roles = []
        while True:
            display_loading_screen("Connexion à la partie en cours...", screen, font)
            n=Network()
            response = n.send_command(Protocols.Request.JOIN_ROOM, {"game_code": game_code, "role": role})
            print(f"[CLIENT] Je tente de join la room avec le rôle: {role}")
            print("Réponse serveur :", response)
            if response.get("status") in ("ok", "joined"):  # adapte selon ta logique serveur
                break
            else:
                # Teste si la raison est "role déjà pris"
                taken_roles = response.get("taken_roles", [])
                # Ici, on passe la liste des rôles pris à select_online_role
                nouveau_role = select_online_role(screen, font, taken_roles)
                print("Rôle choisi après refus :", nouveau_role)
                if nouveau_role == "back":
                    n.close()
                    return
                role = nouveau_role
                n.close()
                continue

    # Si le joueur souhaite créer une partie, il envoie une demande au serveur
    elif is_created_game:
        # Le client demande la création d'une partie au serveur
        n = Network()
        display_loading_screen("Création de la partie en cours...", screen, font)
        print("Game started")
        response = n.send_command(Protocols.Request.CREATE_GAME,{"role": role})
        print(f"[CLIENT] Rôle demandé : {role}")
        print(f"[CLIENT] Réponse du serveur : {response}")
        game_code = response.get("code", "")
        print(f"Code de la partie créée : {game_code}")

    # Le serveur envoie les positions initiales à chaque joueur
    display_loading_screen("Chargement des données de jeu...", screen, font)
    welcome = n.receive_json()
    print("WELCOME reçu:", welcome)
    all_players_data = welcome
    print("fin")
    print("Joueurs récupérés :", all_players_data["players"])
    print(f"[CLIENT] Données reçues du serveur (welcome) : {all_players_data}")

    # création de la liste des joueurs
    players = {}
    role_to_player_id = {}
    player_id_to_role = {}
    current_player_id = all_players_data["current_player_id"]
    print(f"[CLIENT] current_player_id (pour ce client) : {current_player_id}")


    # On crée des classes pour chaque joueur en local
    for data in all_players_data["players"]:
        print(f"[CLIENT] Initialisation du joueur : {data['id']} | rôle : {data['roles']} | pos : {data['pos']}")
        role = data["roles"].lower()
        pid = data["id"]
        if "pacman" in role:
            player = PacMan(ip=data["ip"], tcp_port=data["tcp_port"], position=tuple(data["pos"]))
        elif "fantome" in role:
            player = Ghost(ip=data["ip"], tcp_port=data["tcp_port"], position=tuple(data["pos"]))
        else:
            print(f"Erreur: rôle inconnu {role}")
            continue
        player.id = pid
        player.role = role
        player.score = data.get("score", 0)
        player.lives = data.get("lives", 3)
        players[pid] = player
        role_to_player_id[role] = pid
        player_id_to_role[pid] = role

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
                        update_game_state_from_server(response, players, current_player_id, coins, fruits, role_to_player_id, player_id_to_role, chat_box)

                except Exception as e:
                    print(f"Erreur lors de l'envoi du message de chat: {e}")
                    import traceback
                    logger.error(f"Exception attrapée: {e}\n{traceback.format_exc()}")

            # Gestion de la visibilité du chat avec la touche TAB
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                chat_box.toggle_visibility()

        playerControlled = players.get(current_player_id)
        if playerControlled is None:
            print("[CLIENT] Aucun joueur contrôlé (playerControlled est None), retour au menu.")
            return

        # Seul le joueur contrôlé par le client (identifié par current_player_id) peut être déplacé via les touches du clavier
        if isinstance(playerControlled, PacMan) and playerControlled.lives <= 0:
            game_over(playerControlled.score, screen, font)
            return

        # --- MOVE LOCAL ---
        playerControlled.move(players, controlled=True)

        for pid, player in players.items():
            if pid != current_player_id:
                player.move(players, controlled=False)

        # --- ENVOI POSITION (UNE SEULE FOIS PAR FRAME) ---
        payload = {
            "players": [
                {
                    "id": playerControlled.id,
                    "pos": playerControlled.coord,
                    "direction": getattr(playerControlled, 'direction', 'right')
                }
            ]
        }
        # On envoie la position et on reçoit la vérité serveur
        response = n.send_command(Protocols.Request.UPDATE_POSITION, payload)
        update_game_state_from_server(response, players, current_player_id, coins, fruits, role_to_player_id,
                                      player_id_to_role, chat_box)


        if response.get("game_over"):
            winner = response.get("winner")
            if winner == "fantomes":
                if playerControlled.role.lower().startswith("pacman"):
                    game_over(playerControlled.score, screen, font)
                else:
                    you_win(playerControlled.score, screen, font)
            elif winner == "pacman":  # (au cas où tu ajoutes la victoire Pacman plus tard)
                if playerControlled.role.lower().startswith("pacman"):
                    you_win(playerControlled.score, screen, font)
                else:
                    game_over(playerControlled.score, screen, font)
            return  # On quitte la partie !

        # Vérifier s'il y a des messages de chat entrants
        try:
            incoming_data = n.receive_json_non_blocking()
            if incoming_data:
                update_game_state_from_server(incoming_data, players, current_player_id, coins, fruits, role_to_player_id, player_id_to_role, chat_box)
                if incoming_data.get("game_over"):
                    winner = incoming_data.get("winner")
                    if winner == "fantomes":
                        if playerControlled.role.lower().startswith("pacman"):
                            game_over(playerControlled.score, screen, font)
                        else:
                            you_win(playerControlled.score, screen, font)
                    elif winner == "pacman":
                        if playerControlled.role.lower().startswith("pacman"):
                            you_win(playerControlled.score, screen, font)
                        else:
                            game_over(playerControlled.score, screen, font)
                    return  # On quitte la partie !
        except Exception as e:
            print(f"Erreur lors de la réception des données: {e}")
            import traceback
            logger.error(f"Exception attrapée: {e}\n{traceback.format_exc()}")

        # Afficher la carte et les joueurs
        screen.fill((0, 0, 0))
        screen.blit(MAP_SURFACE, (0, 0))
        for coin in coins:
            screen.blit(coin_image, (coin[0] + coin_offset, coin[1] + coin_offset))

        for fruit in fruits:
            screen.blit(fruit_image, (fruit[0] + fruit_offset, fruit[1] + fruit_offset))

        # On affiche sur l'interface l'ensemble des joueurs
        for player in players.values():
            player.draw(screen, playerControlled)

        # Affiche le code de la partie sous le score
        game_code_text = font.render(f"Code de la partie: {game_code}", True, (69, 6, 44))
        screen.blit(game_code_text, (10, 40))

        # Afficher le score du joueur actuel
        score_text = font.render(f"Score: {playerControlled.score}", True, (0, 0, 255))
        screen.blit(score_text, (10, 10))

        lives_text = font.render(f"Vies: {playerControlled.lives}", True, (0, 0, 255))
        screen.blit(lives_text, (WIDTH - 100, 10))

        if hasattr(playerControlled, "ghosts_eaten"):
            ghosts_eaten_text = font.render(
                f"Fantômes mangés: {playerControlled.ghosts_eaten}/ 15", True, (0, 0, 255)
            )
            screen.blit(ghosts_eaten_text, (WIDTH - 220, 30))

        # Dessiner le chat
        chat_box.draw(screen)

        pygame.display.flip()
        clock.tick(60)
    return
