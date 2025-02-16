import pygame
import sys

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
pygame.display.set_caption("PACM'INT Futuriste")

# Police d'écriture futuriste (remplacez par une police de style high-tech si disponible)
font = pygame.font.Font(None, 100)  # Taille de police augmentée pour un effet plus impactant

def draw_futuristic_text(text, x, y, base_color, glow_color, screen):
    """
    Dessine un texte futuriste avec un effet de lumière (glow) et un dégradé.
    :param text: Texte à afficher
    :param x: Position x du texte
    :param y: Position y du texte
    :param base_color: Couleur de base du texte
    :param glow_color: Couleur de la lumière autour du texte
    :param screen: Surface Pygame où dessiner le texte
    """
    # Effet de lumière autour du texte (glow)
    for i in range(10):
        glow_radius = i * 2
        glow_surface = font.render(text, True, (*glow_color, 50 - i * 5))
        screen.blit(glow_surface, (x - glow_radius, y - glow_radius))

    # Dessiner le texte avec un dégradé
    text_surface = font.render(text, True, base_color)
    screen.blit(text_surface, (x, y))

def main():
    run = True
    while run:
        # Fond d'écran (noir pour un style futuriste)
        screen.fill(BLACK)

        # Dessiner le texte "PACM'INT" avec un style futuriste
        draw_futuristic_text("PACM'INT", 200, 250, CYAN, BLUE, screen)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

        # Mettre à jour l'affichage
        pygame.display.flip()

# Lancer le programme
main()