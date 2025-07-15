import sys
import os
import threading
import json
import uuid
import socket
import time

# Configuration robuste des imports - DOIT ÊTRE EN PREMIER
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from _thread import start_new_thread
from rooms import RoomManager
from common.protocols import Protocols
from game.utils.helpers import distance
from common.global_variable import CELL_SIZE, WIDTH, HEIGHT


# Configuration pour la journalisation
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pacmint_server")


def send_json(conn, obj):
    """Envoie un dict JSON suivi d'un saut de ligne."""
    payload = json.dumps(obj).encode() + b"\n"
    conn.sendall(payload)


def recv_json(conn):
    """Lit une ligne (jusqu’à \n) et renvoie le dict."""
    line = conn.makefile("r").readline()
    if not line:
        raise ConnectionError("socket closed")
    return json.loads(line)


# Paramètres
timeout = 10  # temps en seconde pour considérer un joueur inactif
max_players = 5  # Limite de joueurs
server = "0.0.0.0"
port = 5555  # Port de communication

# Initialisation d'un RoomManager
room_manager = RoomManager(room_capacity=max_players)

# création d'un socket INET (IPV4) et un socket Stream (TCP)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Liaison du socket à l'adresse IP et au port définis précédemment
    s.bind((server, port))
except socket.error as e:
    logger.error("Erreur de liaison du socket :")
    sys.exit(1)

# Nombre de connexions simultanées maximales
s.listen(max_players)
logger.info("Serveur démarré, en attente de connexions...")


def game_tick():
    """Envoie des mises à jour régulières à tous les joueurs."""
    while True:
        for room in room_manager.rooms.values():
            # Mettre à jour les états des joueurs
            update_player_states(room)
            update_ghost_eaten_states(room)

            # Diffuser l'état du jeu à tous les joueurs
            for player_id, player in room.players.items():
                if hasattr(player, "tcp_socket") and player.tcp_socket:
                    try:
                        state = sync_game_state(room, player_id)
                        send_json(player.tcp_socket, state)
                    except Exception as e:
                        logger.error(
                            f"Erreur lors de la diffusion au joueur {player_id}: {e}"
                        )

        time.sleep(0.1)  # Envoie des mises à jour toutes les 100ms


# Démarrer le thread de mise à jour régulière
threading.Thread(target=game_tick, daemon=True).start()


# Gestion de l'arrêt du serveur
def server_shutdown():
    logger.info("Arrêt du serveur...")
    s.close()
    sys.exit(0)


def build_state(
    room,
    current_id,
    *,
    with_action=False,
    initial=False,
    activate_super_power=False,
    event=None,
):
    state = {
        "current_player_id": current_id,
        "players": [
            {
                "id": pid,
                "pos": p.position,
                "roles": p.role,
                "ip": p.ip,
                "tcp_port": p.tcp_port,
                "score": p.score,
                "lives": getattr(p, "lives", 3),
                "invincible": getattr(p, "invincible", False),
                "invincibility_timer": getattr(p, "invincibility_timer", 0),
                "super_power_active": getattr(p, "super_power_active", False),
                "super_power_timer": getattr(p, "super_power_timer", 0),
                "is_eaten": getattr(p, "is_eaten", False),
                "respawn_target": getattr(p, "respawn_target", None),
                "direction": getattr(p, "direction", "right"),
                "ghosts_eaten": getattr(p, "ghosts_eaten", 0),
                "activate_super_power": (
                    activate_super_power if pid == current_id else False
                ),
            }
            for pid, p in room.players.items()
        ],
    }
    if with_action:
        if initial:
            state["action"] = "welcome"
            state["items"] = {
                "coins": room.item_manager.coins,
                "fruits": room.item_manager.fruits,
            }
            state["chat_history"] = room.get_chat_history()
        else:
            state["action"] = "update"

    # Ajouter des événements spécifiques si nécessaire
    if event:
        state["event"] = event

    return state


def broadcast_to_room(
    room, event=None, exclude_player=None, force_game_over=None, force_winner=None
):
    """Diffuse l'état du jeu à tous les clients connectés d'une room"""
    for pid, player in list(room.players.items()):
        if exclude_player and pid == exclude_player:
            continue
        if hasattr(player, "tcp_socket") and player.tcp_socket:
            try:
                # ICI : construit le state POUR CE JOUEUR
                state = sync_game_state(room, pid, event=event)
                # PATCH: force l'injection de game_over si besoin
                if force_game_over is not None:
                    state["game_over"] = force_game_over
                if force_winner is not None:
                    state["winner"] = force_winner
                send_json(player.tcp_socket, state)
                logger.debug(f"État diffusé au joueur {pid}")
            except Exception as e:
                logger.error(f"Erreur lors de la diffusion au joueur {pid}: {e}")


