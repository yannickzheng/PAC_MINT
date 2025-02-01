import pygame
from global_variable import WIDTH, HEIGHT, CELL_SIZE
from map import MAP_DATA
import random
import sys

epsilon = sys.float_info.epsilon  # 2.220446049250313e-16


class Player:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.coord = (x, y)
        self.color = (255, 0, 0)
        self.size = 20
        self.image1 = pygame.image.load("images/pacman - right.png")
        self.image2 = pygame.image.load("images/pacman - left.png")
        self.image3 = pygame.image.load("images/pacman - up.png")
        self.image4 = pygame.image.load("images/pacman - down.png")
        self.is_pacman = role == "PacMan"
        self.is_phantom = role == "Fantôme"
        self.is_coin = role == "Pièce"
        self.score = 0

    def add_score(self, coin, smallfont=None, gameDisplay=None):
        text = smallfont.render(f"Score : {self.score}", True, (255, 255, 255))

        if self.is_pacman:
            if self.x - coin.x < epsilon and self.y - coin.y < epsilon:
                self.score += 1
                del coin  # On supprime la pièce de la map
                gameDisplay.blit(text, (0, 0))
                return True
            return False



    def generate_random_position(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)

    def get_img(self):
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


    def move(self):
        # il faut que le joueur ne puisse se déplacer que dans les cases de la map qui sont des chemins
        keys = pygame.key.get_pressed()
        cell_x = self.x // CELL_SIZE
        cell_y = self.y // CELL_SIZE

        print(f"Position du joueur : ({self.x}, {self.y}), Cellule : ({cell_x}, {cell_y})")  # Debug
        print(f"MAP_DATA[{self.y}][{self.x}] = {MAP_DATA[cell_y][cell_x]}")  # Debug

        if (keys[pygame.K_LEFT]
                and self.x > 0
                and cell_x > 0
                and MAP_DATA[cell_y][(self.x - 2) // CELL_SIZE] == 0):
            self.x = self.x - 2

        if (keys[pygame.K_RIGHT]
                and self.x + 1 < WIDTH
                and cell_x > 0
                and MAP_DATA[cell_y][(self.x + 2) // CELL_SIZE] == 0):
            self.x = self.x + 2

        if (keys[pygame.K_UP]
                and self.y > 0
                and cell_y > 0
                and MAP_DATA[(self.y - 2) // CELL_SIZE][cell_x] == 0):
            self.y = self.y - 2

        if (keys[pygame.K_DOWN]
                and self.y - 1 < HEIGHT
                and cell_y > 0
                and MAP_DATA[(self.y + 2) // CELL_SIZE][cell_x] == 0):
            self.y = self.y + 2

        self.update()

    def update(self):
        self.coord = (self.x, self.y)

    def draw(self, screen):
        if self.is_pacman:
            self.spawn(screen, self.get_img())

        elif self.is_phantom:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def spawn(self, screen, img):
        screen.blit(img, (self.x, self.y))


# Il faut convertir la position d'un joueur (tuple) en string pour pouvoir l'envoyer via le réseau et vice versa
def tuple_to_str(couple):
    return str(couple[0]) + "," + str(couple[1])


def triple_to_str(triple):
    return str(triple[0]) + "," + str(triple[1]) + "," + str(triple[2])


def str_to_tuple(s: str):
    s = s.split(",")
    return int(s[0]), int(s[1])
