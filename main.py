import pygame
from game import objects, entities

pygame.init()
window = pygame.display.set_mode([1280, 720])
running = True
screen = "game"

tilemap = pygame.sprite.Group()
towergrp = pygame.sprite.Group()
enemygrp = pygame.sprite.Group()
tilemap, towergrp = objects.GenerateMap()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if screen == "game":
        window.fill([255, 255, 255])
        tilemap.draw(window)
        towergrp.draw(window)

    pygame.display.flip()
pygame.quit()