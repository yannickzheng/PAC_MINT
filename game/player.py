import pygame
from global_variable import WIDTH, HEIGHT, CELL_SIZE
from map import MAP_DATA

class Player:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.coord = (x, y)
        self.color = (255, 0, 0)
        self.size = CELL_SIZE  # Pac-Man doit être basé sur `CELL_SIZE`
        self.hitbox_size = CELL_SIZE // 2
        self.speed = CELL_SIZE // 6  # Pac-Man bouge par petits pas
        self.lives = 3  # Pac-Man commence avec 3 vies
    #Chargement des images
        self.image1 = pygame.image.load("images/pacman - right.png")
        self.image2 = pygame.image.load("images/pacman - left.png")
        self.image3 = pygame.image.load("images/pacman - up.png")
        self.image4 = pygame.image.load("images/pacman - down.png")
        self.image5 = pygame.image.load("images/red_ghost.png")
        self.image_super = pygame.image.load("images/Black Pacman.png")
        self.image_super_left = pygame.transform.flip(self.image_super, True, False)
        self.image_super_up = pygame.transform.rotate(self.image_super, 90)
        self.image_super_down = pygame.transform.rotate(self.image_super, -90)
        self.is_pacman = role == "PacMan"
        self.is_phantom = role == "Fantôme"
        self.is_coin = role == "Pièce"
        self.score = 0

    def check_collision(self, players):
        """Vérifie si le joueur entre en collision avec un autre joueur"""
        for player in players:
            if player != self:
                distance_squared = (self.x - player.x) ** 2 + (self.y - player.y) ** 2
                if distance_squared < (self.hitbox_size + player.hitbox_size) ** 2:
                    return True
        return False

    def move(self, players):
        """Déplace Pac-Man en s'assurant qu'il ne traverse pas les murs"""
        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        hitbox_offset = self.size // 4  #  Réduit la hitbox pour éviter l'entrée partielle dans les murs

        #  Vérifie plusieurs points autour de Pac-Man pour détecter un mur
        def is_wall(x, y):
            return (
                    MAP_DATA[y // CELL_SIZE][x // CELL_SIZE] == 1 or  # Point Haut-Gauche
                    MAP_DATA[y // CELL_SIZE][(x + self.size - hitbox_offset) // CELL_SIZE] == 1 or  # Point Haut-Droit
                    MAP_DATA[(y + self.size - hitbox_offset) // CELL_SIZE][x // CELL_SIZE] == 1 or  # Point Bas-Gauche
                    MAP_DATA[(y + self.size - hitbox_offset) // CELL_SIZE][
                        (x + self.size - hitbox_offset) // CELL_SIZE] == 1  # Point Bas-Droit
            )

        #  Pac-Man ne peut pas traverser les murs
        if self.is_pacman:
            if keys[pygame.K_LEFT] and self.x > 0:
                if not is_wall(self.x - self.speed, self.y):
                    new_x -= self.speed

            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH:
                if not is_wall(self.x + self.speed, self.y):
                    new_x += self.speed

            if keys[pygame.K_UP] and self.y > 0:
                if not is_wall(self.x, self.y - self.speed):
                    new_y -= self.speed

            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT:
                if not is_wall(self.x, self.y + self.speed):
                    new_y += self.speed

        #  Les Fantômes ne sont PAS bloqués par les murs
        elif self.is_phantom:
            if keys[pygame.K_LEFT] and self.x > 0:
                if not is_wall(self.x - self.speed, self.y):
                    new_x -= self.speed

            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH:
                if not is_wall(self.x + self.speed, self.y):
                    new_x += self.speed

            if keys[pygame.K_UP] and self.y > 0:
                if not is_wall(self.x, self.y - self.speed):
                    new_y -= self.speed

            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT:
                if not is_wall(self.x, self.y + self.speed):
                    new_y += self.speed

        #  Vérification des collisions avec les autres joueurs
        old_x, old_y = self.x, self.y
        self.x, self.y = new_x, new_y

        if self.check_collision(players):
            self.x, self.y = old_x, old_y  #  Annule le déplacement en cas de collision avec un autre joueur
        else:
            self.update()  #  Met à jour les coordonnées si le déplacement est valide

    def update(self):
        """Met à jour les coordonnées du joueur"""
        self.coord = (self.x, self.y)

    def get_img_pacman(self, controlled_player):
        """Renvoie l'image de Pac-Man en fonction de la direction uniquement si c'est le joueur contrôlé"""

        #  Vérifie que Pac-Man est bien le joueur contrôlé
        if not self.is_pacman or self != controlled_player:
            return self.image1  #  Garde son orientation actuelle

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            return self.image2
        if keys[pygame.K_RIGHT]:
            return self.image1
        if keys[pygame.K_UP]:
            return self.image3
        if keys[pygame.K_DOWN]:
            return self.image4
        return self.image1  #  Par défaut, Pac-Man regarde à droite

    def get_img_phantom(self):
        """Renvoie l'image du fantôme"""
        return self.image5

    def draw(self, screen, controlled_player):
        """Dessine Pac-Man ou un fantôme sur l'écran"""
        if self.is_pacman:
            self.spawn(screen, self.get_img_pacman(controlled_player))  #  Passe `controlled_player`
        elif self.is_phantom:
            self.spawn(screen, self.image5)  # Les fantômes gardent leur image
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def spawn(self, screen, img):
        """Affiche Pac-Man ou un fantôme"""
        screen.blit(img, (self.x, self.y))
