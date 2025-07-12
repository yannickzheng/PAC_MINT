import pygame

class ChatBox:
    """Interface de chat pour le jeu multijoueur"""
    
    def __init__(self, x, y, width, height, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Zone de messages
        self.message_area_height = height - 30
        self.input_area_height = 25
        
        # État du chat
        self.messages = []
        self.current_input = ""
        self.is_active = False
        self.is_visible = True
        self.scroll_offset = 0
        
        # Couleurs
        self.bg_color = (0, 0, 0, 180)  # Fond semi-transparent
        self.border_color = (100, 100, 100)
        self.input_bg_color = (40, 40, 40)
        self.input_active_color = (60, 60, 60)
        self.text_color = (255, 255, 255)
        self.timestamp_color = (150, 150, 150)
        
    def toggle_visibility(self):
        """Basculer la visibilité du chat"""
        self.is_visible = not self.is_visible
        if not self.is_visible:
            self.is_active = False
    
    def add_message(self, player_name, message, timestamp=None):
        """Ajouter un message au chat"""
        import time
        if timestamp is None:
            timestamp = time.time()
        
        # Formater le timestamp
        time_str = time.strftime("%H:%M", time.localtime(timestamp))
        
        self.messages.append({
            "player_name": player_name,
            "message": message,
            "timestamp": time_str,
            "formatted": f"[{time_str}] {player_name}: {message}"
        })
        
        # Garder seulement les 50 derniers messages
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
    
    def handle_event(self, event):
        """Gérer les événements du chat"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t and not self.is_active:
                # Touche T pour activer le chat
                self.is_active = True
                return None
            elif event.key == pygame.K_ESCAPE and self.is_active:
                # Escape pour désactiver le chat
                self.is_active = False
                self.current_input = ""
                return None
            elif self.is_active:
                if event.key == pygame.K_RETURN:
                    # Envoyer le message
                    if self.current_input.strip():
                        message = self.current_input.strip()
                        self.current_input = ""
                        self.is_active = False
                        return message
                    else:
                        self.is_active = False
                        self.current_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    # Supprimer le dernier caractère
                    self.current_input = self.current_input[:-1]
                else:
                    # Ajouter le caractère saisi
                    if len(self.current_input) < 100:
                        self.current_input += event.unicode
        return None
    
    def draw(self, screen):
        """Dessiner le chat"""
        if not self.is_visible:
            return

        if self.is_active:
            chat_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Fond bien visible pour focus (plus opaque, genre 160-200)
            pygame.draw.rect(chat_surface, (0, 0, 0, 200), (0, 0, self.width, self.height))
            pygame.draw.rect(chat_surface, self.border_color, (0, 0, self.width, self.height), 1)
        
            # Zone de saisie
            input_y = self.height - self.input_area_height - 2
            input_color = self.input_active_color
            pygame.draw.rect(chat_surface, input_color, (2, input_y, self.width - 4, self.input_area_height))
        
            # Texte de saisie
            input_text = self.current_input + "|"
            if input_text:
                text_surface = self.small_font.render(input_text[:50], True, (255, 255, 255))
                chat_surface.blit(text_surface, (5, input_y + 3))
            else:
                placeholder = self.small_font.render("Tapez votre message...", True, (200, 200, 200))
                chat_surface.blit(placeholder, (5, input_y + 3))
        
            # Messages
            message_y = self.message_area_height - 20
            visible_messages = self.messages[-15:]  # Afficher les 15 derniers messages
        
            for message in reversed(visible_messages):
                if message_y < 5:
                    break
            
                # Découper le message en lignes si nécessaire
                lines = self.wrap_text(message["formatted"], self.width - 10)
            
                for line in reversed(lines):
                    if message_y < 5:
                        break
                    text_surface = self.small_font.render(line, True, self.text_color)
                    chat_surface.blit(text_surface, (5, message_y))
                    message_y -= 16
        
            screen.blit(chat_surface, (self.x, self.y))
            return
        # ----- Mode input inactif : juste overlay des messages (pas de boîte) -----
        overlay_x = self.x + 5
        overlay_y = self.y + 10
        visible_overlay = self.messages[-15:]  # Afficher 15 derniers messages
        for message in visible_overlay:
            lines = self.wrap_text(message["formatted"], self.width - 20)
            for line in lines:
                # Texte blanc, ombre légère si tu veux (optionnel)
                text_surface = self.small_font.render(line, True, (0, 0, 0))
                screen.blit(text_surface, (overlay_x, overlay_y))
                overlay_y += 18
    
    def wrap_text(self, text, max_width):
        """Découper le texte en lignes pour qu'il rentre dans la largeur"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.small_font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines