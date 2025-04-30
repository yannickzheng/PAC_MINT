import json
import socket

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
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.server_address)
        self.sockfile = self.client.makefile('r')  # ← pour readline()


    def receive_json(self):
        line = self.sockfile.readline()
        if not line:
            raise ConnectionError("Socket closed")
        return json.loads(line)

    def send_command(self, request, message=None):
        payload = {"command": request, "message": message}
        self.client.sendall(json.dumps(payload).encode() + b'\n')
        return self.receive_json()
