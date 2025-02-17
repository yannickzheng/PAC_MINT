import uuid  #générer des identifiants uniques

"""Donne t'on un identifiant pour les players ?"""


class Room:

    def __init__(self, identifier, capacity, room_name):
        """
        Création d'une salle'
        """
        self.capacity = capacity
        self.players = set() #set pour éviter les doublons
        self.identifier = identifier
        self.room_name = room_name

    def is_full(self):
        if len(self.players) >= self.capacity:
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