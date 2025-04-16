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

    def read_json_message(self):
        """Lit un message JSON complet terminé par '\n'."""
        buffer = ""
        while True:
            chunk = self.client.recv(2048).decode()
            if not chunk:
                break
            buffer += chunk
            if '\n' in buffer:
                break
        try:
            return json.loads(buffer.strip())
        except json.JSONDecodeError as e:
            print(f"[Erreur JSON] {e}\nMessage reçu (tronqué ?) : {buffer}")
            return None

    def send_command(self, command):
        """
        Méthode générique pour envoyer une commande au serveur et recevoir une réponse.
        :param command: La commande à envoyer.
        :return: La réponse du serveur.
        """
        # Envoi de la commande au serveur
        self.client.sendall(command.encode())
        response = self.read_json_message()
        print("reponse finisant par \n",response)

        return response

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