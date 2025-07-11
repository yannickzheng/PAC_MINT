import sys
import os

# Configuration robuste des imports - DOIT ÊTRE EN PREMIER
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import time
from _thread import start_new_thread
from rooms import RoomManager
from common.protocols import Protocols

import threading

import json
import uuid

# Configuration pour la journalisation
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pacmint_server')

def send_json(conn, obj):
    """Envoie un dict JSON suivi d'un saut de ligne."""
    payload = json.dumps(obj).encode() + b'\n'
    conn.sendall(payload)

def recv_json(conn):
    """Lit une ligne (jusqu’à \n) et renvoie le dict."""
    line = conn.makefile('r').readline()
    if not line:
        raise ConnectionError("socket closed")
    return json.loads(line)


#Paramètres
timeout = 10 #temps en seconde pour considérer un joueur inactif
max_players = 5 # Limite de joueurs
server = "localhost" # Adresse IP du serveur
port = 5555 # Port de communication

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

#Gestion de l'arrêt du serveur
def server_shutdown():
    logger.info("Arrêt du serveur...")
    s.close()
    sys.exit(0)

def build_state(room, current_id, *,with_action = False, initial=False, activate_super_power=False, event=None):
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
                "super_power_active": getattr(p, "super_power_active", False),
                "super_power_timer": getattr(p, "super_power_timer", 0),
                "is_eaten": getattr(p, "is_eaten", False),
                "direction": getattr(p, "direction", "right"),
                "activate_super_power": activate_super_power if pid == current_id else False
            }
            for pid, p in room.players.items()
        ]
    }
    if with_action:
        if initial:
            state["action"] = "welcome"
            state["items"] = {
                "coins": room.item_manager.coins,
                "fruits": room.item_manager.fruits
            }
            state["chat_history"] = room.get_chat_history()
        else:
            state["action"] = "update"
    
    # Ajouter des événements spécifiques si nécessaire
    if event:
        state["event"] = event
    
    return state

def broadcast_to_room(room, state, exclude_player=None):
    """Diffuse l'état du jeu à tous les clients connectés d'une room"""
    for pid, player in room.players.items():
        if exclude_player and pid == exclude_player:
            continue
        if hasattr(player, 'tcp_socket') and player.tcp_socket:
            try:
                send_json(player.tcp_socket, state)
                logger.debug(f"État diffusé au joueur {pid}")
            except Exception as e:
                logger.error(f"Erreur lors de la diffusion au joueur {pid}: {e}")


