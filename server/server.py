import socket
import time
import sys
from _thread import start_new_thread
from reseaux import Network
import json


#Paramètres
timeout = 10 #temps en seconde pour considérer un joueur inactif
MAX_PLAYERS = 5 # Limite de joueurs
server = "localhost" # J'ai pris mon adresse IP wifi, il faudra mettre celle du serveur plus tard
port = 5555 # Port de communication

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

# création d'un socket INET (IPV4) et un socket Stream (TCP)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Liaison du socket à l'adresse IP et au port définis précédemment
    s.bind((server, port))
except socket.error as e:
    print("Erreur de liaison du socket :")
    sys.exit(1)

# Nombre de connexions simultanées maximales
s.listen(MAX_PLAYERS)
print("En attente de connexion, serveur démarré")

#
game_sessions = {} # Stocke les parties en cours

def threaded_game_client(connexion, joueur_actuel, game_code):
    """
       Fonction permettant de gérer les connexions des clients
       :param connexion: socket de connexion
       :param joueur_actuel: joueur actuel (entier)
       :return:
    """

    try:
        if game_code not in game_sessions:
            print("Partie introuvable")
            connexion.close()
            return
        game_data = game_sessions[game_code]
        datas = {
        "players": [
                {"pos": [150, 150], "roles": "PacMan"},
                {"pos": [950, 450], "roles": "Fantôme"},
                {"pos": [920, 450], "roles": "Fantôme"},
                {"pos": [950, 420], "roles": "Fantôme"},
                {"pos": [920, 420], "roles": "Fantôme"}
            ],
            "current_player": joueur_actuel # Permet d'identifier quel joueur est en train de se connecter
        }

        # Envoi des données initiales au client connecté
        connexion.send(str.encode(json.dumps(datas)))

        #Mettre à jour le temps d'inactivité dès que le joueur se connecte
        player_inactive_time[joueur_actuel] = time.time()

        while True:
            try:
                # Réception des données mises à jour par le client
                raw_data = connexion.recv(2048).decode()
                if not raw_data:
                    print(f"Déconnexion du joueur {joueur_actuel}")
                    break

                # Si le client envoie la commande GET_POS, on renvoie l'état actuel
                if raw_data == "GET_POS":
                    connexion.sendall(json.dumps(datas).encode())
                    continue

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

        print(f"Connexion fermée pour le joueur {joueur_actuel}")
        connexion.close()

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
        print(data)
        if data["action"] == "create_party":
            code = data["code"]
            if code not in game_sessions:
                game_sessions[code] = {"players": [], "current_player": 0}
                connexion.send(str.encode(json.dumps({"status": "ok", "code": code})))
                return

        elif data["action"] == "join_party":
            code = data["code"]
            if code in game_sessions and len(game_sessions[code]["players"]) < MAX_PLAYERS:
                joueur_actuel = game_sessions[code]["current_player"]
                game_sessions[code]["players"].append(joueur_actuel)
                game_sessions[code]["current_player"] += 1

                # Démarrer un thread pour ce joueur
                start_new_thread(threaded_game_client, (connexion, joueur_actuel, code))

                return
            else:
                connexion.send(str.encode(json.dumps({"status": "full" if code in game_sessions else "not_found"})))
                connexion.close()
                return
    except Exception as e:
        print(f"Erreur lors de la gestion d'un client : {e}")
        connexion.close()

while True:
    connexion, address = s.accept()
    print("Connecté à:", address)
    print(game_sessions)
    start_new_thread(threaded_client, (connexion,))

