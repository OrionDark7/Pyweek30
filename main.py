import pygame
from game import objects, entities

pygame.init()
window = pygame.display.set_mode([1280, 720])
clock = pygame.time.Clock()

running = True
screen = "game"
fps = 60 #hopefully

bulletgrp = pygame.sprite.Group()
enemygrp = pygame.sprite.Group()

tilemap = pygame.sprite.Group()
towergrp = pygame.sprite.Group()
tilemap, towergrp = objects.GenerateMap()

enemy = entities.Enemy([640.0, 360.0], [20, 120])
enemygrp.add(enemy)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if screen == "game":
        window.fill([255, 255, 255])
        tilemap.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)
        towergrp.update(bulletgrp, enemygrp, clock)
        bulletgrp.update(enemygrp)
        enemygrp.update(fps)
        print(enemygrp)
    pygame.display.flip()
    clock.tick(60)
    fps = clock.get_fps()
pygame.quit()