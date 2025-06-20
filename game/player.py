import pygame
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from game.map import MAP_DATA
import heapq

import pygame
from common.global_variable import CELL_SIZE

class Player:
    def __init__(self, ip, tcp_port, role, position):
        self.ip = ip
        self.tcp_port = int(tcp_port) if tcp_port else None
        self.tcp_addr = (self.ip, self.tcp_port)

        self.role = role
        self.score = 0
        self.id = None
        self.is_coin = role == "Pièce"

        # Position
        self.position = position
        self.x, self.y = position
        self.coord = (self.x, self.y)

        self.size = CELL_SIZE
        self.hitbox_size = CELL_SIZE // 2
        self.speed = CELL_SIZE // 6

        # Chargement des images
        self.image_right = pygame.transform.scale(pygame.image.load("images/pacman - right.png"), (self.size, self.size))
        self.image_left = pygame.transform.scale(pygame.image.load("images/pacman - left.png"), (self.size, self.size))
        self.image_up = pygame.transform.scale(pygame.image.load("images/pacman - up.png"), (self.size, self.size))
        self.image_down = pygame.transform.scale(pygame.image.load("images/pacman - down.png"), (self.size, self.size))
        self.image_red_ghost = pygame.transform.scale(pygame.image.load("images/red_ghost2.png"), (self.size, self.size))

        self.image_super_right = pygame.transform.scale(pygame.image.load("images/Black Pacman.png"), (self.size, self.size))
        self.image_super_left = pygame.transform.scale(pygame.image.load("images/Black Pacman-left.png"), (self.size, self.size))
        self.image_super_up = pygame.transform.scale(pygame.image.load("images/Black Pacman-up.png"), (self.size, self.size))
        self.image_super_down = pygame.transform.scale(pygame.image.load("images/Black Pacman-down.png"), (self.size, self.size))

    def move(self, players):
        """Déplace le joueur (Pacman ou Fantôme)""" ###### A COMPLETER DANS CHAQUE CLASSE#########################
        pass

    def check_collision(self, players):
        """Vérifie si le joueur entre en collision avec un autre joueur"""
        for player in players.values():
            if player != self:
                distance_squared = (self.x - player.x) ** 2 + (self.y - player.y) ** 2
                if distance_squared < (self.hitbox_size + player.hitbox_size) ** 2:
                    return True
        return False

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

    def draw(self, screen):
        """Affiche le joueur à l'écran"""
        pass

    def update(self):
        """Met à jour les coordonnées du joueur"""
        self.coord = (self.x, self.y)  # Met à jour les coordonnées


