import socket
from _thread import start_new_thread
from player import tuple_to_str, str_to_tuple, triple_to_str

import json

# Adresse IP locale du serveur (ici le serveur est sur la même machine que le client, il doit être modifiable)
server = "192.168.1.13"  # J'ai pris l'adresse IP de ma carte réseau
port = 5555

# Création d'un socket pour la communication sur IPV4 en utilisant le protocole TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Liaison du socket à l'adresse IP et au port défini précédemment
    s.bind((server, port))
except socket.error as e:
    str(e)

# Nombre de connexions simultanées maximales (ici 5)
s.listen(5)
print("En attente de connexion, serveur démarré")

# position initale des 5 joueurs
pos = [(100, 100), (200, 200), (300, 300), (400, 400), (500, 500)]
datas = {
    "players": [
        {"pos": [100, 100], "roles": "PacMan"},
        {"pos": [200, 200], "roles": "Fantôme"},
        {"pos": [300, 300], "roles": "Fantôme"},
        {"pos": [400, 400], "roles": "Fantôme"},
        {"pos": [500, 500], "roles": "Fantôme"}
    ],
    "current_player": 0
}


def threaded_client(connexion, joueur_actuel):
    """
    Fonction permettant de gérer les connexions des clients
    :param connexion: socket de connexion
    :param joueur_actuel: joueur actuel (int)
    :return:
    """
    # Quand un client se connecte, il envoie au serveur sa position initiale
    #    connexion.send(str.encode(tuple_to_str(pos[joueur_actuel])))

    datas["current_player"] = joueur_actuel
    connexion.send(str.encode(json.dumps(datas)))
    run = True
    while run:
        try:
            # Le serveur reçoit les nouvelles positions du client et les met à jour dans pos
            datas["current_player"] = joueur_actuel
            raw_data = connexion.recv(2048).decode()
            all_players_updated = json.loads(raw_data)
            datas["players"][joueur_actuel] = all_players_updated[joueur_actuel]
            # data = str_to_tuple(connexion.recv(2048).decode())
            # pos[joueur_actuel] = data

            # Si il n'y a pas de données reçues, on arrête la connexion
            if not datas[joueur_actuel]:
                print("Déconnexion")
                break
            else:

                # On envoie la position du joueur actuel à l'autre joueur
                #                if joueur_actuel == 1:
                #                   response = pos[0]
                #              else:
                #                 response = pos[1]

                #                print("Reçu:", data)
                #               print("Envoi:", response)
                # Envoi de la position du joueur actuel à l'autre joueur
                connexion.sendall(json.dumps(datas))

        #            connexion.sendall(str.encode(tuple_to_str(response)))
        except:
            break

    print("Connexion perdue")
    connexion.close()


joueur_actuel = 0

while True:
    connexion, address = s.accept()  # en attente d'une connexion
    print("Connecté à:", address)
    # création d'un nouveau thread pour gérer la connexion de chaque client
    start_new_thread(threaded_client, (connexion, joueur_actuel))
    joueur_actuel += 1  # On passe au joueur suivant
