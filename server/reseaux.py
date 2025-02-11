import json
import socket
import random
import string

def generate_unique_code():
    """Génère un code aléatoire unique pour une nouvelle partie"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return code

class Network:
    def __init__(self):
        # La classe pour une partie
        """
        Initialisation de la classe :
        - Création d'un socket
        - Connexion au serveur
        - Récupération de la position initiale du joueur
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket TCP/IP
        self.server = "localhost" #Adresse IP du serveur (ici le serveur est sur la même machine que le client, à l'avenir il devra avoir une adresse IP fixe)
        self.port = 5555 #Port de communication
        self.address = (self.server, self.port)
        self.pos = self.connect() #Permet d'établir une connexion avec le serveur et de récupérer la position initiale du joueur
        self.game_code = ""

    def get_pos(self):
        """
        Renvoie la position actuelle du joueur
        """
        return self.pos

    def connect(self):
        """
        Etablit une connexion avec le serveur :
        -En cas de  succès, reçoit une donnée initiale telle que la positon du joueur
        -En cas d'échec, la connexion est fermée
        Renvoie les données reçues du serveur après la connexion (décodées en chaîne de caractères)
        """

        self.client.connect(self.address) #Connexion au serveur
        return self.client.recv(2048).decode() #Récupération des données initiales du serveur (taille max = 2048 octets)


    def send(self, data):
        """
        Envoie des données au serveur et attend une réponse
        -Les données envoyés sont converties en bytes
        :param data: données à envoyer au serveur
        :return: données reçues du serveur (décodées en chaîne de caractères)
        """
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048*4).decode()
        except socket.error as e:
            print(e)

    def create_party(self):
        """Crée une nouvelle partie"""
        code = generate_unique_code()
        self.send(json.dumps({"action":"create_party", "code": code})) #
        self.game_code = code
        return code

    def join_party(self, code):
        """Rejoint une partie existante"""
        self.send(json.dumps({"action":"join_party", "code": code}))
        self.game_code = code
        return True