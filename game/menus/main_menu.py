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
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title_text = title_font.render("PAC-MINT", True, (255, 255, 0))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 200))
        
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
