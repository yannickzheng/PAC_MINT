import json
import socket
import select

class Network:
    SERVER_ADDRESS = "157.159.104.199"
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
        self.client.settimeout(5)  # Timeout de 5 secondes pour éviter de bloquer trop longtemps
        try:
            self.client.connect(self.server_address)
            self.client.settimeout(None)  # Remettre en mode bloquant après connexion
            self.sockfile = self.client.makefile('r') # Créer un fichier pour lire les données du socket
            print("Connexion au serveur établie!")
        except socket.timeout:
            print("ERREUR: Timeout de connexion au serveur. Vérifiez que le serveur est bien démarré.")
            raise ConnectionError("Timeout lors de la connexion au serveur")
        except ConnectionRefusedError:
            print("ERREUR: Connexion refusée. Vérifiez que le serveur est bien démarré.")
            raise ConnectionError("Connexion au serveur refusée")


    def receive_json(self):
        line = self.sockfile.readline()
        if not line:
            raise ConnectionError("Socket closed")
        return json.loads(line)

    def send_command(self, request, message=None):
        payload = {"command": request, "message": message}
        self.client.sendall(json.dumps(payload).encode() + b'\n')
        return self.receive_json()
    
    def send_command_async(self, request, message=None):
        """Envoie une commande au serveur sans attendre de réponse."""
        payload = {"command": request, "message": message}
        try:
            self.client.sendall(json.dumps(payload).encode() + b'\n')
        except Exception as e:
            print(f"Erreur lors de l'envoi de la commande asynchrone : {e}")

    def has_data_waiting(self):
        """Vérifie s'il y a des données en attente sans bloquer"""
        
        ready, _, _ = select.select([self.client], [], [], 0)
        return len(ready) > 0
    
    def receive_json_non_blocking(self):
        """Reçoit des données JSON de manière non-bloquante"""
        if self.has_data_waiting():
            return self.receive_json()
        return None

    def close(self):
        try:
            if hasattr(self, "sockfile") and self.sockfile:
                self.sockfile.close()
        except Exception:
            pass
        try:
            if hasattr(self, "sock") and self.sock:
                self.sock.close()
        except Exception:
            pass
