import pygame
import sys
from common.global_variable import WIDTH, HEIGHT, BLUE, CYAN, PURPLE

from game.ui.components import draw_button

def create_game(screen, image, font):
    """Menu de création de partie"""
    game_code = None
    run = True

    while run:
        screen.blit(image, (0, 0))
        draw_button("Lancer la partie", 550, 600, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Retour", 850, 600, 200, 50, BLUE, PURPLE, screen, font)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # Vérifier si le bouton musique est cliqué

                # Vérifier les boutons en bas de l'écran
                if 600 <= y <= 650:
                    if 550 <= x <= 750:  # Lancer la partie
                        return "start"
                    elif 850 <= x <= 1050:  # Retour
                        return "back"
                        
        pygame.display.flip()
    
    return None

def join_game(screen, image, font):
    """Menu pour rejoindre une partie"""
    from common.global_variable import WHITE
    
    run = True
    game_code = ""
    input_active = False
    input_box = pygame.Rect(250, 600, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = BLUE

    while run:
        screen.blit(image, (0, 0))

        draw_button("Rejoindre", 550, 600, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Retour", 850, 600, 200, 50, BLUE, PURPLE, screen, font)

        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(game_code, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if input_box.collidepoint(event.pos):
                    input_active = not input_active
                else:
                    input_active = False
                color = color_active if input_active else color_inactive

                if 600 <= y <= 650:
                    if 550 <= x <= 750 and game_code:
                        return game_code
                    elif 850 <= x <= 1050:
                        return "back"

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    return game_code
                elif event.key == pygame.K_BACKSPACE:
                    game_code = game_code[:-1]
                else:
                    game_code += event.unicode

        pygame.display.flip()
    
    return None

def online_menu(screen, image, font):
    """Page de sélection pour le mode en ligne (créer ou rejoindre une partie)"""
    run = True
    while run:
        screen.blit(image, (0, 0))
        
        # Titre
        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        title_text = title_font.render("Mode En Ligne", True, (255, 255, 0))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 200))
        
        # Boutons positionnés en bas de l'écran
        draw_button("Créer une partie", 250, 600, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Rejoindre une partie", 550, 600, 200, 50, BLUE, CYAN, screen, font)
        draw_button("Retour", 850, 600, 200, 50, BLUE, PURPLE, screen, font)
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Vérifier les boutons en bas de l'écran
                if 600 <= y <= 650:
                    if 250 <= x <= 450:  # Créer une partie
                        return "create"
                    elif 550 <= x <= 750:  # Rejoindre une partie
                        return "join"
                    elif 850 <= x <= 1050:  # Retour
                        return "back"
                        
        pygame.display.flip()
    
    return None
