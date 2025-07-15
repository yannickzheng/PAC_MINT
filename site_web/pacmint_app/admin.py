from django.contrib import admin

from .models import (Friend, Game, GameResult, Map, Player, Room, Room_Players,
                     Table_Score)

admin.site.register(Player)
admin.site.register(GameResult)
admin.site.register(Friend)
admin.site.register(Room)
admin.site.register(Room_Players)
admin.site.register(Game)
admin.site.register(Table_Score)
admin.site.register(Map)
