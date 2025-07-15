from django.contrib import admin
from .models import (
    Player,
    GameResult,
    Friend,
    Room,
    Room_Players,
    Game,
    Table_Score,
    Map,
)

admin.site.register(Player)
admin.site.register(GameResult)
admin.site.register(Friend)
admin.site.register(Room)
admin.site.register(Room_Players)
admin.site.register(Game)
admin.site.register(Table_Score)
admin.site.register(Map)
