import pygame
class Player :
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.coord = (x,y)
        self.color = (255,0,0)
        self.squares = 2
        self.size = 10

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.squares
        if keys[pygame.K_RIGHT]:
            self.x += self.squares
        if keys[pygame.K_UP]:
            self.y -= self.squares
        if keys[pygame.K_DOWN]:
            self.y += self.squares

        self.coord = (self.x,self.y)

    def draw(self,screen):
        pygame.draw.circle(screen,self.color,(self.x,self.y),self.size//2)