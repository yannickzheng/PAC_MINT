import socket
import sys
from _thread import start_new_thread
import json


#Gestion de l'arrêt du serveur
def server_shutdown():
    print("Arrêt du serveur...")
    s.close()
    sys.exit(0)

# Adresse IP locale du serveur (ici le serveur est sur la même machine que le client, il doit être modifiable)
server = "localhost" # J'ai pris mon adresse IP wifi, il faudra mettre celle du serveur plus tard
port = 5555 # Port de communication

# Création d'un socket pour la communication sur IPV4 en utilisant le protocole TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Liaison du socket à l'adresse IP et au port définis précédemment
    s.bind((server, port))
except socket.error as e:
    str(e)

# Nombre de connexions simultanées maximales (ici 5)
s.listen(5)
print("En attente de connexion, serveur démarré")

# position initale des 5 joueurs
datas = {
    "players": [
        {"pos": [150, 150], "roles": "PacMan"},
        {"pos": [950, 450], "roles": "Fantôme"},
        {"pos": [920, 450], "roles": "Fantôme"},
        {"pos": [950, 420], "roles": "Fantôme"},
        {"pos": [920, 420], "roles": "Fantôme"}
    ],
    "current_player": 0 # Permet d'identifier quel joueur est en train de se connecter
}

def threaded_client(connexion, joueur_actuel):
    """
       Fonction permettant de gérer les connexions des clients
       :param connexion: socket de connexion
       :param joueur_actuel: joueur actuel (entier)
       :return:
    """
    # Envoi des données initiales au client connecté
    datas["current_player"] = joueur_actuel
    connexion.send(str.encode(json.dumps(datas)))

    while True:
        try:
            # Réception des données mises à jour par le client
            raw_data = connexion.recv(2048).decode()
            if not raw_data:
                print("Déconnexion")
                break

            # Reçoit les données du client et met à jour uniquement les informations du joueur correspondant.
            all_players_updated = json.loads(raw_data)
            datas["players"][joueur_actuel] = all_players_updated["players"][joueur_actuel]

            # Renvoi les données mises à jour à tous les clients
            connexion.sendall(json.dumps(datas).encode())
        except:
            break

    print(f"Connexion fermée pour le joueur {joueur_actuel}")
    connexion.close()


MAX_PLAYERS = 5 # Limite de joueurs
joueur_actuel = 0 # Initialisation du compteur de joueurs

while True:

    if joueur_actuel >= MAX_PLAYERS: # Si la limite de joueurs est atteinte
        print("Limite de joueurs atteinte.")
        break

    connexion, address = s.accept() # En attente d'une connexion
    print("Connecté à:", address)
    # Création d'un nouveau thread pour gérer la connexion de chaque client
    start_new_thread(threaded_client, (connexion, joueur_actuel))
    joueur_actuel += 1  # On passe au joueur suivant