import random
import time

from game.player import Player, PacMan, Ghost
from game.items import ServerItemManager
from common.global_variable import WIDTH, HEIGHT
"""Faire en sort qu'un joueur n'est présent que dans une seule salle"""

class RoomManager:

    """On instaure un nombre maximum de salles"""

    def __init__(self,room_capacity):
        self.rooms = {}
        self.room_capacity = room_capacity

    def create_room(self,player_capacity = 5, room_name = None):
        """Création d'une salle'"""

        # Par default, on dit que la capacité des rooms est de 5 joueurs max
        code = self.generate_unique_code()
        new_room = Room(player_capacity, room_name, code)
        self.rooms[new_room.code] = new_room
        return new_room

    def join(self, player_identifier, room_identifier, role = None):
        """Ajout d'un joueur dans une salle"""
        print(f"[DEBUG][RoomManager] join: player_id={player_identifier}, room_id={room_identifier}, role={role}")
        # Retirer le joueur de toutes les salles où il serait présent
        for room in self.rooms.values():
            #On regarde si le joueur est dans un salon
            if room.is_player_in_room(player_identifier):
                room.leave(player_identifier)
        #ATTENTION room_identifer est un str mais les clés du dictiononnaires rooms sont des int
        room = self.rooms.get(int(room_identifier))
        if room:
            result = room.join(player_identifier, role=role)
            return result  # On retourne l'objet réponse (ok ou erreur)
        return False

    def leave(self, player_identifier, room_identifier):
        """Suppression d'un joueur d'une salle"""
        room = self.rooms.get(room_identifier)
        if room:
            return room.leave(player_identifier)
        return False

    def remove_empty_rooms(self):
        """Suppression des salles vides"""
        for room_id, room in self.rooms.items():
            if room.is_empty():
                del self.rooms[room_id]

    def room_exists(self, room_id):
        """Check if a room exists in the manager."""
        return room_id in self.rooms

    def is_sender_in_room(self, sender_id, room_id):
        """Check if the sender is part of the specified room."""
        room = self.rooms.get(room_id)
        return room and room.is_player_in_room(sender_id)

    def send_udp(self, sender_id, room_id, message, sock):
        """
        Send data to all players in room, except sender with udp
        """
        if not self.room_exists(room_id):
            return False

        room = self.rooms.get(room_id)
        if not room:
            return False

        players = room.players

        for player_id in players:
            if player_id != sender_id:
                pass
                #mettre ici la fonction send utilisant udp

    def generate_unique_code(self):
        while True:
            code = random.randint(100000, 999999)
            if code not in self.rooms:
                return code

class Room:

    def __init__(self, player_capacity, room_name, code = None):
        """
        Création d'une salle'
        """
        self.player_capacity = player_capacity
        self.players = {} #  Exemple : {"pacman": Player(...), "fantome_1": Player(...)}
        self.room_name = room_name
        self.code = code
        self.initial_positions = {
            "pacman": (150, 150),
            "fantome_1": (WIDTH // 2 - 20, HEIGHT // 2 - 20),
            "fantome_2": (WIDTH // 2 + 20, HEIGHT // 2 - 20),
            "fantome_3": (WIDTH // 2 - 20, HEIGHT // 2 + 20),
            "fantome_4": (WIDTH // 2 + 20, HEIGHT // 2 + 20)
        }
        self.item_manager = ServerItemManager()
        self.chat_history = []

    def is_role_taken(self, role):
        """Vérifie si un rôle est déjà pris dans cette room."""
        return any(
            hasattr(p, "role") and p.role and p.role.lower() == role.lower()
            for p in self.players.values()
        )
    def update_position(self, role_key, new_pos):
        if role_key in self.players:
            self.players[role_key].update_position(new_pos)

    def is_full(self):
        if len(self.players) >= self.player_capacity:
            return True

    def is_empty(self):
        if len(self.players) == 0:
            return True

    def join(self, player_id, role=None):
        print(f"[DEBUG][Room] join: player_id={player_id}, role={role}")

        # --- Utilisation de is_role_taken ---
        if role and self.is_role_taken(role):
            taken_roles = [p.role for p in self.players.values() if p.role]
            print(f"[DEBUG][Room] join refusé: rôle {role} déjà pris. Rôles pris: {taken_roles}")
            return {"status": "error", "reason": "role_taken", "message": f"Le rôle '{role}' est déjà pris dans cette salle.", "taken_roles": taken_roles}  # Rôle déjà pris : refuse l’entrée

        if not self.is_full():
            position = self.initial_positions[role]

            if "pacman" in role.lower():
                player = PacMan(ip=None, tcp_port=None, position=position)
                player.id = player_id
            elif "fantome" in role.lower():
                player = Ghost(ip=None, tcp_port=None, position=position, role = role)
                player.id = player_id
            else:
                player = Player(ip=None, tcp_port=None, role=role, position=position)
                player.id = player_id

            self.players[player_id] = player
            return {"status": "ok", "message": "Joueur ajouté à la salle"}

        return {"status": "error", "reason": "room_full", "message": "La salle est pleine."}


    def leave(self, player_id):
        """Suppression d'un joueur de la salle"""
        if player_id in self.players:
            self.players.pop(player_id)
            return True

    def is_player_in_room(self, player_id):
        """Le joueur est il dans la salle?"""
        return player_id in self.players
    
    def add_chat_message(self, player_id, message):
        """Ajoute un message au chat de la room"""
        
        player_name = self.players[player_id].role if player_id in self.players else "Joueur"
        
        chat_message = {
            "player_id": player_id,
            "player_name": player_name,
            "message": message,
            "timestamp": time.time()
        }
        
        self.chat_history.append(chat_message)
        
        # On garde les 50 derniers messages
        if len(self.chat_history) > 50:
            self.chat_history = self.chat_history[-50:]
            
        return chat_message
    
    def get_chat_history(self, limit=20):
        """Retourne l'historique du chat (limité aux derniers messages)"""
        return self.chat_history[-limit:] if len(self.chat_history) > limit else self.chat_history