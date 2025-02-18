import pygame
from global_variable import WIDTH, HEIGHT, CELL_SIZE
from map import MAP_DATA
class Player:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.coord = (x, y)
        self.color = (255, 0, 0)
        self.size = 20
        self.hitbox_size = 10
        self.image1 = pygame.image.load("images/pacman - right.png")
        self.image2 = pygame.image.load("images/pacman - left.png")
        self.image3 = pygame.image.load("images/pacman - up.png")
        self.image4 = pygame.image.load("images/pacman - down.png")
        self.image5 = pygame.image.load("images/red_ghost.png")
        self.is_pacman = role == "PacMan"
        self.is_phantom = role == "Fantôme"
        self.is_coin = role == "Pièce"
        self.score = 0

    def check_collision(self, players):
        """
        Vérifie si le joueur entre en collision avec un autre joueur en prenant en compte leur hitbox
        :param players: Liste des autres joueurs
        :return: True si collision, False sinon
        """
        for player in players:
            if player != self:
                # calcul de la distance au carré entre les centres des deux joueurs
                distance_squared = (self.x - player.x) ** 2 + (self.y - player.y) ** 2
                # il y a collision quand la distance entre les deux joueurs est inférieure à la somme de leur rayon
                if distance_squared < (self.hitbox_size + player.hitbox_size) ** 2:
                    return True
        return False

    def move(self, players):
        """
        Déplace le joueur en vérifiant les collisions avec les murs et les autres joueurs.
        :param players: Liste des autres joueurs
        """
        keys = pygame.key.get_pressed()
        cell_x = self.x // CELL_SIZE
        cell_y = self.y // CELL_SIZE

        new_x, new_y = self.x, self.y

        if (keys[pygame.K_LEFT]
                and self.x > 0
                and cell_x > 0
                and MAP_DATA[cell_y][(self.x - 2) // CELL_SIZE] == 0):
            new_x = self.x - 2

        if (keys[pygame.K_RIGHT]
                and self.x + 1 < WIDTH
                and cell_x > 0
                and MAP_DATA[cell_y][(self.x + 2) // CELL_SIZE] == 0):
            new_x = self.x + 2

        if (keys[pygame.K_UP]
                and self.y > 0
                and cell_y > 0
                and MAP_DATA[(self.y - 2) // CELL_SIZE][cell_x] == 0):
            new_y = self.y - 2

        if (keys[pygame.K_DOWN]
                and self.y - 1 < HEIGHT
                and cell_y > 0
                and MAP_DATA[(self.y + 2) // CELL_SIZE][cell_x] == 0):
            new_y = self.y + 2
        # anciennes coordonnées
        old_x, old_y = self.x, self.y
        # nouvelles coordonnées temporaires
        self.x, self.y = new_x, new_y
        # on vérifgie s'il y a collision
        if self.check_collision(players):
            # on annule le déplacement en cas de collision
            self.x, self.y = old_x, old_y
        else:
            # sinon on met à jour les coordonnées
            self.x, self.y = new_x, new_y
        self.update()
    def update(self):
        """
        Met à jour les coordonnées du joueur
        """
        self.coord = (self.x, self.y)
    def get_img_pacman(self):
        """
        Renvoie l'image du joueur en fonction de la direction
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            return self.image2
        if keys[pygame.K_RIGHT]:
            return self.image1
        if keys[pygame.K_UP]:
            return self.image3
        if keys[pygame.K_DOWN]:
            return self.image4
        return self.image1

    def get_img_phantom(self):
        """
        Renvoie l'image du joueur
        """
        return self.image5
    def draw(self, screen):
        """
        Dessine le joueur à l'écran
        :param screen: Surface d'affichage du jeu
        """
        if self.is_pacman:
            self.spawn(screen, self.get_img_pacman())
        elif self.is_phantom:
            self.spawn(screen,self.get_img_phantom())
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def spawn(self, screen, img):
        """
        Affiche l'image du joueur à l'écran
        :param screen: Surface d'affichage du jeu
        :param img: Image du joueur
        """
        screen.blit(img, (self.x, self.y))