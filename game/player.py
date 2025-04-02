import pygame
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from map import MAP_DATA

class Player:
    def __init__(self, x, y, role, ip, tcp_port, udp_port=None):
        self.ip = ip
        self.tcp_port = int(tcp_port) if tcp_port else None
        self.tcp_addr = (self.ip, self.tcp_port)

        self.x = x
        self.y = y
        self.coord = (x, y)
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

        self.is_pacman = role == "PacMan"
        self.is_phantom = role == "Fantôme"
        self.is_coin = role == "Pièce"
        self.score = 0
        self.super_power_active = False
        self.super_power_timer = 0
        self.invincible = False
        self.invincibility_timer = 0

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
                    print("💥 COLLISION Pac-Man ↔ Fantôme détectée")

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

    def eat_ghost(self, ghost, players):
        print("👻 Pac-Man a mangé un fantôme !")
        self.score += 1000
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        cell = CELL_SIZE

        offsets = [
            (0, 0), (cell, 0), (-cell, 0), (0, cell), (0, -cell),
            (cell, cell), (-cell, -cell), (cell, -cell), (-cell, cell),
            (2 * cell, 0), (-2 * cell, 0), (0, 2 * cell), (0, -2 * cell)
        ]

        for dx, dy in offsets:
            new_x, new_y = center_x + dx, center_y + dy
            ghost_rect = pygame.Rect(new_x, new_y, ghost.size, ghost.size)
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
        """Déplace Pac-Man ou un fantôme, gère les murs, le super pouvoir et sauvegarde la position"""

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

        # 🔁 Mouvement Pac-Man (bloqué par les murs)
        if self.is_pacman:
            if keys[pygame.K_LEFT] and self.x > 0 and not is_wall(self.x - self.speed, self.y):
                new_x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH and not is_wall(self.x + self.speed, self.y):
                new_x += self.speed
            if keys[pygame.K_UP] and self.y > 0 and not is_wall(self.x, self.y - self.speed):
                new_y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT and not is_wall(self.x, self.y + self.speed):
                new_y += self.speed

        # 🔁 Mouvement Fantômes (traversent les murs)
        elif self.is_phantom:
            if keys[pygame.K_LEFT] and self.x > 0:
                new_x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH:
                new_x += self.speed
            if keys[pygame.K_UP] and self.y > 0:
                new_y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT:
                new_y += self.speed

        # 💾 Sauvegarde position avant tentative de déplacement
        self.coord = (self.x, self.y)

        # ✅ Applique le déplacement
        self.x, self.y = new_x, new_y

        # 🔁 Met à jour les coordonnées (utile pour rollback ou affichage)
        self.update()

    def update(self):
        self.coord = (self.x, self.y)

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
            screen.blit(self.get_img_phantom(), (self.x, self.y))

        pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.size, self.size), 1)
        center = (self.x + self.size // 2, self.y + self.size // 2)
        pygame.draw.circle(screen, (0, 255, 0), center, self.hitbox_size, 1)

    def spawn(self, screen, img):
        screen.blit(img, (self.x, self.y))
