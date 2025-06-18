import pygame
import sys
from common.global_variable import WIDTH, HEIGHT, BLUE, CYAN, PURPLE

from game.ui.components import draw_button

def main_menu(screen, image, font):
    """Menu principal du jeu"""
    
    run = True
    while run:
        screen.blit(image, (0, 0))

        # Titre du jeu
        title_image = pygame.image.load("images/Pacmint texte.png").convert_alpha()

        # Redimensionnement à 50% de la taille originale
        original_width, original_height = title_image.get_size()
        new_width = original_width // 2
        new_height = original_height // 2
        title_image = pygame.transform.smoothscale(title_image, (new_width, new_height))

        # Recalcul du rectangle pour bien centrer l'image redimensionnée
        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

        # Affichage
        screen.blit(title_image, title_rect)
        
        draw_button("Mode Hors Ligne", 250, 600, 200, 50, BLUE, CYAN, screen, font)  
        draw_button("Mode En Ligne", 550, 600, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Quitter", 850, 600, 200, 50, BLUE, PURPLE, screen, font)
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Vérifier les boutons principaux en bas de l'écran
                if 600 <= y <= 650:
                    if 250 <= x <= 450:  # Mode Hors Ligne
                        return "offline"
                    elif 550 <= x <= 750:  # Mode En Ligne
                        return "online"
                    elif 850 <= x <= 1050:  # Quitter
                        run = False
                        pygame.quit()
                        sys.exit()
                        
        pygame.display.flip()
    
    return None
