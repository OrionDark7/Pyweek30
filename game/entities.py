import pygame, math
from pygame.math import Vector2

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface([30, 30])
        self.image.fill([255, 0, 0])
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position
        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = target
        self.velocity = Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery).normalize()
        self.rotation = 0
    def update(self):
        self.velocity = Vector2(self.target[0] - self.rect.centerx, self.target[1] - self.rect.centery).normalize()
        self.position += self.velocity
        self.rect.center = round(self.position[0]), round(self.position[1])
        self.rotation = math.asin()