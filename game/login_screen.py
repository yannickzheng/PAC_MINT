import pygame
from game.api import login

def login_screen(screen, font):
    clock = pygame.time.Clock()

    username = ""
    password = ""
    error_message = ""
    active_input = "username"

    input_rects = {
        "username": pygame.Rect(300, 200, 300, 40),
        "password": pygame.Rect(300, 270, 300, 40),
        "button": pygame.Rect(300, 340, 300, 50)
    }

    running = True
    while running:
        screen.fill((0, 0, 0))

        # Labels
        screen.blit(font.render("Nom d'utilisateur:", True, (255, 255, 255)), (100, 205))
        screen.blit(font.render("Mot de passe:", True, (255, 255, 255)), (100, 275))

        # Input boxes
        pygame.draw.rect(screen, (255, 255, 255), input_rects["username"], 2)
        pygame.draw.rect(screen, (255, 255, 255), input_rects["password"], 2)

        username_surface = font.render(username, True, (255, 255, 0))
        password_surface = font.render("*" * len(password), True, (255, 255, 0))

        screen.blit(username_surface, (input_rects["username"].x + 5, input_rects["username"].y + 5))
        screen.blit(password_surface, (input_rects["password"].x + 5, input_rects["password"].y + 5))

        # Login button
        pygame.draw.rect(screen, (50, 200, 50), input_rects["button"])
        screen.blit(font.render("Se connecter", True, (0, 0, 0)), (input_rects["button"].x + 50, input_rects["button"].y + 10))

        # Error message if needed
        if error_message:
            error_surface = font.render(error_message, True, (255, 0, 0))
            screen.blit(error_surface, (300, 410))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rects["username"].collidepoint(event.pos):
                    active_input = "username"
                elif input_rects["password"].collidepoint(event.pos):
                    active_input = "password"
                elif input_rects["button"].collidepoint(event.pos):
                    result = login(username, password)
                    if isinstance(result, int):
                        return username, password, result
                    else:
                        error_message = "Identifiants invalides"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_input = "password" if active_input == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    result = login(username, password)
                    if isinstance(result, int):
                        return username, password, result
                    else:
                        error_message = "Identifiants invalides"
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                else:
                    char = event.unicode
                    if char.isprintable():
                        if active_input == "username":
                            username += char
                        else:
                            password += char

        clock.tick(30)
