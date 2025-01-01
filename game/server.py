import socket
from _thread import *
from classes.player import tuple_to_str, str_to_tuple


#Adresse IP locale du serveur (ici le serveur est sur la même machine que le client, il doit être modifiable)
server = "192.168.31.143"
port = 5555

#Création d'un socket pour la communication sur IPV4 en utilisant le protocole TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    #Liaison du socket à l'adresse IP et au port définis précédemment
    s.bind((server, port))
except socket.error as e:
    str(e)

#Nombre de connexions simultanées maximales (ici 5)
s.listen(5)
print("En attente de connexion, serveur démarré")


#position initale des 2 joueurs
pos = [(0,0),(100,100)]
def threaded_client(connexion, joueur_actuel):
    """
    Fonction permettant de gérer les connexions des clients

    :param connexion: socket de connexion
    :param joueur_actuel: joueur actuel
    :return:
    """
    #Quand un client se connecte, le serveur lui envoie sa position initiale
    connexion.send(str.encode(tuple_to_str(pos[joueur_actuel])))
    response = ""
    run = True
    while run :
        try:
            #Le serveur reçoit les nouvelles positions du client et les met à jour dans pos
            data = str_to_tuple(connexion.recv(2048).decode())
            pos[joueur_actuel] = data

            #Si il n'y a pas de données reçues, on arrête la connexion
            if not data:
                print("Déconnexion")
                break
            else:
                #On envoie la position du joueur actuel à l'autre joueur
                if joueur_actuel == 1:
                    response = pos[0]
                else :
                    response = pos[1]

                print("Reçu:", data)
                print("Envoi:", response)

            connexion.sendall(str.encode(tuple_to_str(response))) #Envoi de la position du joueur actuel à l'autre joueur
        except:
            break

    print("Connexion perdue")
    connexion.close()

joueur_actuel = 0
while True:
    connexion, address = s.accept() #en attente d'une connexion
    print("Connecté à:", address)
    #création d'un nouveau thread pour gérer la connexion de chaque client
    start_new_thread(threaded_client, (connexion, joueur_actuel))
    joueur_actuel += 1 #On passe au joueur suivant