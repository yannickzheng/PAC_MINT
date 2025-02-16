import pygame
import sys
import math

# Initialisation de Pygame
pygame.init()

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 255)

# Taille de l'écran
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bouton Futuriste")

# Police d'écriture futuriste
font = pygame.font.Font(None, 36)  # Remplacez par une police futuriste si disponible


def main_menu():
    run = True
    while run:
        # Fond d'écran (noir pour un style futuriste)
        screen.fill(BLACK)

        # Dessiner un bouton futuriste
        draw_futuristic_button("Jouer", 300, 200, 200, 50, BLUE, CYAN, screen)
        draw_futuristic_button("Options", 300, 300, 200, 50, BLUE, CYAN, screen)
        draw_futuristic_button("Quitter", 300, 400, 200, 50, BLUE, PURPLE, screen)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Vérifier si un bouton est cliqué
                if 300 <= x <= 500:
                    if 200 <= y <= 250:
                        print("Bouton 'Jouer' cliqué !")
                    elif 300 <= y <= 350:
                        print("Bouton 'Options' cliqué !")
                    elif 400 <= y <= 450:
                        run = False
                        pygame.quit()
                        sys.exit()

        # Mettre à jour l'affichage
        pygame.display.flip()

# Lancer le menu principal
main_menu()