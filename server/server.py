import socket
import time
import sys
from _thread import start_new_thread
from rooms import RoomManager

import threading
from reseaux import Network
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

#Gestion de l'arrêt du serveur
def server_shutdown():
    print("Arrêt du serveur...")
    s.close()
    sys.exit(0)

#Gestion des joueurs inactifs

player_inactive_time = {}
def check_inactive_players():
    """Comment voir qu'un joueur est inactif ?
    Il garde la même position (normalement pas possible dans le vrai pacman, il avance tout le temps) ?
    ou l'utilisateur ne touche pas à une touche pendant x temps ? Je crois que le client envoie des données
     quoi qu'il arrive peut-être une modification à apporter au niveau de client"""

    current_time = time.time()
    for joueur, last_active in list(player_inactive_time.items()):
        print(joueur, last_active)

        if current_time - last_active > timeout:
            print(f"Joueur {joueur} inactif")
            del player_inactive_time[joueur]

def threaded_game_client(connexion, joueur_actuel, room_id):
    """
       Fonction permettant de gérer les connexions des clients
       :param connexion: socket de connexion
       :param joueur_actuel: joueur actuel (entier)
       :return:
    """
    print("OK")
    try:
        if not room_manager.room_exists(room_id):
            print("Partie introuvable")
            connexion.close()
            return
        room = room_manager.rooms[room_id]  # Récupération de la salle

        datas = {
        "players": [
                {"pos": [150, 150], "roles": "PacMan", "ip": address[0], "tcp_port": address[1]},
                {"pos": [950, 450], "roles": "Fantôme", "ip": None, "tcp_port": None},
                {"pos": [920, 450], "roles": "Fantôme", "ip": None, "tcp_port": None},
                {"pos": [950, 420], "roles": "Fantôme", "ip": None, "tcp_port": None},
                {"pos": [920, 420], "roles": "Fantôme", "ip": None, "tcp_port": None}
            ],
            "current_player": joueur_actuel # Permet d'identifier quel joueur est en train de se connecter
        }

        # Envoi des données initiales au client connecté
        connexion.send(str.encode(json.dumps(datas)))
        print("Envoi des données au client connecté")

        #Mettre à jour le temps d'inactivité dès que le joueur se connecte
        player_inactive_time[joueur_actuel] = time.time()

        while True:
            try:

                # Réception des données mises à jour par le client
                raw_data = connexion.recv(2048).decode()
                print("Raw data",raw_data)
                if not raw_data:
                    print(f"Déconnexion du joueur {joueur_actuel}")
                    break
                print(f"Reçu du joueur {joueur_actuel} : {raw_data}")
                # Si le client envoie la commande GET_POS, on renvoie l'état actuel
                if raw_data == "GET_POS":
                    print(f"Envoi des positions au joueur {joueur_actuel}")
                    connexion.sendall(json.dumps(datas).encode())
                    continue
                else:
                    print(f"Commande inconnue : {raw_data}")

                # Sinon, on considère que le client envoie des données JSON pour mettre à jour sa position
                all_players_updated = json.loads(raw_data)
                datas["players"][joueur_actuel] = all_players_updated["players"][joueur_actuel]

                # Renvoi les données mises à jour à tous les clients
                connexion.sendall(json.dumps(datas).encode())

                #Mettre à jour le temps d'inactivité
                player_inactive_time[joueur_actuel] = time.time()

            except Exception as erreur:
                print(f"Erreur avec le joueur {joueur_actuel} : {erreur}")
                break

        connexion.close()
        room.leave(joueur_actuel)  # Supprime le joueur de la salle
        print(f"Connexion fermée pour le joueur {joueur_actuel}")


    except Exception as e:
        print(f"Erreur dans la gestion de la partie : {e}")
        connexion.close()

def threaded_client(connexion):
    """
    Gère la création et la connexion aux parties.
    """
    try:
        raw_data = connexion.recv(2048).decode()
        if not raw_data:
            print("Client déconnecté avant d'envoyer des données")
            connexion.close()
            return

        data = json.loads(raw_data)
        if data["action"] == "create_party":
            #room_name = data["name"]
            room_name = "Test Room"
            room = room_manager.create_room(room_name = room_name,room_id= data["code"],player_capacity=max_players)
            print("data",data)
            room_id = data["code"]

            player_id = threading.get_ident()  # Identifiant unique pour le joueur
            # Le créateur rejoint la partie
            if room_manager.join(player_id, data["code"]):
                connexion.send(str.encode(json.dumps({"status": "ok", "room_id": room.identifier})))
                # Lancement du thread de jeu pour le créateur
                start_new_thread(threaded_game_client, (connexion, player_id, data["code"]))
            else:
                connexion.send(str.encode(json.dumps({"status": "full"})))
                connexion.close()

        elif data["action"] == "join_party":
            room_id = data["room_id"]
            player_id = threading.get_ident()  # Identifiant unique pour le joueur

            if room_manager.join(player_id, room_id):
                # Démarrer un thread pour le joueur
                start_new_thread(threaded_game_client, (connexion, player_id, room_id))
            else:
                print('pas ok')
                connexion.send(
                    str.encode(json.dumps({"status": "full" if room_manager.room_exists(room_id) else "not_found"})))
                connexion.close()
    except Exception as e:
        print(f"Erreur lors de la gestion d'un client : {e}")
        connexion.close()

while True:
    connexion, address = s.accept()
    print("Connecté à:", address)
    print("Room Manager",room_manager.rooms)
    thread = threading.Thread(target=threaded_client, args=(connexion,))
    thread.start()


