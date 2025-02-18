
#Un item est un objet que PacMan peut ramasser.
#Il s'agit de soit d'une pièce qui augmente son score
#ou d'un super pouvoir qui lui permet de manger les fantômes pendant un certain temps.
#soit une pièce soit un super pouvoir, type : boost ou non boost (si c'est un super pouvoir alors
    #il est boost),
    #Pour le système de super pouvoir, on peut utiliser un système de tick, quand PacMan ramasse un super
    #pouvoir, on va attribuer la possibilité à pacman de manger les fantômes pendant un certain nombre de ticks
class Items:
    def __init__(self, nom, type, color):
        self.nom = nom
        self.type = type
        self.color = color


    def traitement_objet(self):
        if self == "super_pouvoir":
            pass