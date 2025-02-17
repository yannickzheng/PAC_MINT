import uuid  #générer des identifiants uniques


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