import pygame
from common.global_variable import WIDTH, HEIGHT, CELL_SIZE
from game.map import MAP_DATA
import heapq
import math
import pygame
from common.global_variable import CELL_SIZE
from game.utils.helpers import distance


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
        """Déplace le joueur (Pacman ou Fantôme)"""
        pass

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

    def heuristic(self, a, b):
        # heuristique Manhattan #
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start, goal, map_data,  allow_goal_occupied=False):
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
                if 0 <= nx < len(map_data[0]) and 0 <= ny < len(map_data):
                    # Permettre d’atteindre la case d’arrivée même si c’est un fantôme
                    if map_data[ny][nx] == 1 and (neighbor != goal or not allow_goal_occupied):
                        continue

                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + self.heuristic(neighbor, goal)
                        heapq.heappush(open_set, (f_score, neighbor))

        return []  # Aucun chemin trouvé

    def move_along_path(self, path):
        if not path:
            return
        next_cell = path[0]
        # Vise le centre de la prochaine case
        target_x = next_cell[0] * CELL_SIZE + CELL_SIZE // 2 - self.size // 2
        target_y = next_cell[1] * CELL_SIZE + CELL_SIZE // 2 - self.size // 2
        dx = target_x - self.x
        dy = target_y - self.y

        dist = math.hypot(dx, dy)
        if dist < self.speed:
            # On est arrivé au centre de la case cible, on s'aligne parfaitement
            self.x = target_x
            self.y = target_y
            path.pop(0)
        else:
            # Avance vers la cible
            step_x = self.speed * dx / dist
            step_y = self.speed * dy / dist
            if not self.is_wall(self.x + step_x, self.y + step_y):
                self.x += step_x
                self.y += step_y
        self.update()


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

    def draw(self, screen, controlled):
        """Affiche PacMan à l'écran"""
        image = self.get_img_pacman(controlled)
        screen.blit(image, (int(self.x), int(self.y)))  # Affiche l'image à la position actuelle de PacMan

    def pacman_ai_move(self, players, coins, fruits, ghosts):
        active_ghosts = [g for g in ghosts if not g.is_eaten]

        # Mode super pouvoir : chasse les fantômes
        if self.super_power_active and active_ghosts:
            # Mange tous les fantômes assez proches
            for ghost in active_ghosts:
                if distance(self.x, self.y, ghost.x, ghost.y) < CELL_SIZE * 0.8:
                    self.eat_ghost(ghost, players)
            # Cible le fantôme le plus proche pour continuer la chasse
            target = min(active_ghosts, key=lambda g: (g.x - self.x) ** 2 + (g.y - self.y) ** 2)
            start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
            goal = (int(target.x // CELL_SIZE), int(target.y // CELL_SIZE))
            path = self.find_path(start, goal, MAP_DATA)
            self.move_along_path(path)
            return

        # Mode normal : cherche fruit en priorité, sinon pièce
        if fruits:
            target = min(fruits, key=lambda f: (f[0] - self.x) ** 2 + (f[1] - self.y) ** 2)
        elif coins:
            target = min(coins, key=lambda c: (c[0] - self.x) ** 2 + (c[1] - self.y) ** 2)
        else:
            return  # Rien à faire

        # Fuit les fantômes proches
        for ghost in active_ghosts:
            if distance(self.x, self.y, ghost.x, ghost.y) < CELL_SIZE * 2:
                dx = self.x - ghost.x
                dy = self.y - ghost.y
                flee_cell = (int((self.x + dx * 3) // CELL_SIZE), int((self.y + dy * 3) // CELL_SIZE))
                start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
                path = self.find_path(start, flee_cell, MAP_DATA)
                self.move_along_path(path)
                return

        # Sinon, va vers la cible (fruit ou pièce)
        start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))
        goal = (int(target[0] // CELL_SIZE), int(target[1] // CELL_SIZE))
        path = self.find_path(start, goal, MAP_DATA)
        self.move_along_path(path)

    def get_img_pacman(self, controlled=False):
        """Retourne l'image de PacMan en fonction de son état et de l'input du joueur"""
        if not controlled:
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

    def activate_super_power(self, duration=360):
        """Active le super pouvoir de PacMan pour une durée donnée"""
        self.super_power_active = True
        self.super_power_timer = duration
        self.speed = CELL_SIZE // 5
        print(f"Super pouvoir activé pour {duration//60} secondes!")

    def eat_ghost(self, ghost, players):
        self.score += 1000  # Ajout de points à PacMan

        respawn_position = ghost.get_respawn_position(players)

        if respawn_position:
            ghost.is_eaten = True
            ghost.respawn_target = respawn_position  # Assigner le point de respawn au fantôme
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

    def check_collision_with_items(self, coins, fruits):
        """Gère les collisions de Pacman avec les pièces et les fruits."""
        for coin in coins[:]:
            if distance(self.x, self.y, coin[0], coin[1]) < CELL_SIZE // 2:
                self.score += 10
                coins.remove(coin)
        for fruit in fruits[:]:
            if distance(self.x, self.y, fruit[0], fruit[1]) < CELL_SIZE // 2:
                self.score += 50
                fruits.remove(fruit)
                self.activate_super_power()

    def check_collision_with_ghosts(self, ghosts, players):
        """Gère la collision Pacman vs tous les fantômes."""
        for ghost in ghosts:
            if distance(self.x, self.y, ghost.x, ghost.y) < CELL_SIZE:
                if self.super_power_active:
                    self.eat_ghost(ghost, players)
                    self.score += 200
                elif not self.invincible:
                    self.lose_life()
                    self.invincible = True
                    self.invincibility_timer = 180



class Ghost(Player):
    def __init__(self, ip, tcp_port, position):
        super().__init__(ip, tcp_port, "Fantôme", position)
        self.lives = float('inf')  # Fantômes ont des vies illimitées
        self.is_eaten = False
        self.respawn_target = None
        self.pathfinding_timer = 0  # Temps restant avant nouveau recalcul
        self.current_path = []  # Chemin actuel pour le fantôme

    def move(self, players, controlled=False):
        """Si controlled=True : le joueur déplace ce fantôme au clavier.Sinon : IA A* via ghost_ai_move."""
        if controlled:
            keys = pygame.key.get_pressed()
            new_x, new_y = self.x, self.y

            if keys[pygame.K_LEFT] and not self.is_wall(self.x - self.speed, self.y):
                new_x -= self.speed

            if keys[pygame.K_RIGHT] and not self.is_wall(self.x + self.speed, self.y):
                new_x += self.speed

            if keys[pygame.K_UP] and not self.is_wall(self.x, self.y - self.speed):
                new_y -= self.speed
            if keys[pygame.K_DOWN] and not self.is_wall(self.x, self.y + self.speed):
                new_y += self.speed

            self.x, self.y = new_x, new_y
        else:
            pacman = next((p for p in players.values() if isinstance(p, PacMan)), None)
            if pacman:
                self.ghost_ai_move(pacman)
        self.update()

    def draw(self, screen, controlled):
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

    def is_position_free(self, x, y, players):
        """Retourne True si la position (x,y) est libre de collision avec les autres joueurs."""
        for other in players.values():
            if other is self:
                continue
            dx = (other.x + other.size // 2) - (x + self.size // 2)
            dy = (other.y + other.size // 2) - (y + self.size // 2)
            if dx * dx + dy * dy < (self.size) ** 2:
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

        # Parmi les fantômes qui sont déjà en cours de respawn,
        # on recense leurs cibles actuelles pour ne pas les réutiliser.
        used = {
        other.respawn_target
        for other in players.values()
            if isinstance(other, Ghost) and other.is_eaten and other.respawn_target is not None
        }

        # On parcourt les offsets : on choisit le premier libre ET non déjà attribué

        for dx, dy in offsets:
            tx = center_x + dx
            ty = center_y + dy

            if (tx, ty) in used:
                continue
            if self.is_position_free(tx, ty, players):
                return (tx, ty)

        # Cherche un point libre autour du centre pour respawn
        for dx, dy in offsets:
            target_x = center_x + dx
            target_y = center_y + dy

            if self.is_position_free(target_x, target_y, players):
                return (target_x, target_y)

        return None  # Si aucun point libre trouvé

    def check_collision_with_pacman(self, pacman, players):
        """Gère la collision Fantôme contrôlé <-> Pacman."""
        if distance(self.x, self.y, pacman.x, pacman.y) < CELL_SIZE:
            if pacman.super_power_active:
                pacman.eat_ghost(self, players)
                pacman.score += 200
            elif not pacman.invincible:
                pacman.lose_life()
                pacman.invincible = True
                pacman.invincibility_timer = 180
                self.score += 1000
    def update_eaten_state(self):
        """Déplace le fantôme mangé vers le centre en ligne droite sans collision."""
        if not self.is_eaten or self.respawn_target is None:
            return

        tx, ty = self.respawn_target
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        # Si on est déjà au point de respawn, on termine
        if dist == 0:
            self.is_eaten = False
            self.respawn_target = None
            return

        # On avance de `speed` pixels vers la cible (ou moins si on est tout proche)
        step = min(self.speed, dist)
        self.x += step * dx / dist
        self.y += step * dy / dist

        # Si on a atteint la cible, on réactive le fantôme normalement
        if step == dist:
            self.x, self.y = tx, ty
            self.is_eaten = False
            self.respawn_target = None

    def ghost_ai_move(self, pacman):
        if self.is_eaten:
            return  # Ne pas faire d'IA si le fantôme est en train de respawn

        # Forcer le recalcul si changement de stratégie (fuite vs poursuite)
        if pacman.super_power_active and self.pathfinding_timer > 0:
            self.pathfinding_timer = 0

        self.pathfinding_timer -= 1

        target_cell = (int(pacman.x // CELL_SIZE), int(pacman.y // CELL_SIZE))
        # Fuite : cellule éloignée de Pacman
        if pacman.super_power_active:
            dx = self.x - pacman.x
            dy = self.y - pacman.y
            flee_cell = (
                max(0, min(int((self.x + dx * 3) // CELL_SIZE), len(MAP_DATA[0]) - 1)),
                max(0, min(int((self.y + dy * 3) // CELL_SIZE), len(MAP_DATA) - 1))
            )
            goal = flee_cell
        else:
            goal = target_cell

        start = (int(self.x // CELL_SIZE), int(self.y // CELL_SIZE))

        # Recalcule le chemin si besoin (timer, cible changée, ou pas de chemin)
        if self.pathfinding_timer <= 0 or not self.current_path or self.current_path[-1] != goal:
            self.current_path = self.find_path(start, goal, MAP_DATA)
            self.pathfinding_timer = 10  # Recalcul toutes les 10 frames

        if self.current_path:
            self.move_along_path(self.current_path)
