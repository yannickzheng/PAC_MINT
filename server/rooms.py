import uuid  #générer des identifiants uniques

"""Donne t'on un identifiant pour les players ?"""
"""Faire en sort qu'un joueur n'est présent que dans une seule salle"""


class RoomManager:

    """On instaure un nombre maximum de salles"""

    def __init__(self,room_capacity):
        self.rooms = {}
        self.room_capacity = room_capacity

    def create_room(self, room_name, player_capacity = 5):
        """Création d'une salle'"""

        # Par default, on dit que la capacité des rooms est de 5 joueurs max

        identifier = str(uuid.uuid4())
        new_room = Room(identifier, player_capacity, room_name)
        self.rooms[identifier] = new_room
        return new_room

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

    def join(self, player):
        """Ajout d'un joueur dans la salle"""
        if not self.is_full():
            self.players.add(player)
            return True

    def leave(self, player):
        """Suppression d'un joueur de la salle"""
        if player in self.players:
            self.players.remove(player)
            return True

    def is_player_in_room(self, player):
        """Le joeur est il dans la salle?"""
        return player in self.players