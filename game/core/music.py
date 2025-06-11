from pygame import mixer

# Variables globales pour la musique
music_on = True
music_loaded = None

def init_music():
    global music_loaded
    if not mixer.get_init():
        mixer.init()
    mixer.music.set_volume(0.9)
    music_loaded = None

def play_music(path, volume=0.9):
    global music_loaded
    if music_loaded != path:
        mixer.music.load(path)
        music_loaded = path
    mixer.music.set_volume(volume)
    mixer.music.play(-1)
    if not music_on:
        mixer.music.pause()

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        mixer.music.unpause()
    else:
        mixer.music.pause()
