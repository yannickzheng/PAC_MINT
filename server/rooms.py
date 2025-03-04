import uuid  #générer des identifiants uniques

"""Faire en sort qu'un joueur n'est présent que dans une seule salle"""

class RoomManager:

    """On instaure un nombre maximum de salles"""

    def __init__(self,room_capacity):
        self.rooms = {}
        self.room_capacity = room_capacity

    def create_room(self, room_name,room_id,player_capacity = 5):
        """Création d'une salle'"""

        # Par default, on dit que la capacité des rooms est de 5 joueurs max

        new_room = Room(room_id, player_capacity, room_name)
        self.rooms[room_id] = new_room
        return new_room

    def join(self, player_identifier, room_identifier):
        """Ajout d'un joueur dans une salle"""
        # Retirer le joueur de toutes les salles où il serait présent
        for room in self.rooms.values():
            if room.is_player_in_room(player_identifier):
                room.leave(player_identifier)
        room = self.rooms.get(room_identifier)
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

class Room:

    def __init__(self, identifier, player_capacity, room_name):
        """
        Création d'une salle'
        """
        self.player_capacity = player_capacity
        self.players = set() #set pour éviter les doublons
        self.identifier = identifier
        self.room_name = room_name

    def is_full(self):
        if len(self.players) >= self.player_capacity:
            return True

    def is_empty(self):
        if len(self.players) == 0:
            return True

    def join(self, player_id):
        """Ajout d'un joueur dans la salle"""
        if not self.is_full():
            self.players.add(player_id)
            return True

    def leave(self, player_id):
        """Suppression d'un joueur de la salle"""
        if player_id in self.players:
            self.players.remove(player_id)
            return True

    def is_player_in_room(self, player_id):
        """Le joueur est il dans la salle?"""
        return player_id in self.players