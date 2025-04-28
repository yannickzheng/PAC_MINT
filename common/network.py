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

    def send_command(self, request, message = None):
        """
        Méthode générique pour envoyer une commande au serveur et recevoir une réponse.
        :param request: La commande à envoyer
        :param message: le message à transmettre
        :return: La réponse du serveur.
        """
        # Envoi de la commande au serveur
        data = json.dumps({"command": request, "message": message})
        self.client.sendall(data.encode())
        #response = self.read_json_message()
        response = self.receive_j()


        return response

    def receive(self):
        return self.client.recv(Network.BUFFER_SIZE).decode()

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

    def receive_j(self):
        buffer = ""
        open_braces = 0
        close_braces = 0

        while True:
            data = self.client.recv(2048)
            if not data:
                raise ConnectionError("Socket closed")

            buffer += data.decode()

            # Compter les accolades
            open_braces += buffer.count('{')
            close_braces += buffer.count('}')

            # Si le nombre d'accolades ouvrantes = fermantes → JSON complet
            if open_braces > 0 and open_braces == close_braces:
                break

        return json.loads(buffer)
