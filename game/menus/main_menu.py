import pygame
import sys
from common.global_variable import WIDTH, HEIGHT, BLUE, CYAN, PURPLE

from game.ui.components import draw_button

def select_role(screen, font, mode="offline"):
    """Affiche un menu pour choisir le rôle (Pacman ou Fantôme)"""
    run = True
    while run:
        screen.fill((0, 0, 0))

        # ——— Affichage du bandeau “Mode Hors-Ligne” ———
        if mode == "offline":
            header_img = pygame.transform.scale(
                pygame.image.load("images/mode-hors-ligne.png").convert_alpha(),
                (400, 80)
            )
            header_rect = header_img.get_rect(center=(WIDTH // 2, 70))
            screen.blit(header_img, header_rect)

        # Affichage du texte "Choisissez votre rôle"
        title_text = pygame.image.load(("images/Choisissez-votre-role.png"))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        screen.blit(title_text, title_rect)

        # Charger les images
        pacman_image = pygame.image.load("images/pacman - right.png").convert_alpha()
        ghost_image = pygame.image.load("images/red_ghost.png").convert_alpha()

        # Redimensionner les images pour qu'elles s'adaptent bien à l'interface
        pacman_image = pygame.transform.scale(pacman_image, (50, 50))  # Ajuste la taille de l'image
        ghost_image = pygame.transform.scale(ghost_image, (50, 50))  # Ajuste la taille de l'image

        # Afficher les images à côté des boutons
        pacman_image_rect = pacman_image.get_rect(midright=(WIDTH // 2 - 265, HEIGHT // 2 + 130 )) #Pour qu'il soit juste en dessous du bouton
        ghost_image_rect = ghost_image.get_rect(midright=(WIDTH // 2 + 180, HEIGHT // 2 + 130))

        # Afficher les boutons Pacman et Fantôme
        draw_button("Pacman", 250, 500, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Fantôme", 700, 500, 200, 50, BLUE, CYAN, screen, font)

        # Blitter les images
        screen.blit(pacman_image, pacman_image_rect)
        screen.blit(ghost_image, ghost_image_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 250 <= x <= 250 + 200 and 500 <= y <= 500 + 50:
                    return "pacman"  # Choisir Pacman
                elif 700 <= x <= 700 + 200 and 500 <= y <= 500 + 50:
                    return "fantome"  # Choisir Fantôme

        pygame.display.flip()

def select_online_role(screen, font, taken_roles = None):
    roles = ["pacman", "fantome_1", "fantome_2", "fantome_3", "fantome_4"]
    if taken_roles is None:
        taken_roles = []
    run = True
    while run:
        screen.fill((0, 0, 0))

        # affichage du mode
        header_img = pygame.transform.scale(
            pygame.image.load("images/mode-en-ligne.png").convert_alpha(),
            (400, 80)
        )
        header_rect = header_img.get_rect(center=(WIDTH // 2, 70))
        screen.blit(header_img, header_rect)

        # Affichage du texte "Choisissez votre rôle"
        title_img = pygame.image.load("images/Choisissez-votre-role.png")
        title_img = pygame.transform.smoothscale(title_img, (550, 150))
        title_rect = title_img.get_rect(center=(WIDTH // 2, 170))  # 180 ou moins pour le monter
        screen.blit(title_img, title_rect)

        # Afficher les boutons Pacman et Fantômes
        color_disabled = (100, 100, 100)
        color_active = CYAN
        draw_button("Pacman", 250, 400, 200, 50,
                    color_disabled if "pacman" in taken_roles else BLUE,
                    color_disabled if "pacman" in taken_roles else color_active,
                    screen, font)
        if "pacman" in taken_roles:
            taken_roles_text = font.render(f"Trop tard :(  Rôle déjà pris", True, (255, 255, 0))
            screen.blit(taken_roles_text, (250, 470))

        draw_button("Fantôme 1", 800, 250, 200, 50,
                    color_disabled if "fantome_1" in taken_roles else BLUE,
                    color_disabled if "fantome_1" in taken_roles else color_active,
                    screen, font)
        if "fantome_1" in taken_roles:
            taken_roles_text = font.render(f"Trop tard :(  Rôle déjà pris", True, (255, 255, 0))
            screen.blit(taken_roles_text, (1020, 260))
        draw_button("Fantôme2 ", 800, 350, 200, 50,
                    color_disabled if "fantome_2" in taken_roles else BLUE,
                    color_disabled if "fantome_2" in taken_roles else color_active,
                    screen, font)
        if "fantome_2" in taken_roles:
            taken_roles_text = font.render(f"Trop tard :(  Rôle déjà pris", True, (255, 255, 0))
            screen.blit(taken_roles_text, (1020, 360))
        draw_button("Fantôme 3", 800, 450, 200, 50,
                    color_disabled if "fantome_3" in taken_roles else BLUE,
                    color_disabled if "fantome_3" in taken_roles else color_active,
                    screen, font)
        if "fantome_3" in taken_roles:
            taken_roles_text = font.render(f"Trop tard :(  Rôle déjà pris", True, (255, 255, 0))
            screen.blit(taken_roles_text, (1020, 460))
        draw_button("Fantôme 4", 800, 550, 200, 50,
                    color_disabled if "fantome_4" in taken_roles else BLUE,
                    color_disabled if "fantome_4" in taken_roles else color_active,
                    screen, font)
        if "famtome_4" in taken_roles:
            taken_roles_text = font.render(f"Trop tard :(  Rôle déjà pris", True, (255, 255, 0))
            screen.blit(taken_roles_text, (1020, 560))
        draw_button("Retour", 520, 650, 200, 50, BLUE, CYAN, screen, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 250 <= x <= 250 + 200 and 400 <= y <= 400 + 50:
                    return roles[0]  # Choisir Pacman
                elif 800 <= x <= 800 + 200 and 250 <= y <= 250 + 50:
                    return roles[1]  # Choisir Fantôme1
                elif 800 <= x <= 800 + 200 and 350 <= y <= 350 + 50:
                    return roles[2]  # Choisir Fantôme2
                elif 800 <= x <= 800 + 200 and 450 <= y <= 450 + 50:
                    return roles[3]  # Choisir Fantôme3
                elif 800 <= x <= 800 + 200 and 550 <= y <= 550 + 50:
                    return roles[4]  # Choisir Fantôme4
                elif 520 <= x <= 520 + 200 and 650 <= y <= 650 + 50:
                    return "back"  # Retour

        pygame.display.flip()




def main_menu(screen, image, font):
    """Menu principal du jeu"""
    
    run = True
    while run:
        screen.blit(image, (0, 0))

        # Titre du jeu
        title_image = pygame.image.load("images/Pacmint-texte.png").convert_alpha()
        original_width, original_height = title_image.get_size()
        new_width = original_width // 2
        new_height = original_height // 2
        title_image = pygame.transform.smoothscale(title_image, (new_width, new_height))

        # Recalcul du rectangle pour bien centrer l'image redimensionnée
        title_rect = title_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 230))

        # Affichage du titre
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
                        role = select_role(screen, font, mode="offline")
                        return "offline", role
                    elif 550 <= x <= 750:  # Mode En Ligne
                        return "online", None
                    elif 850 <= x <= 1050:  # Quitter
                        run = False
                        pygame.quit()
                        sys.exit()
                        
        pygame.display.flip()
    
    return None, None
