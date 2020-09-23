import pygame
from game import objects, entities, ui

pygame.init()
window = pygame.display.set_mode([1280, 720])
clock = pygame.time.Clock()

p = {"a" : "./assets/", "g" : "./assets/graphics/"}

class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.surface.Surface([1,1])
        self.rect = self.image.get_rect()
        self.rect.topleft = pygame.mouse.get_pos()
    def update(self):
        self.rect.topleft = pygame.mouse.get_pos()

class Highlight(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface([40, 40])
        self.image.fill([255, 255, 255])
        self.image.set_alpha(84)
        self.rect = self.image.get_rect()
        self.rect.center = 20, 20
    def draw(self):
        global window
        window.blit(self.image, self.rect.topleft)
    def update(self, tilegrp):
        global mouse
        if pygame.sprite.spritecollide(mouse, tilegrp, False):
            self.rect.center = pygame.sprite.spritecollide(mouse, tilegrp, False)[0].rect.center

def switchbuild():
    global building, buildimg, buildrect, buildindex
    building = builds[buildindex]
    buildimg = pygame.image.load(p["g"] + building + ".png")
    buildrect = buildimg.get_rect()
    buildrect = [-(buildrect.width / 2), -(buildrect.height / 2)]

def Enemy(pos):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0]*40)-20, (pos[1]*40)-20], pos, pos)
    newenemy.targetqueue = newenemy.pathfinding(listmap, [1, 10])
    enemygrp.add(newenemy)

mouse = Mouse()
highlight = Highlight()

running = True
screen = "game"
fps = 60 #hopefully

cash = 1000
wave = 1
wavestarted = False
building = None
buildimg = None
buildingcosts = {"shooter" : 100, "wall" : 75}
buildindex = 0
builds = ["shooter", "wall"]

bulletgrp = pygame.sprite.Group()
enemygrp = pygame.sprite.Group()

tilemap = pygame.sprite.Group()
towergrp = pygame.sprite.Group()
listmap = []
tilemap, towergrp, listmap = objects.GenerateMap()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            mouse.update()
            highlight.update(tilemap)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if building != None:
                if cash >= buildingcosts[building]:
                    towergrp.add(objects.Tower(highlight.rect.center, building))
                    cash -= buildingcosts[building]
                else:
                    pass #trigger message - not enough money!
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b and building == None:
                buildindex = 0
                switchbuild()
            elif event.key == pygame.K_b and building != None:
                building = None
                buildimg = None
            if event.key == pygame.K_LEFT and building != None:
                if buildindex == 0:
                    buildindex = len(builds)-1
                else:
                    buildindex -= 1
                switchbuild()
            if event.key == pygame.K_RIGHT and building != None:
                if buildindex == len(builds)-1:
                    buildindex = 0
                else:
                    buildindex += 1
                switchbuild()
            if event.key == pygame.K_w and not wavestarted:
                wavestarted = True
                pygame.time.set_timer(pygame.USEREVENT, 1000)
        if event.type == pygame.USEREVENT:
            Enemy([31, 15])
    if screen == "game":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        bulletgrp.draw(window)
        towergrp.draw(window)
        enemygrp.draw(window)

        if building != None:
            window.blit(buildimg, [highlight.rect.centerx + buildrect[0], highlight.rect.centery + buildrect[1]])
        else:
            highlight.draw()

        ui.text("cash - " + str(cash), [5, 5], window)
        ui.text("wave " + str(wave), [5, 22], window)

        towergrp.update(bulletgrp, enemygrp, clock)
        bulletgrp.update(enemygrp)
        enemygrp.update(fps)

    pygame.display.flip()
    clock.tick(60)
    fps = clock.get_fps()
pygame.quit()