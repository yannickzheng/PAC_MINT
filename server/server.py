import socket
import time
import sys
from _thread import start_new_thread
from rooms import RoomManager
from protocols import Protocols

import threading

import json
import uuid

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
server = "localhost" # J'ai pris mon adresse IP wifi, il faudra mettre celle du serveur plus tard
port = 5555 # Port de communication

# Initialisation d'un RoomManager
room_manager = RoomManager(room_capacity=max_players)

# création d'un socket INET (IPV4) et un socket Stream (TCP)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Liaison du socket à l'adresse IP et au port définis précédemment
    s.bind((server, port))
except socket.error as e:
    print("Erreur de liaison du socket :")
    sys.exit(1)

# Nombre de connexions simultanées maximales
s.listen(max_players)
print("Serveur démarré, en attente de connexions...")

#Gestion de l'arrêt du serveur
def server_shutdown():
    print("Arrêt du serveur...")
    s.close()
    sys.exit(0)

def build_state(room, current_id, *, with_action=False):
    state = {
        "current_player_id": current_id,
        "players": [
            {
                "id": pid,
                "pos": p.position,
                "roles": p.role,
                "ip": p.ip,
                "tcp_port": p.tcp_port
            }
            for pid, p in room.players.items()
        ]
    }
    if with_action:
        state["action"] = "welcome"

        state["items"] = {
            "coins": room.item_manager.coins,
            "fruits": room.item_manager.fruits
        }


    return state

def threaded_game_client(connexion, joueur_actuel, room_id, address = None):
    """
       Fonction permettant de gérer les connexions des clients
       :param connexion: socket de connexion
       :param joueur_actuel: joueur actuel (entier)
       :return:
    """
    print(f"Connexion établie avec le joueur {joueur_actuel} depuis {address}")

    #Sécurité, on impose que room_id est bien un int
    room_id = int(room_id)

    try:
        # On vérifie que la salle existe bien sinon on ferme la session
        if not room_manager.room_exists(room_id):
            print("Partie introuvable")
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
        welcome = build_state(room, joueur_actuel, with_action=True)
        send_json(connexion, welcome)

        while True:
            try:
                #On écoute le client
                raw_data = recv_json(connexion)

                """
                if raw_data.get("command", False) == Protocols.Request.GET_POS :
                    json_data = json.dumps(datas)
                    connexion.send(json_data.encode())
                    #print("Coucouu",json_data)
                """

                if not raw_data.get("command", False):
                    print(f"Déconnexion du joueur {joueur_actuel}")
                    break
                #print(raw_data)
                if raw_data.get("command") == Protocols.Request.UPDATE_POSITION:
                    #print(raw_data)
                    payload = raw_data.get("message", {})
                    for pdata in payload.get("players", []):

                        pid = pdata["id"]
                        pos = pdata["pos"]
                        if pid in room.players:
                            player = room.players[pid]
                            player.update_position(pos)

                            # Vérifie la collecte d’items pour ce joueur (uniquement si c'est Pacman)
                            collected = room.item_manager.check_collision(player)
                            if collected["coins"]:
                                player.score += 10 * len(collected["coins"])
                            if collected["fruits"]:
                                player.score += 50 * len(collected["fruits"])
                                # Active le pouvoir si besoin (à gérer côté client aussi)

                    state = build_state(room, joueur_actuel, with_action=True)
                    send_json(connexion, state)

            except Exception as erreur:
                print(f"Erreur avec le joueur {joueur_actuel} : {erreur}")
                break

        connexion.close()
        room.leave(joueur_actuel)  # Supprime le joueur de la salle
        print(f"Connexion fermée pour le joueur {joueur_actuel}")


    except Exception as e:
        print(f"Erreur dans la gestion de la partie : {e}")
        connexion.close()

def threaded_client(connexion, address):
    """
    Gère la création et la connexion aux parties.
    """
    try:
        raw_data = recv_json(connexion)
        if not raw_data:
            print("Connexion interrompue avant la réception des données.")
            connexion.close()
            return

        data = raw_data
        if data["command"] == Protocols.Request.CREATE_GAME:
            print("game crée")

            #On crée la partie
            room_name = "Test Room"
            room = room_manager.create_room(room_name=room_name)
            room_code = room.code

            player_id = str(uuid.uuid4())   # Identifiant unique pour le joueur
            if room_manager.join(player_id, room_code) is not None:
                print("Test")
                #On envoie le code de la partie au joueur
                send_json(connexion, {"status": "ok", "code": room_code})
                start_new_thread(threaded_game_client, (connexion, player_id, room_code, address))
                #return
            else:
                send_json(connexion, {"status": "full"})
                connexion.close()

        elif data["command"] == Protocols.Request.JOIN_ROOM:
            #print(data)
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
        print(f"Erreur lors de la gestion d'un client : {e}")
        connexion.close()


while True:
    connexion, address = s.accept()
    print("Connecté à:", address)
    print("Room Manager",room_manager.rooms)
    thread = threading.Thread(target=threaded_client, args=(connexion,address))
    thread.start()




