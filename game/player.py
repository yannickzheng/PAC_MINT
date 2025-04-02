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
        self.hitbox_size = int(self.size * 0.5)  # au lieu de 0.4
        self.speed = CELL_SIZE // 6  # Pac-Man bouge par petits pas
        self.lives = 3  # Pac-Man commence avec 3 vies
    #Chargement des images
        self.image_right = pygame.image.load("images/pacman - right.png")
        self.image_left = pygame.image.load("images/pacman - left.png")
        self.image_up = pygame.image.load("images/pacman - up.png")
        self.image_down = pygame.image.load("images/pacman - down.png")
        self.image_red_ghost = pygame.image.load("images/red_ghost.png")

        self.image_super_right = pygame.image.load("images/Black Pacman.png")
        self.image_super_left = pygame.image.load("images/Black Pacman-left.png")
        self.image_super_up = pygame.image.load("images/Black Pacman-up.png")
        self.image_super_down = pygame.image.load("images/Black Pacman-down.png")

        # Redimensionner toutes les images pour correspondre à Pac-Man normal
        self.image_right = pygame.transform.scale(self.image_right, (self.size, self.size))
        self.image_left = pygame.transform.scale(self.image_left, (self.size, self.size))
        self.image_up = pygame.transform.scale(self.image_up, (self.size, self.size))
        self.image_down = pygame.transform.scale(self.image_down, (self.size, self.size))
        self.image_red_ghost = pygame.transform.scale(self.image_red_ghost, (self.size, self.size))

        #Redimensionner les images de super Pacman
        self.image_super_right = pygame.transform.scale(self.image_super_right, (self.size, self.size))
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

            self.invincible = True
            self.invincibility_timer = 180  # Environ 3 secondes à 60 FPS

        else:
            self.lives = 0

    def check_collision(self, players):
        """Empêche Pac-Man de traverser d'autres joueurs (selon leur type)"""
        for player in players:
            if player != self:
                if self.is_pacman and player.is_phantom:
                    continue  # Pac-Man peut traverser les fantômes (logique de collision gérée ailleurs)

                dx = (self.x + self.size // 2) - (player.x + player.size // 2)
                dy = (self.y + self.size // 2) - (player.y + player.size // 2)
                distance_squared = dx * dx + dy * dy
                radius_sum = self.hitbox_size + player.hitbox_size

                if distance_squared < radius_sum ** 2:
                    return True
        return False

    def handle_collisions_with_players(self, players):
        """Gère les collisions entre Pac-Man et les fantômes, via distance"""
        if not self.is_pacman or self.invincible:
            return

        pacman_center = (self.x + self.size // 2, self.y + self.size // 2)

        for player in players:
            if player.is_phantom:
                ghost_center = (player.x + player.size // 2, player.y + player.size // 2)

                dx = pacman_center[0] - ghost_center[0]
                dy = pacman_center[1] - ghost_center[1]
                distance_squared = dx * dx + dy * dy
                combined_radius = self.hitbox_size + player.hitbox_size
                combined_squared = combined_radius ** 2

                # 💬 DEBUG LOG
                print(f"🔎 Test collision Pac-Man <-> Fantôme")
                print(f"    Distance²: {distance_squared}")
                print(f"    Rayon combiné²: {combined_squared}")
                print(
                    f"    Résultat: {'✅ COLLISION' if distance_squared <= combined_squared else '❌ PAS de collision'}")

                if distance_squared <= combined_squared:
                    print("💥 COLLISION DÉTECTÉE !")
                    if self.super_power_active:
                        self.eat_ghost(player, players)
                    else:
                        self.lose_life()
                    break

    def activate_super_power(self, duration=200):
        """Active le super pouvoir immédiatement lorsque Pac-Man mange un fruit"""
        self.super_power_active = True  # Active le pouvoir
        self.super_power_timer = duration  # Durée du pouvoir (ex: 300 frames = 5 secondes à 60 FPS)
        self.speed = min(int(self.speed * 1.2), CELL_SIZE//5)

    def eat_ghost(self, ghost, players):
        """Pac-Man mange un fantôme : score +1000 et repositionnement du fantôme sans collision"""
        print("👻 Pac-Man a mangé un fantôme !")
        self.score += 1000

        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        cell = CELL_SIZE

        # Directions autour du centre à tester
        offsets = [
            (0, 0),  # Centre
            (cell, 0), (-cell, 0),
            (0, cell), (0, -cell),
            (cell, cell), (-cell, -cell),
            (cell, -cell), (-cell, cell),
            (2 * cell, 0), (-2 * cell, 0),
            (0, 2 * cell), (0, -2 * cell)
        ]

        for dx, dy in offsets:
            new_x = center_x + dx
            new_y = center_y + dy
            ghost_rect = pygame.Rect(new_x, new_y, ghost.size, ghost.size)

            # Vérifie les collisions avec les autres joueurs
            collision = False
            for player in players:
                if player != ghost:
                    player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
                    if ghost_rect.colliderect(player_rect):
                        collision = True
                        break

            if not collision:
                ghost.x = new_x
                ghost.y = new_y
                ghost.update()
                print(f"📍 Fantôme replacé à ({ghost.x}, {ghost.y})")
                return

        print("⚠ Aucune position libre trouvée pour le fantôme.")

    def move(self, players):
        """Déplace Pac-Man en s'assurant qu'il ne traverse pas les murs"""
        # Gère le timer d'invincibilité
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        hitbox_offset = self.size // 4  #  Réduit la hitbox pour éviter l'entrée partielle dans les murs
        if self.super_power_active:
            self.super_power_timer -= 1
            if self.super_power_timer <= 0:
                self.super_power_active = False  # Désactive le super pouvoir après le temps écoulé
                self.speed = CELL_SIZE // 6  # Remet la vitesse normale

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
        """Renvoie l'image de Pac-Man selon la direction, le super pouvoir ou l'invincibilité"""

        if self != controlled_player:
            return self.image1  # Image par défaut pour les autres clients

        keys = pygame.key.get_pressed()

        # Mode clignotement pendant l'invincibilité
        if self.invincible:
            blink_on = (self.invincibility_timer // 10) % 2 == 0  # Change toutes les ~10 frames
            if blink_on:
                # Image Black
                if keys[pygame.K_LEFT]:
                    return self.image_super_left
                if keys[pygame.K_RIGHT]:
                    return self.image_super_right
                if keys[pygame.K_UP]:
                    return self.image_super_up
                if keys[pygame.K_DOWN]:
                    return self.image_super_down
                return self.image_super_right
            else:
                # Image normale
                if keys[pygame.K_LEFT]:
                    return self.image_left
                if keys[pygame.K_RIGHT]:
                    return self.image_right
                if keys[pygame.K_UP]:
                    return self.image_up
                if keys[pygame.K_DOWN]:
                    return self.image_down
                return self.image_right

        # Mode super pouvoir actif
        if self.super_power_active:
            if keys[pygame.K_LEFT]:
                return self.image_super_left
            if keys[pygame.K_RIGHT]:
                return self.image_super_right
            if keys[pygame.K_UP]:
                return self.image_super_up
            if keys[pygame.K_DOWN]:
                return self.image_super_down
            return self.image_super_right

        # Mode normal
        if keys[pygame.K_LEFT]:
            return self.image_left
        if keys[pygame.K_RIGHT]:
            return self.image_right
        if keys[pygame.K_UP]:
            return self.image_up
        if keys[pygame.K_DOWN]:
            return self.image_down
        return self.image_right

    def get_img_phantom(self):
        """Renvoie l'image du fantôme"""
        return self.image_red_ghost

    def draw(self, screen, controlled_player):
        # Affichage de l'image du joueur
        if self.is_pacman:
            screen.blit(self.get_img_pacman(controlled_player), (self.x, self.y))
        elif self.is_phantom:
            screen.blit(self.get_img_phantom(), (self.x, self.y))

        # DEBUG : hitbox rectangulaire bleue
        pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.size, self.size), 1)

        # DEBUG : hitbox circulaire verte (utilisée pour collision réelle)
        center = (self.x + self.size // 2, self.y + self.size // 2)
        pygame.draw.circle(screen, (0, 255, 0), center, self.hitbox_size, 1)

    def spawn(self, screen, img):
        """Affiche Pac-Man ou un fantôme"""
        screen.blit(img, (self.x, self.y))



