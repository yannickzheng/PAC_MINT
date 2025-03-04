import json
import socket

class Client:

    """Gère la connexion au serveur (TCP/UDP), envoie et reçoit des messages, il sert juste à communiquer avec le serveur"""
    def __init__(self,server_host,server_port_tcp=5555,server_port_udp=1234,client_port_udp=1235):
        """

        """
        self.server_tcp = (server_host, server_port_tcp)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.identifier = None  # ID unique du joueur
        self.room_id = None  # ID de la salle dans laquelle le joueur est connecté

        try:
            self.client.connect(self.server_tcp)
            print(f"Connecté au serveur {server_host}:{server_port_tcp}")
        except Exception as e:
            print(f"Erreur de connexion au serveur: {e}")

    def send(self, data):
        """Envoie des données au serveur et reçoit une réponse"""
        try:
            self.client.send(json.dumps(data).encode())
            return json.loads(self.client.recv(4096).decode())
        except socket.error as e:
            print(f"Erreur d'envoi des données : {e}")
            return None


    def create_room(self):
        """Crée une salle de jeu et récupère le code de la partie"""
        response = self.send({"action": "create_party"})
        if response and response.get("status") == "ok":
            self.room_id = response["code"]
            print(f"Partie créée avec le code: {self.room_id}")
            return self.room_id
        return None


    def join_room(self, code):
        """Rejoint une salle existante"""
        response = self.send({"action": "join_party", "code": code})
        if response and response.get("status") == "ok":
            self.room_id = code
            print(f"Rejoint la partie {code}")
            return True
        elif response and response.get("status") == "full":
            print("La salle est pleine")
        else:
            print("Salle introuvable")
        return False

    def get_game_state(self):
        """À FAIRE : Ajouter une vérification pour s'assurer que le joueur est bien connecté à une partie"""
        return self.send({"action": "get_state", "code": self.room_id})

    def update_position(self, player_data):
        """À FAIRE : Ajouter une condition pour vérifier que `self.room_id` est défini avant d'envoyer les données"""
        return self.send({"action": "update_position", "code": self.room_id, "player_data": player_data})