def threaded_game_client(connexion, joueur_actuel, room_id, address=None):
    logger.info(f"Connexion établie avec le joueur {joueur_actuel} depuis {address}")
    room_id = int(room_id)
    try:
        # Vérifie que la salle existe bien sinon on ferme la session
        if not room_manager.room_exists(room_id):
            logger.warning(f"Partie introuvable pour room_id={room_id}")
            logger.info(f"[SERVER] Fermeture connexion pour joueur {joueur_actuel}")
            connexion.close()
            return

        # Récupération du salon
        room = room_manager.rooms[room_id]

        # Mise à jour des infos réseau du joueur
        if joueur_actuel in room.players:
            player = room.players[joueur_actuel]
            player.ip = address[0]
            player.tcp_port = address[1]
            player.tcp_socket = connexion

        # Le serveur envoie les positions initiales aux joueurs
        welcome = build_state(room, joueur_actuel, with_action=True, initial=True)
        send_json(connexion, welcome)

        while True:
            try:
                # On écoute le client
                raw_data = recv_json(connexion)

                if not raw_data.get("command", False):
                    logger.info(f"Déconnexion du joueur {joueur_actuel}")
                    break

                if raw_data.get("command") == Protocols.Request.UPDATE_POSITION:
                    payload = raw_data.get("message", {})
                    activate_super_power = False

                    for pdata in payload.get("players", []):
                        pid = pdata["id"]
                        pos = pdata["pos"]
                        direction = pdata.get("direction", "right")

                        if pid in room.players:
                            player = room.players[pid]
                            player.update_position(pos)
                            player.direction = direction
                            logger.debug(
                                f"Position et direction mises à jour pour le joueur {pid}: {pos}, direction: {direction}"
                            )

                            # Vérifie la collecte d'items pour ce joueur (uniquement si c'est Pacman)
                            if "pacman" in player.role.lower():
                                server_check_item_collision(room, player)

                    # Mise à jour des états des joueurs (timers, etc.)
                    update_player_states(room)

                    # GESTION COLLISION FANTÔME/PACMAN
                    collision_result = check_pacman_ghost_collision(room)
                    event = None

                    if collision_result["ghost_eaten"]:
                        pacman = collision_result["ghost_eaten"]["pacman"]
                        ghost = collision_result["ghost_eaten"]["ghost"]

                        # marquer le fantôme comme mangé IMMEDIATEMENT pour  ne pas le manger plusieurs fois
                        if not ghost.is_eaten:
                            ghost.is_eaten = True

                        eat_ghost(pacman, ghost, room)
                        event = "ghost_eaten"
                        logger.info(f"Fantôme mangé ! Score Pacman : {pacman.score}")
                    elif collision_result["pacman_hit"]:
                        pacman_touche = collision_result["pacman_hit"]
                        pacman_touche.lives = getattr(pacman_touche, "lives", 3) - 1
                        pacman_touche.invincible = True
                        pacman_touche.invincibility_timer = 600  # 4 secondes à 60 FPS
                        logger.info(
                            f"Pacman touché ! Vies restantes : {pacman_touche.lives}"
                        )
                        event = "pacman_hit"
                    update_ghost_eaten_states(room)

                    # Construire l'état de jeu final
                    state = sync_game_state(room, joueur_actuel, event=event)
                    pacmans = [
                        p for p in room.players.values() if "pacman" in p.role.lower()
                    ]
                    game_over = False
                    for pacman in pacmans:
                        if getattr(pacman, "lives", 3) <= 0:
                            game_over = True
                            break
                        if getattr(pacman, "ghosts_eaten", 0) >= 3:
                            # state["game_over"] = True
                            # state["winner"] = "pacman"
                            room.game_over = True
                            room.winner = "pacman"
                            broadcast_to_room(
                                room,
                                event=event,
                                force_game_over=True,
                                force_winner="pacman",
                            )
                            continue  #

                    if game_over:
                        # state["game_over"] = True
                        # state["winner"] = "fantomes"
                        room.game_over = True
                        room.winner = "fantomes"
                        broadcast_to_room(
                            room,
                            event=event,
                            force_game_over=True,
                            force_winner="fantomes",
                        )
                        continue  # On saute la suite de la boucle, car la partie est finie

                    # On envoie l'état mis à jour uniquement au client qui a initié la demande
                    send_json(connexion, state)

                elif raw_data.get("command") == Protocols.Request.SEND_CHAT_MESSAGE:
                    logger.info(
                        f"[SERVER] Traitement de la commande : {raw_data.get('command')}"
                    )
                    # Gestion des messages de chat
                    try:
                        message_text = raw_data.get("message", "").strip()
                        if (
                            message_text and len(message_text) <= 200
                        ):  # Limiter la taille des messages
                            chat_message = room.add_chat_message(
                                joueur_actuel, message_text
                            )

                            chat_response = {
                                "action": "chat_message",
                                "chat_message": chat_message,
                            }

                            broadcast_to_room(
                                room, event=chat_response, exclude_player=joueur_actuel
                            )

                            send_json(
                                connexion,
                                {
                                    "status": "ok",
                                    "message": "Message sent",
                                    "action": "chat_message",
                                    "chat_message": chat_message,
                                },
                            )
                        else:
                            send_json(
                                connexion,
                                {"status": "error", "message": "Invalid message"},
                            )
                    except Exception as e:
                        send_json(
                            connexion, {"status": "error", "message": "Server error"}
                        )

            except ConnectionError as ce:
                logger.info(
                    f"[Déconnexion] Socket fermée pour le joueur {joueur_actuel} : {ce}"
                )
                break
            except Exception as erreur:
                logger.error(
                    f"Erreur serveur avec le joueur {joueur_actuel} : {erreur}"
                )
                import traceback

                logger.error(f"Exception attrapée: {erreur}\n{traceback.format_exc()}")
                break

    except Exception as e:
        logger.error(f"Erreur dans la gestion de la partie : {e}")
    finally:
        logger.info(f"[SERVER] Fermeture connexion pour joueur {joueur_actuel}")
        connexion.close()
        room.leave(joueur_actuel)  # Supprime le joueur de la salle
        logger.info(f"Connexion fermée pour le joueur {joueur_actuel}")


