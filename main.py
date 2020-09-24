import pygame
from game import objects, entities, ui

#Page w/Font Used: https://www.dafont.com/8-bit-pusab.font?l[]=10&l[]=1

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

class Data():
    def __init__(self):
        self.addmoney = 0

def switchbuild():
    global building, buildimg, buildrect, buildindex
    building = builds[buildindex]
    buildimg = pygame.image.load(p["g"] + building + ".png")
    buildrect = buildimg.get_rect()
    buildrect = [-(buildrect.width / 2), -(buildrect.height / 2)]

def Enemy(pos):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0]*40)-20, (pos[1]*40)-20], pos, pos)
    newenemy.targetqueue = newenemy.pathfinding(listmap, [1, 9])
    enemygrp.add(newenemy)

def CheckAccesible(pos):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0]*40)-20, (pos[1]*40)-20], pos, pos)
    newenemy.targetqueue = newenemy.pathfinding(listmap, [1, 9])
    if newenemy.targetqueue == []:
        return False
    else:
        return True

def GamePos(pos):
    return [int((pos[0]-20)/40), int((pos[1]-20)/40)]

def drawlistmap():
    global listmap
    for line in listmap:
        print(line)

mouse = Mouse()
highlight = Highlight()

running = True
screen = "game"
fps = 60 #hopefully

cash = 10000
wave = 1
wavestarted = False
building = None
buildimg = None
buildingcosts = {"shooter" : 100, "wall" : 25, "healer" : 250, "fxf_slowness" : 600}
buildindex = 0
builds = ["shooter", "wall", "healer", "fxf_slowness"]

data = Data()

bulletgrp = pygame.sprite.Group()
enemygrp = pygame.sprite.Group()
fieldgrp = pygame.sprite.Group()

tilemap = pygame.sprite.Group()
towergrp = pygame.sprite.Group()
listmap = []
tilemap, towergrp, listmap, metadata = objects.GenerateMap()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            mouse.update()
            highlight.update(tilemap)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #LEFT BUTTON
                if building != None:
                    if cash >= buildingcosts[building]:
                        newgpos = GamePos(highlight.rect.center)
                        towergrp.add(objects.Tower(highlight.rect.center, building, newgpos, fieldgrp))
                        cash -= buildingcosts[building]
                        if building.startswith("wall"):
                            listmap[newgpos[0]][newgpos[1]] = 2
                        else:
                            listmap[newgpos[0]][newgpos[1]] = 1
                    else:
                        pass #trigger message - not enough money!
            elif event.button == 4 and building != None:
                if buildindex == len(builds)-1:
                    buildindex = 0
                else:
                    buildindex += 1
                switchbuild()
            elif event.button == 5 and building != None:
                if buildindex == 0:
                    buildindex = len(builds)-1
                else:
                    buildindex -= 1
                switchbuild()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b and building == None:
                buildindex = 0
                switchbuild()
            elif event.key == pygame.K_b and building != None:
                building = None
                buildimg = None
            if bool(event.key == pygame.K_LEFT or event.key == pygame.K_DOWN) and building != None:
                if buildindex == 0:
                    buildindex = len(builds)-1
                else:
                    buildindex -= 1
                switchbuild()
            if bool(event.key == pygame.K_RIGHT or event.key == pygame.K_UP) and building != None:
                if buildindex == len(builds)-1:
                    buildindex = 0
                else:
                    buildindex += 1
                switchbuild()
            if event.key == pygame.K_w and not wavestarted:
                if CheckAccesible([31, 9]):
                    wavestarted = True
                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                else:
                    print("Can't reach base!!!")
            if event.key == pygame.K_l:
                drawlistmap()
        if event.type == pygame.USEREVENT:
            Enemy([32, 9])
    if screen == "game":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        bulletgrp.draw(window)
        towergrp.draw(window)
        enemygrp.draw(window)

        if building != None:
            window.blit(buildimg, [highlight.rect.centerx + buildrect[0], highlight.rect.centery + buildrect[1]])
        else:
            highlight.draw()

        if data.addmoney > 0:
            cash += 1
            data.addmoney -= 1

        ui.text("cash - " + str(cash), [5, 0], window)
        ui.text("wave " + str(wave), [5, 25], window)

        towergrp.update(bulletgrp, enemygrp, towergrp, clock)
        bulletgrp.update(enemygrp, data)
        enemygrp.update(fps, clock, data)
        fieldgrp.update()

    pygame.display.flip()
    clock.tick(60)
    fps = clock.get_fps()
pygame.quit()