class PacMan(Player):
    def __init__(self, ip, tcp_port, position):
        super().__init__(ip, tcp_port, "PacMan", position)
        self.lives = 3  # PacMan commence avec 3 vies
        self.score = 0
        self.super_power_active = False
        self.super_power_timer = 0
        self.invincible = False
        self.invincibility_timer = 0

    def move(self, players, controlled=False):
        """Déplace PacMan contrôlé par le joueur avec les touches du clavier"""
        keys = pygame.key.get_pressed()  # Récupère les touches enfoncées
        new_x, new_y = self.x, self.y  # Position de départ
        hitbox_offset = self.size // 4  # Ajuste la taille du hitbox pour la détection des collisions

        # Gestion du super pouvoir (accélération)
        if self.super_power_active:
            self.super_power_timer -= 1
            if self.super_power_timer <= 0:
                self.super_power_active = False
                self.speed = CELL_SIZE // 6  # Réinitialise la vitesse à la normale

        # Si PacMan est contrôlé par le joueur
        if controlled:
            # Déplacement avec les touches directionnelles (gauche, droite, haut, bas)
            if keys[pygame.K_LEFT] and self.x > 0 and not self.is_wall(self.x - self.speed, self.y):
                new_x -= self.speed
            if keys[pygame.K_RIGHT] and self.x + self.size < WIDTH and not self.is_wall(self.x + self.speed, self.y):
                new_x += self.speed
            if keys[pygame.K_UP] and self.y > 0 and not self.is_wall(self.x, self.y - self.speed):
                new_y -= self.speed
            if keys[pygame.K_DOWN] and self.y + self.size < HEIGHT and not self.is_wall(self.x, self.y + self.speed):
                new_y += self.speed

            # Applique les nouvelles coordonnées
            self.x, self.y = new_x, new_y

        # Met à jour les coordonnées du personnage
        self.update()

    def draw(self, screen, controlled_player = None):
        """Affiche PacMan à l'écran"""
        image = self.get_img_pacman(controlled_player)
        screen.blit(image, (int(self.x), int(self.y)))  # Affiche l'image à la position actuelle de PacMan

    def get_img_pacman(self, controlled_player):
        """Retourne l'image de PacMan en fonction de son état et de l'input du joueur"""
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

    def handle_collisions_with_ghosts(self, players):
        """Gère les collisions de PacMan avec les fantômes."""
        if self.invincible:  # Si PacMan est invincible, il ne perd pas de vie
            return

        pacman_center = (self.x + self.size // 2, self.y + self.size // 2)

        for player in players.values():
            if player != self and player.is_phantom:  # Si c'est un fantôme
                ghost_center = (player.x + player.size // 2, player.y + player.size // 2)
                dx = pacman_center[0] - ghost_center[0]
                dy = pacman_center[1] - ghost_center[1]
                distance_squared = dx * dx + dy * dy
                combined_radius = self.hitbox_size + player.hitbox_size
                combined_squared = combined_radius ** 2

                if distance_squared <= combined_squared:  # Collision avec le fantôme
                    if self.super_power_active:
                        self.eat_ghost(player, players)  # Si PacMan a le super pouvoir, manger le fantôme
                    else:
                        self.lose_life()  # Sinon, perdre une vie

                    self.x, self.y = self.coord  # Réinitialise la position de PacMan après la collision
                    return  # Fin de la gestion de la collision

    def activate_super_power(self, duration=200):
        """Active le super pouvoir de PacMan pour une durée donnée"""
        self.super_power_active = True
        self.super_power_timer = duration
        self.speed = min(int(self.speed * 1.2), CELL_SIZE // 5)
        print(f"Super pouvoir activé pour {duration//60} secondes!")

    def eat_ghost(self, ghost, players):
        self.score += 1000  # Ajout de points à PacMan

        respawn_position = ghost.get_respawn_position(players)

        if respawn_position:
            ghost.respawn_target = respawn_position  # Assigner le point de respawn au fantôme
            ghost.x, ghost.y = respawn_position  # Déplacer le fantôme au point de respawn
        else:
            print("⚠ Aucun point libre pour le respawn du fantôme.")

    def lose_life(self):
        """Perdre une vie"""
        if self.invincible:
            return
        if self.lives > 1:
            self.lives -= 1
            self.invincible = True
            self.invincibility_timer = 180  # PacMan est invincible pendant 3 secondes
        else:
            self.lives = 0

    def update(self):
        """Met à jour les informations de PacMan"""
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False



class Ghost(Player):
    def __init__(self, ip, tcp_port, position):
        super().__init__(ip, tcp_port, "Fantôme", position)
        self.lives = float('inf')  # Fantômes ont des vies illimitées
        self.is_eaten = False
        self.respawn_target = None
        self.pathfinding_timer = 0  # Temps restant avant nouveau recalcul
        self.current_path = []  # Chemin actuel pour le fantôme

    def draw(self, screen, controlled_player = None):
        """Affiche le fantôme à l'écran"""
        if self.is_eaten:
            # Si le fantôme est mangé, on le dessine en tant que boule translucide
            ghost_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(
                ghost_surface,
                (150, 200, 255, 150),  # Couleur et transparence pour effet "mangé"
                (self.size // 2, self.size // 2),
                self.size // 2
            )
            screen.blit(ghost_surface, (int(self.x), int(self.y)))
        else:
            # Affichage normal du fantôme
            image = self.get_img_phantom()  # On récupère l'image du fantôme via la méthode
            screen.blit(image, (int(self.x), int(self.y)))

    def get_img_phantom(self):
        """Retourne l'image du fantôme"""
        return self.image_red_ghost

    def is_position_free(x, y, ghost, players):
        for player in players.values():
            if player == ghost:
                continue
            dx = (player.x + player.size // 2) - (x + ghost.size // 2)
            dy = (player.y + player.size // 2) - (y + ghost.size // 2)
            distance_squared = dx * dx + dy * dy
            if distance_squared < (ghost.size) ** 2:
                return False
        return True

    def get_respawn_position(self, players):
        """Retourne un point de respawn libre pour le fantôme"""
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

        # Cherche un point libre autour du centre pour respawn
        for dx, dy in offsets:
            target_x = center_x + dx
            target_y = center_y + dy

            if self.is_position_free(target_x, target_y, self, players):
                return (target_x, target_y)

        return None  # Si aucun point libre trouvé

    def update_eaten_state(self):
        "Déplace le fantôme mangé vers le centre en ligne droite sans collision"
        if not self.is_eaten or not self.respawn_target:
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

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start, goal, map_data):
        "Algorithme A* basique pour trouver un chemin sur ta MAP_DATA"
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

        # 🔁 Forcer le recalcul si changement de stratégie (fuite vs poursuite)
        if pacman.super_power_active and self.pathfinding_timer > 0:
            self.pathfinding_timer = 0

        self.pathfinding_timer -= 1

        if self.pathfinding_timer <= 0 or not self.current_path:
            start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

            if pacman.super_power_active:
                # 🔁 Fuite : aller dans la direction opposée à Pacman
                dx = self.x - pacman.x
                dy = self.y - pacman.y
                flee_x = self.x + dx * 3
                flee_y = self.y + dy * 3

                # Clamp les coordonnées dans les limites de la carte
                goal = (
                    max(0, min(int(flee_x // CELL_SIZE), len(MAP_DATA[0]) - 1)),
                    max(0, min(int(flee_y // CELL_SIZE), len(MAP_DATA) - 1))
                )
            else:
                # 🎯 Poursuite normale de Pacman
                goal = (int(pacman.x // CELL_SIZE), int(pacman.y // CELL_SIZE))

            self.current_path = self.find_path(start, goal, MAP_DATA)
            self.pathfinding_timer = 5  # Recalcul toutes les 10 frames

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

            # Si on est proche de la prochaine case, on passe à la suivante
            if abs(dx) < 5 and abs(dy) < 5:
                self.current_path.pop(0)

"""class Player:
    def __init__(self, ip, tcp_port, role, position, tcp_socket=None):   ######### GERE ########

        self.ip = ip
        self.tcp_port = int(tcp_port) if tcp_port else None
        self.tcp_socket = tcp_socket
        # self.udp_port = int(udp_port) # Pas prise en compte encore de udp
        self.tcp_addr = (self.ip, self.tcp_port)
        # self.udp_addr = (self.ip, self.udp_port) # Pas prise en compte encore de udp

        self.role = role
        self.id = None
        self.is_pacman = "pacman" in role.lower()
        self.is_phantom = "fantôme" in role.lower()
        self.is_coin = role == "Pièce"

        #Position
        self.position = position
        self.x,self.y = position
        self.coord = (self.x, self.y)

        self.color = (255, 0, 0)
        self.size = CELL_SIZE  # Pac-Man doit être basé sur `CELL_SIZE`
        self.hitbox_size = CELL_SIZE // 2
        self.speed = CELL_SIZE // 6  # Pac-Man bouge par petits pas

        # Gestion des vies
        if self.is_pacman:
            self.lives = 3  # PacMan commence avec 3 vies
        else:
            self.lives = float('inf')  # Fantôme a des vies illimitées
        #Chargement des images
        self.image1 = pygame.image.load("images/pacman - right.png")
        self.image2 = pygame.image.load("images/pacman - left.png")
        self.image3 = pygame.image.load("images/pacman - up.png")
        self.image4 = pygame.image.load("images/pacman - down.png")
        self.image5 = pygame.image.load("images/red_ghost2.png")

        self.image_right = pygame.transform.scale(pygame.image.load("images/pacman - right.png"), (self.size, self.size))
        self.image_left = pygame.transform.scale(pygame.image.load("images/pacman - left.png"), (self.size, self.size))
        self.image_up = pygame.transform.scale(pygame.image.load("images/pacman - up.png"), (self.size, self.size))
        self.image_down = pygame.transform.scale(pygame.image.load("images/pacman - down.png"), (self.size, self.size))
        self.image_red_ghost = pygame.transform.scale(pygame.image.load("images/red_ghost2.png"), (self.size, self.size))

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
        self.respawn_target = None
        self.pathfinding_timer = 0  # Temps restant avant nouveau recalcul
        self.current_path = []  # Chemin actuel pour le fantôme

    def check_collision(self, players): ######### GERE ########
        "Vérifie si le joueur entre en collision avec un autre joueur"
        for player in players.values():
            if player != self:
                distance_squared = (self.x - player.x) ** 2 + (self.y - player.y) ** 2
                if distance_squared < (self.hitbox_size + player.hitbox_size) ** 2:
                    return True
        return False
    def is_wall(self, x, y): ######### GERE ########
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

    def lose_life(self):    ######### GERE ########
        if self.invincible:
            return
        if self.lives > 1:
            self.lives -= 1
            self.invincible = True
            self.invincibility_timer = 180
        else:
            self.lives = 0

    def handle_collisions_with_players(self, players):  ######### GERE pour Pacman########
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
    
    def activate_super_power(self, duration=200): ######### GERE ########
        "Active le super pouvoir de Pacman pour une durée donnée"
        self.super_power_active = True
        self.super_power_timer = duration
        self.speed = min(int(self.speed * 1.2), CELL_SIZE // 5)
        print(f"Super pouvoir activé pour {duration//60} secondes!")

    def is_position_free(x, y, ghost, players): ######### GERE ########
        for player in players.values():
            if player == ghost:
                continue
            dx = (player.x + player.size // 2) - (x + ghost.size // 2)
            dy = (player.y + player.size // 2) - (y + ghost.size // 2)
            distance_squared = dx * dx + dy * dy
            if distance_squared < (ghost.size) ** 2:
                return False
        return True

    def eat_ghost(self, ghost, players):  ######### GERE ########
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

############## Algorithme deplacement des fantomes par IA###########################

    def heuristic(self, a, b):    ######### GERE ########
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start, goal, map_data):    ######### GERE ########
        "Algorithme A* basique pour trouver un chemin sur ta MAP_DATA"
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

    def ghost_ai_move(self, pacman):   ######### GERE ########
        if self.is_eaten:
            return  # Ne pas faire d'IA si le fantôme est en train de respawn

        # 🔁 Forcer le recalcul si changement de stratégie (fuite vs poursuite)
        if pacman.super_power_active and self.pathfinding_timer > 0:
            self.pathfinding_timer = 0

        self.pathfinding_timer -= 1

        if self.pathfinding_timer <= 0 or not self.current_path:
            start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

            if pacman.super_power_active:
                # 🔁 Fuite : aller dans la direction opposée à Pacman
                dx = self.x - pacman.x
                dy = self.y - pacman.y
                flee_x = self.x + dx * 3
                flee_y = self.y + dy * 3

                # Clamp les coordonnées dans les limites de la carte
                goal = (
                    max(0, min(int(flee_x // CELL_SIZE), len(MAP_DATA[0]) - 1)),
                    max(0, min(int(flee_y // CELL_SIZE), len(MAP_DATA) - 1))
                )
            else:
                # 🎯 Poursuite normale de Pacman
                goal = (int(pacman.x // CELL_SIZE), int(pacman.y // CELL_SIZE))

            self.current_path = self.find_path(start, goal, MAP_DATA)
            self.pathfinding_timer = 5  # Recalcul toutes les 10 frames

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

            # Si on est proche de la prochaine case, on passe à la suivante
            if abs(dx) < 5 and abs(dy) < 5:
                self.current_path.pop(0)
###################################################################################

    def move(self, players, controlled=False):######### GERE POUR PACMAN ########
        ""Déplace le joueur (Pacman ou Fantôme) contrôlé par le client.""
        keys = pygame.key.get_pressed()
        new_x, new_y = self.x, self.y
        hitbox_offset = self.size // 4

        if self.super_power_active:
            self.super_power_timer -= 1
            if self.super_power_timer <= 0:
                self.super_power_active = False
                self.speed = CELL_SIZE // 6

        self.coord = (self.x, self.y)

        if self.is_phantom and self.is_eaten:
            return

        if self.is_pacman or (self.is_phantom and controlled):
            # Controle clavier pour Pacman et pour le fantôme contrôlé par le joueur
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
            # IA uniquement pour les fantômes non contrôlés par le joueur
            pacman = next((p for p in players.values() if p.is_pacman), None)
            if pacman:
                self.ghost_ai_move(pacman)

        self.update()

    def update_position(self, new_pos): ######### GERE ########
        self.x, self.y = tuple(new_pos)
        self.coord = new_pos
        self.position = new_pos

    def update(self): ######### GERE ########
        "Met à jour les coordonnées du joueur"
        self.coord = (self.x, self.y)

    def update_eaten_state(self): ######### GERE ########
        "Déplace le fantôme mangé vers le centre en ligne droite sans collision"
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

    def get_img_pacman(self, controlled_player):  ######### GERE ########
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



    def get_img_phantom(self): ######### GERE ########
        return self.image_red_ghost2

    def draw(self, screen, controlled_player):   ######### GERE ########
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
        screen.blit(img, (self.x, self.y))"""
