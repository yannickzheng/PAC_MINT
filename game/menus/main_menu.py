import pygame
import sys
from common.global_variable import WIDTH, HEIGHT, BLUE, CYAN, PURPLE

from game.ui.components import draw_button

def select_role(screen, font):
    """Affiche un menu pour choisir le rôle (Pacman ou Fantôme)"""
    run = True
    while run:
        screen.fill((0, 0, 0))

        # Affichage du texte "Choisissez votre rôle"
        title_text = pygame.image.load(("images/Choisissez-votre-role.png"))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))
        screen.blit(title_text, title_rect)

        # Charger les images
        pacman_image = pygame.image.load("images/pacman - right.png").convert_alpha()
        ghost_image = pygame.image.load("images/red_ghost2.png").convert_alpha()

        # Redimensionner les images pour qu'elles s'adaptent bien à l'interface
        pacman_image = pygame.transform.scale(pacman_image, (50, 50))  # Ajuste la taille de l'image
        ghost_image = pygame.transform.scale(ghost_image, (50, 50))  # Ajuste la taille de l'image

        # Afficher les images à côté des boutons
        pacman_image_rect = pacman_image.get_rect(midright=(WIDTH // 2 - 100, HEIGHT // 2 - 40 ))
        ghost_image_rect = ghost_image.get_rect(midright=(WIDTH // 2 - 100, HEIGHT // 2 + 65))

        # Afficher les boutons Pacman et Fantôme
        draw_button("Pacman", 250, 300, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Fantôme", 250, 400, 200, 50, BLUE, CYAN, screen, font)

        # Blitter les images
        screen.blit(pacman_image, pacman_image_rect)
        screen.blit(ghost_image, ghost_image_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 300 <= y <= 350:
                    return "pacman"  # Choisir Pacman
                elif 400 <= y <= 450:
                    return "fantome"  # Choisir Fantôme

        pygame.display.flip()


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
        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 130))

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
                        role = select_role(screen, font)  # Sélectionner le rôle
                        return "offline", role
                    elif 550 <= x <= 750:  # Mode En Ligne
                        return "online"
                    elif 850 <= x <= 1050:  # Quitter
                        run = False
                        pygame.quit()
                        sys.exit()
                        
        pygame.display.flip()
    
    return None
