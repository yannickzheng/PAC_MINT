import pygame
import random
import heapq
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
        self.is_eaten = False
        self.respawn_target = None
        self.pathfinding_timer = 0  # Temps restant avant nouveau recalcul
        self.current_path = []  # Chemin actuel pour le fantôme

    def is_wall(self, x, y):
        cell_size = self.size
        margin = self.size * 0.15  # tolérance pour passer dans les petits espaces

        try:
            return (
                    MAP_DATA[int((y + margin) // cell_size)][int((x + margin) // cell_size)] == 1 or
                    MAP_DATA[int((y + margin) // cell_size)][int((x + self.size - margin) // cell_size)] == 1 or
                    MAP_DATA[int((y + self.size - margin) // cell_size)][int((x + margin) // cell_size)] == 1 or
                    MAP_DATA[int((y + self.size - margin) // cell_size)][
                        int((x + self.size - margin) // cell_size)] == 1
            )
        except IndexError:
            return True

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

                    self.x, self.y = self.coord
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

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start, goal, map_data):
        """Algorithme A* basique pour trouver un chemin sur ta MAP_DATA"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstituer le chemin
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            x, y = current
            neighbors = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            ]

            for neighbor in neighbors:
                nx, ny = neighbor
                # Vérifie que le voisin est dans la carte et n'est pas un mur
                if 0 <= nx < len(map_data[0]) and 0 <= ny < len(map_data):
                    if map_data[ny][nx] == 1:
                        continue

                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + self.heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score, neighbor))

        return []  # Aucun chemin trouvé

    def ghost_ai_move(self, pacman):
        if self.is_eaten:
            return  # Ne pas faire d'IA si le fantôme est en train de respawn

        self.pathfinding_timer -= 1

        if self.pathfinding_timer <= 0 or not self.current_path:
            # ➔ Recalculer chemin seulement toutes X frames
            start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
            goal = (int(pacman.x // CELL_SIZE), int(pacman.y // CELL_SIZE))
            self.current_path = self.find_path(start, goal, MAP_DATA)
            self.pathfinding_timer = 10  # Recalcul toutes les 10 frames (environ 0.15s si tu es en 60 FPS)

        if self.current_path:
            next_cell = self.current_path[0]
            target_x = next_cell[0] * CELL_SIZE
            target_y = next_cell[1] * CELL_SIZE

            dx = target_x - self.x
            dy = target_y - self.y

            if abs(dx) > abs(dy):
                if dx > 0:
                    self.x += self.speed
                else:
                    self.x -= self.speed
            else:
                if dy > 0:
                    self.y += self.speed
                else:
                    self.y -= self.speed

            # Quand il est assez proche de la prochaine case, avancer dans la liste
            if abs(dx) < 5 and abs(dy) < 5:
                self.current_path.pop(0)

    def move(self, players):
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

        if self.super_power_active:
            self.super_power_timer -= 1
            if self.super_power_timer <= 0:
                self.super_power_active = False
                self.speed = CELL_SIZE // 6

        self.coord = (self.x, self.y)

        # 🛑 Très important : ne pas faire IA si mangé
        if self.is_phantom and self.is_eaten:
            return

        if self.is_pacman:
            keys = pygame.key.get_pressed()
            new_x, new_y = self.x, self.y
            hitbox_offset = self.size // 4

            if keys[pygame.K_LEFT] and self.x > 0 and not self.is_wall(self.x - self.speed, self.y):
                new_x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH and not self.is_wall(self.x + self.speed, self.y):
                new_x += self.speed
            if keys[pygame.K_UP] and self.y > 0 and not self.is_wall(self.x, self.y - self.speed):
                new_y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT and not self.is_wall(self.x, self.y + self.speed):
                new_y += self.speed

            self.x, self.y = new_x, new_y

        elif self.is_phantom:
            if self.is_eaten:
                return  # NE PAS FAIRE IA si fantôme est mangé
            pacman = next((p for p in players if p.is_pacman), None)
            if pacman:
                self.ghost_ai_move(pacman)

        self.update()

    def update(self):
        self.coord = (self.x, self.y)

    def update_eaten_state(self):
        """Déplace le fantôme mangé vers le centre en ligne droite sans collision"""
        if not self.is_phantom or not self.is_eaten or not self.respawn_target:
            return

        target_x, target_y = self.respawn_target
        speed = self.speed

        dx = target_x - self.x
        dy = target_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < speed:
            # 🎯 Fantôme arrivé au centre => il redevient normal
            self.x, self.y = target_x, target_y  # aligne parfaitement sur le centre
            self.is_eaten = False
            self.respawn_target = None
            return

        # 🔁 Sinon, continue à se déplacer en ligne droite vers le centre
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
            screen.blit(self.get_img_pacman(controlled_player), (int(self.x), int(self.y)))
        elif self.is_phantom:
            if self.is_eaten:
                ghost_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(
                    ghost_surface,
                    (150, 200, 255, 150),
                    (self.size // 2, self.size // 2),
                    self.size // 2
                )
                screen.blit(ghost_surface, (int(self.x), int(self.y)))
            else:
                screen.blit(self.get_img_phantom(), (int(self.x), int(self.y)))

    def spawn(self, screen, img):
        screen.blit(img, (self.x, self.y))
