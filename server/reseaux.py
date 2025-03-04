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
    SERVER_ADDRESS = "localhost"  # Constante pour l'adresse IP du serveur
    SERVER_PORT = 5555  # Constante pour le port
    BUFFER_SIZE = 2048  # Taille du buffer pour les messages reçus

    def __init__(self):
        # La classe pour une partie
        """
        Initialisation de la classe :
        - Création d'un socket
        - Connexion au serveur
        - Récupération de la position initiale du joueur
        """
        print("Connexion au client")
        self.client = None
        self.server_address = (self.SERVER_ADDRESS, self.SERVER_PORT)
        self.player_position = ""
        self.game_code = ""
        self._initialize_connection()


    def _initialize_connection(self):
            """
            Configure le socket client et établit la connexion avec le serveur.
            """
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket TCP/IP
            try:
                self.client.connect(self.server_address)  # Connexion au serveur
                print(f"Connecté au serveur {self.SERVER_ADDRESS}:{self.SERVER_PORT}")
            except socket.error as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
                raise

    def send_command(self, command):
        """
        Méthode générique pour envoyer une commande au serveur et recevoir une réponse.
        :param command: La commande à envoyer.
        :return: La réponse du serveur.
        """
        print(f"Envoi de la commande '{command}' au serveur")
        self.client.sendall(command.encode())
        response = self.client.recv(self.BUFFER_SIZE).decode()
        print(f"Réponse reçue : {response}")
        return response

    def get_pos(self):
        """
        Récupère et retourne la position actuelle du joueur depuis le serveur.
        """
        return self.send_command("GET_POS")

    def connect(self):
        """
        Etablit une connexion avec le serveur :
        -En cas de  succès, reçoit une donnée initiale telle que la positon du joueur
        -En cas d'échec, la connexion est fermée
        Renvoie les données reçues du serveur après la connexion (décodées en chaîne de caractères)
        """
        try:
            #(self.client.connect(self.address)) #Connexion au serveur
            print("Connecté au serveur correctement")
            """
            data = self.client.recv(2048).decode() #Récupération des données initiales du serveur (taille max = 2048 octets)
            if data:
                self.pos = data
            else:
                print("Aucune donnée reçue lors de la connexion initiale")
            """
        except Exception as e:
            print(f"Erreur lors de la connexion {e}")

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
        response = self.send(json.dumps({"action":"create_party", "code": code})) #
        self.game_code = code
        return code

    def join_party(self, code):
        """Rejoint une partie existante"""
        self.send(json.dumps({"action":"join_party", "code": code}))
        self.game_code = code
        return True