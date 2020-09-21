import pygame, math
from pygame.math import Vector2

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/img.png")
        self.originalimage = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position
        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = target
        self.velocity = Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery).normalize()
        self.rotation = 0
        self.health = 50
    def pathfinding(self, listmap):
    def update(self, fps):
        try:
            self.velocity = Vector2(self.target[0] - self.rect.centerx, self.target[1] - self.rect.centery).normalize() * fps * 0.05
        except:
            pass
        self.position += self.velocity
        self.rect.center = round(self.position[0]), round(self.position[1])
        #print(math.atan(abs(self.target[1] - self.rect.centery)/abs(self.target[0] - self.rect.centerx))*57.2958)
        try:
            self.rotation = math.atan(abs(self.target[1] - self.rect.centery)/abs(self.target[0] - self.rect.centerx))*57.2958
            self.rotation = math.round(self.rotation)
        except:
            pass
        if (self.target[0] < self.rect.centerx and self.target[1] < self.rect.centery):
            self.rotation = -self.rotation
        elif (self.target[0] > self.rect.centerx and self.target[1] > self.rect.centery):
            self.rotation = -self.rotation
        self.image = pygame.transform.rotate(self.originalimage, round(self.rotation))
        oldc = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = oldc
        if self.health <= 0:
            self.kill()