def threaded_client(connexion, address):
    """
    Gère la création et la connexion aux parties.
    """
    player_id = None  # Initialiser le player_id
    try:
        raw_data = recv_json(connexion)
        if not raw_data:
            logger.warning("Connexion interrompue avant la réception des données.")
            logger.info(f"[SERVER] Fermeture connexion pour {address}")
            connexion.close()
            return

        data = raw_data
        if data["command"] == Protocols.Request.CREATE_GAME:
            logger.info("Création d'une nouvelle partie")

            # On crée la partie
            room_name = "Test Room"
            room = room_manager.create_room(room_name=room_name)
            room_code = room.code

            player_id = str(uuid.uuid4())  # Identifiant unique pour le joueur
            role = None
            if "message" in data and isinstance(data["message"], dict):
                role = data["message"].get("role")
            if room_manager.join(player_id, room_code, role=role) is not None:
                # On envoie le code de la partie au joueur
                send_json(connexion, {"status": "ok", "code": room_code})
                thread = threading.Thread(
                    target=threaded_game_client,
                    args=(connexion, player_id, room_code, address),
                )
                thread.daemon = True
                thread.start()
                return
            else:
                send_json(connexion, {"status": "full"})
                logger.info(f"[SERVER] Fermeture connexion pour joueur {player_id}")
                connexion.close()
                return

        elif data["command"] == Protocols.Request.JOIN_ROOM:
            logger.info(f"Un joueur tente de rejoindre la room {data['message']}")
            if isinstance(data["message"], dict):
                room_id = (
                    data["message"].get("game_code")
                    or data["message"].get("room_id")
                    or data["message"]
                )
                role = data["message"].get("role")
            else:
                room_id = data["message"]
                role = None
            player_id = str(uuid.uuid4())
            result = room_manager.join(player_id, room_id, role=role)
            if isinstance(result, dict) and result.get("status") == "error":
                send_json(
                    connexion, result
                )  # On renvoie l'objet erreur tel quel (role_taken, room_full, ...)
                logger.info(
                    f"[SERVER] Refus JOIN_ROOM pour joueur {player_id}: {result}"
                )
                connexion.close()
                return
            elif result and isinstance(result, dict) and result.get("status") == "ok":
                send_json(
                    connexion, {"status": "joined", "message": "Welcome to the room"}
                )
                thread = threading.Thread(
                    target=threaded_game_client,
                    args=(connexion, player_id, room_id, address),
                )
                thread.daemon = True
                thread.start()
                return
            else:
                send_json(
                    connexion,
                    {
                        "status": (
                            "full" if room_manager.room_exists(room_id) else "not_found"
                        )
                    },
                )
                logger.info(f"[SERVER] Fermeture connexion pour joueur {player_id}")
                connexion.close()
                return

    except Exception as e:
        logger.error(f"Erreur lors de la gestion d'un client : {e}")
        log_msg = (
            f"[SERVER] Fermeture connexion pour joueur {player_id}"
            if player_id
            else f"[SERVER] Fermeture connexion pour {address}"
        )
        logger.info(log_msg)
        connexion.close()


