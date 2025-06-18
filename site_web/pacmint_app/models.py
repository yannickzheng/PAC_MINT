from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)  # Non-nullable
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Score(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.value}"

class Map(models.Model):
    map_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    difficulty = models.CharField(max_length=20, choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")])
    layout_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Friend(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_of")
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("blocked", "Blocked")])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'friend')

    def __str__(self):
        return f"{self.player.username} -> {self.friend.username} ({self.status})"

class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hosted_rooms")
    max_players = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Room_Players(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_players")
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_rooms")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'player')

    def __str__(self):
        return f"{self.player.username} in {self.room.name}"

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="games")
    map = models.ForeignKey(Map, on_delete=models.CASCADE, related_name="games")
    status = models.CharField(max_length=20, choices=[("waiting", "Waiting"), ("in_progress", "In Progress"), ("finished", "Finished")])
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_games")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Game {self.game_id} - {self.status}"

class Table_Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="scores")
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scores")
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game', 'player')

    def __str__(self):
        return f"{self.player.username} - {self.score} pts in Game {self.game.game_id}"