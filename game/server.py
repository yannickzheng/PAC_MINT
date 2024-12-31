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


#Liste des positions des joueurs
pos = [(0,0),(100,100)]
def threaded_client(connexion, joueur_actuel):
    connexion.send(str.encode(tuple_to_str(pos[joueur_actuel])))
    response = ""
    run = True
    while run :
        try:
            # Réception des données du client
            data = str_to_tuple(connexion.recv(2048).decode())
            pos[joueur_actuel] = data


            if not data:
                print("Déconnexion")
                break
            else:
                if joueur_actuel == 1:
                    response = pos[0]
                else :
                    response = pos[1]

                print("Reçu:", data)
                print("Envoi:", response)

            connexion.sendall(str.encode(tuple_to_str(response)))
        except:
            break

    print("Connexion perdue")
    connexion.close()

joueur_actuel = 0
while True:
    #Acceptation de la connexion
    connexion, address = s.accept()
    print("Connecté à:", address)

    start_new_thread(threaded_client, (connexion, joueur_actuel))
    joueur_actuel += 1