def threaded_game_client(connexion, joueur_actuel, room_id, address = None):
    """
       Fonction permettant de gérer les connexions des clients
       :param connexion: socket de connexion
       :param joueur_actuel: joueur actuel (entier)
       :return:
    """
    logger.info(f"Connexion établie avec le joueur {joueur_actuel} depuis {address}")

    #Sécurité, on impose que room_id est bien un int
    room_id = int(room_id)

    try:
        # On vérifie que la salle existe bien sinon on ferme la session
        if not room_manager.room_exists(room_id):
            logger.warning(f"Partie introuvable pour room_id={room_id}")
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

        #Le serveur envoie les postions initiales aux joueurs
        welcome = build_state(room, joueur_actuel,with_action= True, initial=True)
        send_json(connexion, welcome)

        while True:
            try:
                #On écoute le client
                raw_data = recv_json(connexion)

                if not raw_data.get("command", False):
                    logger.info(f"Déconnexion du joueur {joueur_actuel}")
                    break
                #print(raw_data)
                if raw_data.get("command") == Protocols.Request.UPDATE_POSITION:
                    #print(raw_data)
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
                            logger.debug(f"Position et direction mises à jour pour le joueur {pid}: {pos}, direction: {direction}")

                            # Vérifie la collecte d'items pour ce joueur (uniquement si c'est Pacman)
                            if player.role == "pacman":
                                collected = room.item_manager.check_collision(player)
                                if collected["coins"]:
                                    player.score += 10 * len(collected["coins"])
                                if collected["fruits"]:
                                    player.score += 50 * len(collected["fruits"])
                                    activate_super_power = True
                                    player.super_power_active = True
                                    player.super_power_timer = 300  # 5 secondes à 60 FPS

                    # Mise à jour des états des joueurs (timers, etc.)
                    update_player_states(room)
                    
                    # GESTION COLLISION FANTÔME/PACMAN 
                    collision_result = check_pacman_ghost_collision(room)
                    event = None
                    
                    if collision_result["ghost_eaten"]:
                        # Pacman mange un fantôme
                        pacman = collision_result["ghost_eaten"]["pacman"]
                        ghost = collision_result["ghost_eaten"]["ghost"]
                        eat_ghost(pacman, ghost, room)
                        event = "ghost_eaten"
                        logger.info(f"Fantôme mangé ! Score Pacman : {pacman.score}")
                    elif collision_result["pacman_hit"]:
                        # Pacman est touché par un fantôme
                        pacman_touche = collision_result["pacman_hit"]
                        pacman_touche.lives = getattr(pacman_touche, "lives", 3) - 1
                        pacman_touche.invincible = True
                        pacman_touche.invincibility_timer = 180  # 3 secondes à 60 FPS
                        logger.info(f"Pacman touché ! Vies restantes : {pacman_touche.lives}")
                        event = "pacman_hit"
                    
                    # Construire l'état de jeu final
                    state = sync_game_state(room, joueur_actuel, event=event)
                    pacmans = [p for p in room.players.values() if "pacman" in p.role.lower()]
                    game_over = False
                    for pacman in pacmans:
                        if getattr(pacman, "lives", 3) <= 0:
                            game_over = True
                            break

                    if game_over:
                        state["game_over"] = True
                        state["winner"] = "fantomes"
                        broadcast_to_room(room, state)
                        continue  # On saute la suite de la boucle, car la partie est finie
                    if activate_super_power:
                        state["activate_super_power"] = True
                        # Diffuser à tous les clients de la room quand un super pouvoir est activé
                        broadcast_to_room(room, state)
                    elif event == "pacman_hit" or event == "ghost_eaten":
                        # Diffuser à tous les clients quand Pacman est touché ou mange un fantôme
                        broadcast_to_room(room, state)
                    else:
                        # Envoyer la réponse uniquement au client qui a fait la requête
                        send_json(connexion, state)
                
                elif raw_data.get("command") == Protocols.Request.SEND_CHAT_MESSAGE:
                    # Gestion des messages de chat
                    try:
                        message_text = raw_data.get("message", "").strip()
                        if message_text and len(message_text) <= 200:  # Limiter la taille des messages
                            # Ajouter le message au chat de la room
                            chat_message = room.add_chat_message(joueur_actuel, message_text)
                            
                            # Créer la réponse pour diffuser le message
                            chat_response = {
                                "action": "chat_message",
                                "chat_message": chat_message
                            }
                            
                            # On diffuse le message à tous les joueurs de la room sauf l'expéditeur
                            broadcast_to_room(room, chat_response, exclude_player=joueur_actuel)
                            
                            # Envoyer une confirmation avec le message à l'expéditeur
                            send_json(connexion, {
                                "status": "ok", 
                                "message": "Message sent",
                                "action": "chat_message",
                                "chat_message": chat_message
                            })
                        else:
                            # Message trop long ou vide
                            send_json(connexion, {"status": "error", "message": "Invalid message"})
                    except Exception as e:
                        send_json(connexion, {"status": "error", "message": "Server error"})
                    

            except Exception as erreur:
                logger.error(f"Erreur avec le joueur {joueur_actuel} : {erreur}")
                break

        connexion.close()
        room.leave(joueur_actuel)  # Supprime le joueur de la salle
        logger.info(f"Connexion fermée pour le joueur {joueur_actuel}")


    except Exception as e:
        logger.error(f"Erreur dans la gestion de la partie : {e}")
        connexion.close()