def update_player_states(room):
    """Met à jour les timers et états des joueurs (invincibilité, super-pouvoir)"""
    for pid, player in list(room.players.items()):
        # Mise à jour du timer d'invincibilité
        if getattr(player, "invincible", False):
            player.invincibility_timer -= 1
            if player.invincibility_timer <= 0:
                player.invincible = False
                logger.info(f"Joueur {pid} n'est plus invincible")

        # Mise à jour du timer de super-pouvoir
        if getattr(player, "super_power_active", False):
            if time.time() >= getattr(player, "super_power_end_time", 0):
                player.super_power_active = False
                logger.info(f"Super-pouvoir désactivé pour le joueur {pid}")


def server_check_item_collision(room, pacman):
    """Vérifie et gère la collision de pacman avec les pièces/fruits, modifie room.item_manager, et score pacman."""
    coins_collected = []
    fruits_collected = []
    for coin in room.item_manager.coins[:]:
        if (
            distance(pacman.position[0], pacman.position[1], coin[0], coin[1])
            < CELL_SIZE // 2
        ):  # à ajuster selon ton CELL_SIZE
            coins_collected.append(coin)
            room.item_manager.coins.remove(coin)
    for fruit in room.item_manager.fruits[:]:
        if (
            distance(pacman.position[0], pacman.position[1], fruit[0], fruit[1])
            < CELL_SIZE // 2
        ):
            fruits_collected.append(fruit)
            room.item_manager.fruits.remove(fruit)
            server_activate_super_power(pacman)  # à écrire
    pacman.score += 10 * len(coins_collected)
    pacman.score += 50 * len(fruits_collected)


def server_activate_super_power(pacman, duration=5):
    pacman.super_power_active = True
    pacman.super_power_end_time = time.time() + duration


def check_pacman_ghost_collision(room):
    """Vérifie les collisions entre Pacman et les fantômes."""
    pacmans = [p for p in room.players.values() if "pacman" in p.role.lower()]
    ghosts = [p for p in room.players.values() if "fantome" in p.role.lower()]

    collision_result = {"pacman_hit": None, "ghost_eaten": None}

    for pacman in pacmans:
        for ghost in ghosts:
            # Ignorer les fantômes déjà mangés
            if getattr(ghost, "is_eaten", False):
                continue

            dx = pacman.position[0] - ghost.position[0]
            dy = pacman.position[1] - ghost.position[1]
            distance_squared = dx * dx + dy * dy
            # Rayon de collision (ajuste selon la taille de tes sprites)
            if distance_squared < 30 * 30:
                # Si Pacman a le super-pouvoir et n'est pas invincible
                if getattr(pacman, "super_power_active", False):
                    collision_result["ghost_eaten"] = {"pacman": pacman, "ghost": ghost}
                    logger.info(
                        f"Pacman mange le fantôme {ghost.id if hasattr(ghost, 'id') else 'unknown'}"
                    )
                    return collision_result
                # Sinon, si Pacman n'est pas invincible, il est touché
                elif not getattr(pacman, "invincible", False):
                    collision_result["pacman_hit"] = pacman
                    return collision_result

    return collision_result


def eat_ghost(pacman, ghost, room):
    pacman.score += 200
    ghost.is_eaten = True
    if hasattr(pacman, "ghosts_eaten"):
        pacman.ghosts_eaten += 1

    role = ghost.role.lower()
    respawn_pos = None
    if hasattr(room, "initial_positions") and role in room.initial_positions:
        respawn_pos = room.initial_positions[role]
    else:
        respawn_pos = (WIDTH // 2, HEIGHT // 2)

    ghost.respawn_target = respawn_pos
    logger.info(
        f"Fantôme {getattr(ghost, 'id', 'unknown')} mangé par Pacman. Score: +200 (respawn {respawn_pos})"
    )
    return True


def update_ghost_eaten_states(room):
    for player in room.players.values():
        # Si c'est un fantôme et qu'il est mangé, on met à jour son état
        if player.role.lower().startswith("fantome") and getattr(
            player, "is_eaten", False
        ):
            if hasattr(player, "update_eaten_state"):
                player.update_eaten_state()


def sync_game_state(room, current_id, event=None):
    """
    Construit l'état du jeu pour synchronisation
    La diffusion est maintenant gérée par l'appelant
    """
    # Mettre à jour les états des joueurs (timers d'invincibilité, etc.)
    update_player_states(room)

    # Construire l'état actuel du jeu
    state = build_state(room, current_id, with_action=True, event=event)

    # Ajouter les informations sur les items
    state["items"] = {
        "coins": room.item_manager.coins,
        "fruits": room.item_manager.fruits,
    }

    return state


while True:
    connexion, address = s.accept()
    logger.info(f"Connecté à: {address}")
    logger.debug(f"Room Manager état actuel: {room_manager.rooms}")
    thread = threading.Thread(target=threaded_client, args=(connexion, address))
    thread.start()
