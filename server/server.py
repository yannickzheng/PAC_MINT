import socket
import time
import sys
from _thread import start_new_thread
from rooms import RoomManager

import threading

import json


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

        # Crée un dictionnaire avec les données des joueurs
        datas = {
            "current_player_id": joueur_actuel,
            "players": [
                {
                    "id": p_id,
                    "pos": p.position,
                    "roles": p.role,
                    "ip": p.ip,
                    "tcp_port": p.tcp_port
                }
                for p_id, p in room.players.items()
            ]
        }

        # Envoi des données initiales au client connecté
        connexion.send(str.encode(json.dumps(datas)))
        print("Envoi des données au client connecté")

        while True:
            try:
                raw_data = connexion.recv(2048).decode()
                if not raw_data:
                    print(f"Déconnexion du joueur {joueur_actuel}")
                    break

                if raw_data == "GET_POS":
                    connexion.sendall(json.dumps(datas).encode())
                    continue

                all_players_updated = json.loads(raw_data)
                for pdata in all_players_updated.get("players", []):
                    role = pdata["roles"]
                    pos = pdata["pos"]
                    for p in room.players.values():
                        if p.role == role:
                            p.update_position(pos)

                # Mettre à jour le paquet datas
                datas = {
                    "current_player": (address[0], address[1]),
                    "players": [
                        {
                            "pos": p.position,
                            "roles": p.role,
                            "ip": p.ip,
                            "tcp_port": p.tcp_port
                        } for p in room.players.values()
                    ]
                }

                connexion.sendall(json.dumps(datas).encode())


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
        raw_data = connexion.recv(2048).decode()
        if not raw_data:
            print("Connexion interrompue avant la réception des données.")
            connexion.close()
            return

        data = json.loads(raw_data)
        if data["action"] == "CREATE_GAME":

            #On crée la partie
            room_name = "Test Room"
            room = room_manager.create_room(room_name=room_name)
            room_code = room.code

            player_id = threading.get_ident()  # Identifiant unique pour le joueur
            if room_manager.join(player_id, room_code) is not None:

                #On envoie le code de la partie au joueur
                connexion.send(str.encode(json.dumps({"status": "ok", "code": room_code})))
                start_new_thread(threaded_game_client, (connexion, player_id, room_code, address))
            else:
                connexion.send(str.encode(json.dumps({"status": "full"})))
                connexion.close()

        elif data["action"] == "JOIN_GAME":
            print(data)
            room_id = data["code"]
            #player_id = threading.get_ident()
            player_id = 123
            if room_manager.join(player_id, room_id):
                start_new_thread(threaded_game_client, (connexion, player_id, room_id, address))
            else:
                connexion.send(
                    str.encode(json.dumps({"status": "full" if room_manager.room_exists(room_id) else "not_found"})))
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


