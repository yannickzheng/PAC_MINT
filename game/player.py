import pygame
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from map import MAP_DATA
import random
import string

class Player:
    def __init__(self, x, y, role, ip, tcp_port, udp_port = None):
        self.ip = ip
        self.tcp_port = int(tcp_port) if tcp_port else None
        #self.udp_port = int(udp_port) # Pas prise en compte encore de udp
        self.tcp_addr = (self.ip, self.tcp_port)
        #self.udp_addr = (self.ip, self.udp_port) # Pas prise en compte encore de udp

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
        self.image_super_left = pygame.image.load("images/Black Pacman-left.png")
        self.image_super_up = pygame.image.load("images/Black Pacman-up.png")
        self.image_super_down = pygame.image.load("images/Black Pacman-down.png")

        # Redimensionner toutes les images pour correspondre à Pac-Man normal
        self.image_super = pygame.transform.scale(self.image_super, (self.size, self.size))
        self.image_super_left = pygame.transform.scale(self.image_super_left, (self.size, self.size))
        self.image_super_up = pygame.transform.scale(self.image_super_up, (self.size, self.size))
        self.image_super_down = pygame.transform.scale(self.image_super_down, (self.size, self.size))

        self.is_pacman = role == "PacMan"
        self.is_phantom = role == "Fantôme"
        self.is_coin = role == "Pièce"
        self.score = 0
        self.super_power_active = False  # Par défaut, Pac-Man n'a pas le super pouvoir
        self.super_power_timer = 0  # Timer du super pouvoir initialisé à 0
        self.invincible = False  # Pac-Man ne commence pas invincible
        self.invincibility_timer = 0  # Timer pour gérer l'invincibilité

    def lose_life(self):
        """Fait perdre une vie à Pac-Man et l'active en mode invincible temporairement"""
        if self.invincible:
            return  # Ne perd pas de vie s'il est encore invincible

        if self.lives > 1:
            self.lives -= 1
            print(f"💥 Pac-Man touché ! Il lui reste {self.lives} vies.")

            self.invincible = True
            self.invincibility_timer = 180  # Environ 3 secondes à 60 FPS

        else:
            self.lives = 0
            print("Game Over ! Pac-Man a perdu toutes ses vies.")

    def check_collision(self, players):
        """Vérifie si le joueur entre en collision avec un autre joueur"""
        for player in players:
            if player != self:
                distance_squared = (self.x - player.x) ** 2 + (self.y - player.y) ** 2
                if distance_squared < (self.hitbox_size + player.hitbox_size) ** 2:
                    return True
        return False

    def check_ghost_collision(self, players):
        """Vérifie si Pac-Man entre en collision avec un fantôme"""

        if not self.is_pacman or self.invincible:
            return  # Si Pac-Man est invincible, il ne perd pas de vie

        player_rect = pygame.Rect(self.x, self.y, self.size, self.size)

        for player in players:
            if player.is_phantom:
                ghost_rect = pygame.Rect(player.x, player.y, player.size, player.size)

                if player_rect.colliderect(ghost_rect):
                    if self.super_power_active:
                        self.eat_ghost(player)
                    else:
                        self.lose_life()
                    break

    def activate_super_power(self, duration=200):
        """Active le super pouvoir immédiatement lorsque Pac-Man mange un fruit"""
        self.super_power_active = True  # Active le pouvoir
        self.super_power_timer = duration  # Durée du pouvoir (ex: 300 frames = 5 secondes à 60 FPS)
        self.speed = min(int(self.speed * 1.2), CELL_SIZE//5)
    def move(self, players):
        """Déplace Pac-Man en s'assurant qu'il ne traverse pas les murs"""
        # Gère le timer d'invincibilité
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False
                print("🛡️ Fin de l'invincibilité.")

        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        hitbox_offset = self.size // 4  #  Réduit la hitbox pour éviter l'entrée partielle dans les murs
        if self.super_power_active:
            self.super_power_timer -= 1
            if self.super_power_timer <= 0:
                self.super_power_active = False  # Désactive le super pouvoir après le temps écoulé
                self.speed = CELL_SIZE // 6  # Remet la vitesse normale
                print("⏳ Fin du super pouvoir ! Pac-Man redevient normal.")

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

        if self != controlled_player:  #  Vérifie que Pac-Man est bien le joueur actif
            return self.image1  # Garde son orientation actuelle

        keys = pygame.key.get_pressed()

        if self.super_power_active:  # Vérifie si le super pouvoir est actif
            if keys[pygame.K_LEFT]:
                return self.image_super_left
            if keys[pygame.K_RIGHT]:
                return self.image_super
            if keys[pygame.K_UP]:
                return self.image_super_up
            if keys[pygame.K_DOWN]:
                return self.image_super_down
            return self.image_super  # Par défaut, regarde à droite

        # Si pas de super pouvoir, on retourne les images normales
        if keys[pygame.K_LEFT]:
            return self.image2
        if keys[pygame.K_3]:
            return self.image1
        if keys[pygame.K_UP]:
            return self.image3
        if keys[pygame.K_DOWN]:
            return self.image4
        return self.image1  # Par défaut, Pac-Man regarde à droite

    def get_img_phantom(self):
        """Renvoie l'image du fantôme"""
        return self.image5

    def draw(self, screen, controlled_player):
        """Dessine Pac-Man ou un fantôme sur l'écran"""
        if self.is_pacman:
            self.spawn(screen, self.get_img_pacman(controlled_player))  # Passe `controlled_player`
        elif self.is_phantom:
            self.spawn(screen, self.image5)  # Les fantômes gardent leur image
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def spawn(self, screen, img):
        """Affiche Pac-Man ou un fantôme"""
        screen.blit(img, (self.x, self.y))



