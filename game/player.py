import pygame
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from game.map import MAP_DATA
import random
import string

class Player:
    def __init__(self, ip, tcp_port, role, position):

        self.ip = ip
        self.tcp_port = int(tcp_port) if tcp_port else None
        # self.udp_port = int(udp_port) # Pas prise en compte encore de udp
        self.tcp_addr = (self.ip, self.tcp_port)
        # self.udp_addr = (self.ip, self.udp_port) # Pas prise en compte encore de udp

        self.role = role
        self.id = None
        self.is_pacman = "pacman" in role.lower()
        self.is_phantom = "fantome" in role.lower()
        self.is_coin = role == "Pièce"

        #Position
        self.position = position
        self.x,self.y = position
        self.coord = (self.x, self.y)

        self.color = (255, 0, 0)

        self.size = CELL_SIZE
        self.hitbox_size = int(self.size * 0.5)
        self.speed = CELL_SIZE // 6
        self.lives = 3

        # Images
        self.image_right = pygame.transform.scale(pygame.image.load("images/pacman - right.png"), (self.size, self.size))
        self.image_left = pygame.transform.scale(pygame.image.load("images/pacman - left.png"), (self.size, self.size))
        self.image_up = pygame.transform.scale(pygame.image.load("images/pacman - up.png"), (self.size, self.size))
        self.image_down = pygame.transform.scale(pygame.image.load("images/pacman - down.png"), (self.size, self.size))
        self.image_red_ghost = pygame.transform.scale(pygame.image.load("images/red_ghost.png"), (self.size, self.size))

        self.image_super_right = pygame.transform.scale(pygame.image.load("images/Black Pacman.png"), (self.size, self.size))
        self.image_super_left = pygame.transform.scale(pygame.image.load("images/Black Pacman-left.png"), (self.size, self.size))
        self.image_super_up = pygame.transform.scale(pygame.image.load("images/Black Pacman-up.png"), (self.size, self.size))
        self.image_super_down = pygame.transform.scale(pygame.image.load("images/Black Pacman-down.png"), (self.size, self.size))

        self.score = 0
        self.super_power_active = False
        self.super_power_timer = 0
        self.invincible = False
        self.invincibility_timer = 0
        self.is_eaten = False
        self.respawn_target = None  # Centre à atteindre quand mangé
    
    def lose_life(self):
        if self.invincible:
            return
        if self.lives > 1:
            self.lives -= 1
            self.invincible = True
            self.invincibility_timer = 180
        else:
            self.lives = 0

    def handle_collisions_with_players(self, players):
        if not self.is_pacman or self.invincible:
            return

        pacman_center = (self.x + self.size // 2, self.y + self.size // 2)
        for player in players:
            if player != self and player.is_phantom:
                ghost_center = (player.x + player.size // 2, player.y + player.size // 2)
                dx = pacman_center[0] - ghost_center[0]
                dy = pacman_center[1] - ghost_center[1]
                distance_squared = dx * dx + dy * dy
                combined_radius = self.hitbox_size + player.hitbox_size
                combined_squared = combined_radius ** 2

                if distance_squared <= combined_squared:
                    if self.super_power_active:
                        self.eat_ghost(player, players)
                    else:
                        self.lose_life()

                    self.x, self.y = self.coord  # Annule le déplacement
                    return


    def activate_super_power(self, duration=200):
        self.super_power_active = True
        self.super_power_timer = duration
        self.speed = min(int(self.speed * 1.2), CELL_SIZE // 5)

    def is_position_free(x, y, ghost, players):
        for player in players:
            if player == ghost:
                continue
            dx = (player.x + player.size // 2) - (x + ghost.size // 2)
            dy = (player.y + player.size // 2) - (y + ghost.size // 2)
            distance_squared = dx * dx + dy * dy
            if distance_squared < (ghost.size) ** 2:
                return False
        return True

    def eat_ghost(self, ghost, players):
        print("👻 Pac-Man a mangé un fantôme !")
        self.score += 1000

        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        cell = CELL_SIZE

        offsets = [
            (0, 0),
            (cell, 0), (-cell, 0),
            (0, cell), (0, -cell),
            (cell, cell), (-cell, -cell),
            (cell, -cell), (-cell, cell),
            (2 * cell, 0), (-2 * cell, 0),
            (0, 2 * cell), (0, -2 * cell),
            (cell * 2, cell * 2), (-cell * 2, -cell * 2)
        ]

        for dx, dy in offsets:
            target_x = center_x + dx
            target_y = center_y + dy

            if Player.is_position_free(target_x, target_y, ghost, players):
                ghost.is_eaten = True
                ghost.respawn_target = (target_x, target_y)
                return

        print("⚠ Aucun point de retour libre trouvé autour du centre.")

    def move(self, players):
        # 🔁 Gère l'invincibilité
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

        # 🔁 Gère le super pouvoir
        if self.super_power_active:
            self.super_power_timer -= 1
            if self.super_power_timer <= 0:
                self.super_power_active = False
                self.speed = CELL_SIZE // 6

        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        hitbox_offset = self.size // 4

        def is_wall(x, y):
            return (
                    MAP_DATA[y // CELL_SIZE][x // CELL_SIZE] == 1 or
                    MAP_DATA[y // CELL_SIZE][(x + self.size - hitbox_offset) // CELL_SIZE] == 1 or
                    MAP_DATA[(y + self.size - hitbox_offset) // CELL_SIZE][x // CELL_SIZE] == 1 or
                    MAP_DATA[(y + self.size - hitbox_offset) // CELL_SIZE][
                        (x + self.size - hitbox_offset) // CELL_SIZE] == 1
            )

        # ✅ 🧠 Sauvegarde position avant déplacement
        self.coord = (self.x, self.y)

        if self.is_pacman:
            if keys[pygame.K_LEFT] and self.x > 0 and not is_wall(self.x - self.speed, self.y):
                new_x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH and not is_wall(self.x + self.speed, self.y):
                new_x += self.speed
            if keys[pygame.K_UP] and self.y > 0 and not is_wall(self.x, self.y - self.speed):
                new_y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT and not is_wall(self.x, self.y + self.speed):
                new_y += self.speed

        elif self.is_phantom:
            if keys[pygame.K_LEFT] and self.x > 0:
                new_x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH:
                new_x += self.speed
            if keys[pygame.K_UP] and self.y > 0:
                new_y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT:
                new_y += self.speed

        self.x, self.y = new_x, new_y
        self.update()

    def update_position(self, new_pos):
        self.x, self.y = tuple(new_pos)
        self.coord = new_pos
        self.position = new_pos

    def update(self):
        self.coord = (self.x, self.y)


    def update_eaten_state(self):
        """Déplace le fantôme mangé vers le centre"""
        if not self.is_phantom or not self.is_eaten or not self.respawn_target:
            return

        target_x, target_y = self.respawn_target
        speed = self.speed  # Tu peux mettre une valeur fixe si besoin

        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 2:
            # 🎯 Arrivé au centre
            self.is_eaten = False
            self.respawn_target = None
            return

        # 🔁 Déplacement vers le centre (normalisé)
        move_x = speed * dx / distance
        move_y = speed * dy / distance
        self.x += move_x
        self.y += move_y

    def get_img_pacman(self, controlled_player):
        if self != controlled_player:
            return self.image_right

        keys = pygame.key.get_pressed()

        if self.invincible and (self.invincibility_timer // 10) % 2 == 0:
            if keys[pygame.K_LEFT]: return self.image_super_left
            if keys[pygame.K_RIGHT]: return self.image_super_right
            if keys[pygame.K_UP]: return self.image_super_up
            if keys[pygame.K_DOWN]: return self.image_super_down
            return self.image_super_right

        if self.super_power_active:
            if keys[pygame.K_LEFT]: return self.image_super_left
            if keys[pygame.K_RIGHT]: return self.image_super_right
            if keys[pygame.K_UP]: return self.image_super_up
            if keys[pygame.K_DOWN]: return self.image_super_down
            return self.image_super_right

        if keys[pygame.K_LEFT]: return self.image_left
        if keys[pygame.K_RIGHT]: return self.image_right
        if keys[pygame.K_UP]: return self.image_up
        if keys[pygame.K_DOWN]: return self.image_down
        return self.image_right

    def get_img_phantom(self):
        return self.image_red_ghost

    def draw(self, screen, controlled_player):
        if self.is_pacman:
            screen.blit(self.get_img_pacman(controlled_player), (self.x, self.y))
        elif self.is_phantom:
            if self.is_eaten:
                # Fantôme mangé : cercle translucide bleu clair
                ghost_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(
                    ghost_surface,
                    (150, 200, 255, 150),  # Couleur + alpha
                    (self.size // 2, self.size // 2),
                    self.size // 2
                )
                screen.blit(ghost_surface, (self.x, self.y))
            else:
                screen.blit(self.get_img_phantom(), (self.x, self.y))

    def spawn(self, screen, img):
        screen.blit(img, (self.x, self.y))
