import pygame

def login_screen(screen, font):
    clock = pygame.time.Clock()

    username = ""
    password = ""
    active_input = "username"
    input_rects = {
        "username": pygame.Rect(300, 200, 300, 40),
        "password": pygame.Rect(300, 270, 300, 40),
        "button": pygame.Rect(300, 340, 300, 50)
    }

    running = True
    while running:
        screen.fill((0, 0, 0))

        # Dessin des étiquettes
        username_label = font.render("Nom d'utilisateur:", True, (255, 255, 255))
        password_label = font.render("Mot de passe:", True, (255, 255, 255))
        screen.blit(username_label, (100, 205))
        screen.blit(password_label, (100, 275))

        # Affichage des zones de texte
        pygame.draw.rect(screen, (255, 255, 255), input_rects["username"], 2)
        pygame.draw.rect(screen, (255, 255, 255), input_rects["password"], 2)

        username_surface = font.render(username, True, (255, 255, 0))
        password_surface = font.render("*" * len(password), True, (255, 255, 0))

        screen.blit(username_surface, (input_rects["username"].x + 5, input_rects["username"].y + 5))
        screen.blit(password_surface, (input_rects["password"].x + 5, input_rects["password"].y + 5))

        # Dessin du bouton
        pygame.draw.rect(screen, (50, 200, 50), input_rects["button"])
        button_text = font.render("Se connecter", True, (0, 0, 0))
        screen.blit(button_text, (input_rects["button"].x + 50, input_rects["button"].y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rects["username"].collidepoint(event.pos):
                    active_input = "username"
                elif input_rects["password"].collidepoint(event.pos):
                    active_input = "password"
                elif input_rects["button"].collidepoint(event.pos):
                    return username, password

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_input = "password" if active_input == "username" else "username"

                elif event.key == pygame.K_RETURN:
                    return username, password

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
