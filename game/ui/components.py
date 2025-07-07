import pygame
from common.global_variable import WHITE

def draw_button(text, x, y, width, height, base_color, glow_color, screen, font):
    # permet de vérifier la position de la souris sur le bouton
    mouse_pos = pygame.mouse.get_pos()
    hover = (x <= mouse_pos[0] <= x + width) and (y <= mouse_pos[1] <= y + height)

    # ajout de l'effet de lumière autour du bouton
    if hover:
        for i in range(10):
            glow_radius = i * 2
            glow_surface = pygame.Surface((width + glow_radius * 2, height + glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, 50 - i * 5),
                             (0, 0, width + glow_radius * 2, height + glow_radius * 2), border_radius=10)
            screen.blit(glow_surface, (x - glow_radius, y - glow_radius))

    # dégradé de couleur du bouton
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height):
        alpha = int(255 * (i / height))
        color = (*base_color, alpha)
        pygame.draw.line(button_surface, color, (0, i), (width, i))
    screen.blit(button_surface, (x, y))
    # ajoute un contour de lumière autour du bouton
    pygame.draw.rect(screen, glow_color, (x, y, width, height), 3, border_radius=10)
    # permet de centrer le texte dans le bouton
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

def display_loading_screen(message, screen, font):
    """Affiche un écran de chargement avec un message personnalisable"""
    screen.fill((0, 0, 0))
    loading_font = pygame.font.SysFont("Arial", 36, bold=True)
    loading_text = loading_font.render(message, True, (255, 255, 255))
    loading_rect = loading_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(loading_text, loading_rect)
    
    # Animation de points
    dots = "..." * ((pygame.time.get_ticks() // 500) % 4)
    dots_text = loading_font.render(dots, True, (255, 255, 255))
    dots_rect = dots_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
    screen.blit(dots_text, dots_rect)
    
    pygame.display.flip()

def game_over(score, screen, font):
    """Affiche l'écran de Game Over avec le score final."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Titre Game Over
    game_over_font = pygame.font.SysFont("Arial", 72, bold=True)
    game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))
    screen.blit(game_over_text, game_over_rect)
    
    # Score final
    score_font = pygame.font.SysFont("Arial", 48)
    score_text = score_font.render(f"Score Final: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(score_text, score_rect)
    
    # Instructions
    instruction_font = pygame.font.SysFont("Arial", 24)
    instruction_text = instruction_font.render("Appuyez sur une touche pour continuer...", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 100))
    screen.blit(instruction_text, instruction_rect)
    
    pygame.display.flip()
    
    # Attendre qu'une touche soit pressée
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


def you_win(score, screen, font):
    """Affiche l'écran de victoire avec le score final."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Titre Game Over
    game_over_font = pygame.font.SysFont("Arial", 72, bold=True)
    game_over_text = game_over_font.render("YOU WIN !", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 100))
    screen.blit(game_over_text, game_over_rect)

    # Score final
    score_font = pygame.font.SysFont("Arial", 48)
    score_text = score_font.render(f"Score Final: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(score_text, score_rect)

    # Instructions
    instruction_font = pygame.font.SysFont("Arial", 24)
    instruction_text = instruction_font.render("Appuyez sur une touche pour continuer...", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
    screen.blit(instruction_text, instruction_rect)

    pygame.display.flip()

    # Attendre qu'une touche soit pressée
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