def threaded_client(connexion, address):
    """
    Gère la création et la connexion aux parties.
    """
    try:
        raw_data = recv_json(connexion)
        if not raw_data:
            logger.warning("Connexion interrompue avant la réception des données.")
            connexion.close()
            return

        data = raw_data
        if data["command"] == Protocols.Request.CREATE_GAME:
            logger.info("Création d'une nouvelle partie")

            #On crée la partie
            room_name = "Test Room"
            room = room_manager.create_room(room_name=room_name)
            room_code = room.code

            player_id = str(uuid.uuid4())   # Identifiant unique pour le joueur
            if room_manager.join(player_id, room_code) is not None:
                #On envoie le code de la partie au joueur
                send_json(connexion, {"status": "ok", "code": room_code})
                start_new_thread(threaded_game_client, (connexion, player_id, room_code, address))
                #return
            else:
                send_json(connexion, {"status": "full"})
                connexion.close()

        elif data["command"] == Protocols.Request.JOIN_ROOM:
            logger.info(f"Un joueur tente de rejoindre la room {data['message']}")
            room_id = data["message"]
            player_id = str(uuid.uuid4())
            if room_manager.join(player_id, room_id):
                send_json(connexion, {"status": "joined", "message": "Welcome to the room"})
                threaded_game_client(connexion, player_id, room_id, address)
                #return
            else:
                send_json(connexion, {"status": "full" if room_manager.room_exists(room_id) else "not_found"})
                connexion.close()
                return
    except Exception as e:
        logger.error(f"Erreur lors de la gestion d'un client : {e}")
        connexion.close()


def update_player_states(room):
    """Met à jour les timers et états des joueurs (invincibilité, super-pouvoir)"""
    for pid, player in room.players.items():
        # Mise à jour du timer d'invincibilité
        if getattr(player, "invincible", False):
            player.invincibility_timer -= 1
            if player.invincibility_timer <= 0:
                player.invincible = False
                logger.info(f"Joueur {pid} n'est plus invincible")
        
        # Mise à jour du timer de super-pouvoir
        if getattr(player, "super_power_active", False):
            player.super_power_timer -= 1
            if player.super_power_timer <= 0:
                player.super_power_active = False
                logger.info(f"Super-pouvoir désactivé pour le joueur {pid}")

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
            if distance_squared < 30*30:
                # Si Pacman a le super-pouvoir et n'est pas invincible
                if getattr(pacman, "super_power_active", False):
                    collision_result["ghost_eaten"] = {"pacman": pacman, "ghost": ghost}
                    logger.info(f"Pacman mange le fantôme {ghost.id if hasattr(ghost, 'id') else 'unknown'}")
                    return collision_result
                # Sinon, si Pacman n'est pas invincible, il est touché
                elif not getattr(pacman, "invincible", False):
                    collision_result["pacman_hit"] = pacman
                    return collision_result
                    
    return collision_result

def eat_ghost(pacman, ghost, room):
    """Logique pour faire manger un fantôme par Pacman."""
    # Augmenter le score de Pacman
    pacman.score += 200
    
    # Marquer le fantôme comme mangé
    ghost.is_eaten = False # pour l'instant, je ne le marque pas comme mangé
        
    # Calculer une position de respawn au centre (adapté pour le serveur)
    center_x = 300  # Position centrale approximative
    center_y = 300  # Position centrale approximative
    ghost.respawn_target = (center_x, center_y)
    
    logger.info(f"Fantôme {getattr(ghost, 'id', 'unknown')} mangé par Pacman. Score: +200")
    
    return True

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
        "fruits": room.item_manager.fruits
    }

    return state


while True:
    connexion, address = s.accept()
    logger.info(f"Connecté à: {address}")
    logger.debug(f"Room Manager état actuel: {room_manager.rooms}")
    thread = threading.Thread(target=threaded_client, args=(connexion,address))
    thread.start()




