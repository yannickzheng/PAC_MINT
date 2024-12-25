import socket
import sys
from _thread import *

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

def threaded_client(connexion):
    response = ""
    run = True
    while run :
        try:
            #Réception des données du client
            data = connexion.recv(2048*4)
            response = data.decode('utf-8') #Décodage des données reçues

            if not data:
                print("Déconnexion")
                break
            else:
                print("Reçu:", response)
                print("Envoi:", response)
            connexion.sendall(str.encode(response))
        except:
            break


while True:
    #Acceptation de la connexion
    connexion, address = s.accept()
    print("Connecté à:", address)
    start_new_thread(threaded_client, (connexion,))