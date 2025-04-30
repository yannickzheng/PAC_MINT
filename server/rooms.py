import uuid  #générer des identifiants uniques
import json
import random
import string
from game.player import Player
from game.items import ServerItemManager

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

    def join(self, player_identifier, room_identifier):
        """Ajout d'un joueur dans une salle"""
        # Retirer le joueur de toutes les salles où il serait présent
        for room in self.rooms.values():
            #On regarde si le joueur est dans un salon
            if room.is_player_in_room(player_identifier):
                room.leave(player_identifier)
        #ATTENTION room_identifer est un str mais les clés du dictiononnaires rooms sont des int
        room = self.rooms.get(int(room_identifier))
        if room:
            return room.join(player_identifier)
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
        """Crée une nouvelle partie"""
        #ode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = 111
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
            "fantome_1": (950, 450),
            "fantome_2": (920, 450),
            "fantome_3": (950, 420),
            "fantome_4": (920, 420)
        }
        self.item_manager = ServerItemManager()


    def update_position(self, role_key, new_pos):
        if role_key in self.players:
            self.players[role_key].update_position(new_pos)

    def is_full(self):
        if len(self.players) >= self.player_capacity:
            return True

    def is_empty(self):
        if len(self.players) == 0:
            return True

    def join(self, player_id):
        if not self.is_full():
            # Déterminer le rôle en fonction de l'ordre d'arrivée
            role_keys = list(self.initial_positions.keys())
            role = role_keys[len(self.players)]  # ex : "pacman", "fantome_1", etc.
            position = self.initial_positions[role]
            player = Player(ip=None, tcp_port=None, role=role, position=position)
            self.players[player_id] = player
            return True
        return False

    def leave(self, player_id):
        """Suppression d'un joueur de la salle"""
        if player_id in self.players:
            self.players.pop(player_id)
            return True

    def is_player_in_room(self, player_id):
        """Le joueur est il dans la salle?"""
        return player_id in self.players