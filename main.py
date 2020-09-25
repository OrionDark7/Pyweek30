import pygame, random
from game import objects, entities, ui

#Page w/Font Used: https://www.dafont.com/8-bit-pusab.font?l[]=10&l[]=1

pygame.init()
window = pygame.display.set_mode([1280, 720])
pygame.display.set_caption("Lost in Cyberspace")
clock = pygame.time.Clock()

p = {"a" : "./assets/", "g" : "./assets/graphics/", "t" : "./assets/graphics/towers/"}

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
        self.smallrect = pygame.surface.Surface([30, 30])
        self.smallrect = self.smallrect.get_rect()
        self.image.fill([255, 255, 255])
        self.image.set_alpha(84)
        self.rect = self.image.get_rect()
        self.rect.center = 20, 20
    def draw(self):
        global window
        window.blit(self.image, self.rect.topleft)
    def gettower(self):
        global towergrp
        sprite = None
        oldrect = self.rect
        self.rect = self.smallrect
        self.rect.center = oldrect.center
        if pygame.sprite.spritecollide(self, towergrp, False):
            sprite = pygame.sprite.spritecollide(self, towergrp, False)[0]
        self.rect = oldrect
        return sprite
    def update(self, tilegrp):
        global mouse
        if pygame.sprite.spritecollide(mouse, tilegrp, False):
            self.rect.center = pygame.sprite.spritecollide(mouse, tilegrp, False)[0].rect.center

class Data():
    def __init__(self):
        self.addmoney = 0
        self.metadata = {}

def switchbuild():
    global building, buildimg, buildrect, buildindex
    building = builds[buildindex]
    buildimg = pygame.image.load(p["t"] + building + ".png")
    buildrect = buildimg.get_rect()
    buildrect = [-(buildrect.width / 2), -(buildrect.height / 2)]

def Enemy(pos, type="enemy"):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0]*40)+20, (pos[1]*40)+20], pos, pos, type)
    newenemy.targetqueue = newenemy.pathfinding(listmap, [1, 9])
    enemygrp.add(newenemy)

def CheckAccesible(pos):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0]*40)+20, (pos[1]*40)+20], pos, pos)
    newenemy.targetqueue = newenemy.pathfinding(listmap, [1, 9])
    if newenemy.targetqueue == []:
        return False
    else:
        return True

def GetPath(pos):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0] * 40) - 20, (pos[1] * 40) - 20], pos, pos)
    newenemy.targetqueue = newenemy.pathfinding(listmap, [1, 9])
    return newenemy.targetqueue

def GamePos(pos):
    return [int((pos[0]-20)/40), int((pos[1]-20)/40)]

def drawlistmap():
    global listmap
    for line in listmap:
        print(line)

def effect(position, text, speed, cooldown, color=[255, 255, 255]):
    global effectgrp
    prevsize = ui.size
    ui.fontsize(10)
    effectgrp.add(ui.effect(position, text, speed, cooldown, color))
    ui.fontsize(prevsize)

def heffect(position, cooldown, color=[255, 255, 255]):
    global effectgrp
    effectgrp.add(ui.heffect(position, cooldown, color))

def normalname(name):
    nname = name
    if str(name) == "fxf_slowness":
        nname = "slowness field"
    if str(name) == "shooter_rapid":
        nname = "rapid fire turret"
    if str(name) == "shooter":
        nname = "basic turret"
    return nname

mouse = Mouse()
highlight = Highlight()

running = True
screen = "game"
fullscreen = False
fps = 60 #hopefully

cash = 500
projectedcash = 500
path = []
currenttower = None
wave = 0
wavespawned = {}
wavespawns = [[["enemy",5,1000]], [["enemy",10,700]]]
wavestarted = False
keepspawning = False
building = None
buildimg = None
buildingcosts = {"shooter" : 100, "shooter_rapid" : 130, "wall" : 25, "healer" : 250, "fxf_slowness" : 500}
buildindex = 0
builds = ["shooter", "shooter_rapid","wall", "healer", "fxf_slowness"]
descriptions = {"shooter" : ["shoots 2 bullets a second, each bullet does", "10hp of damage. medium range."],
                "shooter_rapid" : ["shoots around 7 bullets a second, each bullet does", "5hp of damage. short range."],
                "wall" : ["i don't know, it exists? it protects stuff sometimes?", "it has 100 hitpoints, so that's pretty cool i guess."],
                "healer" : ["this tower heals towers within a 2 tile radius.", "it heals 2hp every 5 seconds."],
                "fxf_slowness" : ["all enemies that come within the effect field are", "slowed down to half speed for 4 seconds."]}
ti = {}
for tower in builds:
    ti[tower] = pygame.transform.scale2x(pygame.image.load(p["t"]+str(tower)+".png"))
ti["base"] = pygame.image.load(p["t"]+"base.png")

data = Data()
data.metadata["basepos"] = [1, 9]

gamebuttons = pygame.sprite.Group()
testbutton = ui.button("100 gecs", [20, 660], [255, 255, 255], [255, 255, 255]) #100 GECS BUTTON
ui.fontsize(16)
buildbutton = ui.button("build", [480, 670], [255, 255, 255], [255, 255, 255], True)
wavebutton = ui.button("start wave", [640, 670], [255, 255, 255], [255, 255, 255], True)
pausebutton = ui.button("pause", [800, 670], [255, 255, 255], [255, 255, 255], True)
ui.fontsize(8)
hidebutton = ui.button("hide menu (m)", [640, 600], [255, 255, 255], [255, 255, 255], True)
gamebuttons.add(buildbutton)
gamebuttons.add(wavebutton)
gamebuttons.add(pausebutton)
gamebuttons.add(hidebutton)

gamemenubackdrop = pygame.surface.Surface([480, 120])
gamemenubackdrop.fill([0, 0, 0, 128])
gamemenubackdrop.set_alpha(128)
showmenu = True

bulletgrp = pygame.sprite.Group()
ebulletgrp = pygame.sprite.Group()
enemygrp = pygame.sprite.Group()
fieldgrp = pygame.sprite.Group()
effectgrp = pygame.sprite.Group()

tilemap = pygame.sprite.Group()
towergrp = pygame.sprite.Group()
listmap = []
base = None
tilemap, towergrp, listmap, metadata, base = objects.GenerateMap()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            mouse.update()
            highlight.update(tilemap)
            if screen == "game":
                gamebuttons.update(mouse)
                hidebutton.update(mouse)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #LEFT BUTTON
                if building != None:
                    newgpos = GamePos(highlight.rect.center)
                    if listmap[newgpos[0]][newgpos[1]]==0:
                        if not newgpos in path and wavestarted:
                            if projectedcash >= buildingcosts[building]:
                                towergrp.add(objects.Tower(highlight.rect.center, building, newgpos, fieldgrp))
                                data.addmoney -= buildingcosts[building]
                                projectedcash -= buildingcosts[building]
                                if building.startswith("wall"):
                                    listmap[newgpos[0]][newgpos[1]] = 2
                                else:
                                    listmap[newgpos[0]][newgpos[1]] = 1
                                effect([480, 580], "-"+str(buildingcosts[building])+" bitcoin", -0.05, 750, color=[255, 255, 0])
                            else:
                                effect([640, 580], "not enough money!", -0.05, 750, color=[255, 0, 0])
                        elif not wavestarted:
                            if projectedcash >= buildingcosts[building]:
                                towergrp.add(objects.Tower(highlight.rect.center, building, newgpos, fieldgrp))
                                data.addmoney -= buildingcosts[building]
                                projectedcash -= buildingcosts[building]
                                if building.startswith("wall"):
                                    listmap[newgpos[0]][newgpos[1]] = 2
                                else:
                                    listmap[newgpos[0]][newgpos[1]] = 1
                                effect([480, 580], "-"+str(buildingcosts[building])+" bitcoin", -0.05, 750, color=[255, 255, 0])
                            else:
                                effect([640, 580], "not enough money!", -0.05, 750, color=[255, 0, 0])
                        else:
                            effect([640, 580], "tower obstructs enemy path!", -0.05, 750, color=[255, 0, 0])
                    else:
                        effect([640, 580], "tile is occupied!", -0.05, 750, color=[255, 0, 0])
                else:
                    if pausebutton.click(mouse) and showmenu:
                        screen = "paused"
                    elif wavebutton.click(mouse) and not wavestarted and showmenu and building == None:
                        if CheckAccesible([31, 9]) and CheckAccesible([31, 8]):
                            wavebutton.kill()
                            wavestarted = True
                            keepspawning = True
                            wave += 1
                            path = GetPath([31, 9])
                            try:
                                wavespawned = wavespawns[wave - 1]
                            except:
                                screen = "levelcomplete"
                            pygame.time.set_timer(pygame.USEREVENT, 1000)
                        else:
                            effect([640, 580], "base not accesible!", -0.0375, 1000, color=[255, 0, 0])
                    elif buildbutton.click(mouse) and showmenu and building == None:
                        buildindex = 0
                        switchbuild()
                    elif hidebutton.click(mouse) and showmenu and building == None:
                        showmenu = False
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
            if event.key == pygame.K_m and building == None:
                showmenu = not showmenu
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
                if CheckAccesible([31, 9]) and CheckAccesible([31, 8]):
                    wavebutton.kill()
                    wavestarted = True
                    keepspawning = True
                    wave += 1
                    path = GetPath([31, 9])
                    try:
                        wavespawned = wavespawns[wave - 1]
                    except:
                        screen = "levelcomplete"
                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                else:
                    effect([640, 580], "base not accesible!", -0.0375, 1000, color=[255, 0, 0])
            if event.key == pygame.K_l:
                drawlistmap()
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    window = pygame.display.set_mode([1280, 720], pygame.FULLSCREEN)
                else:
                    window = pygame.display.set_mode([1280, 720])
        if event.type == pygame.USEREVENT and wavestarted and keepspawning and screen == "game":
            try:
                Enemy([31, random.randint(8,9)], wavespawned[0][0])
            except:
                screen = "levelcomplete"
            if not screen == "levelcomplete":
                pygame.time.set_timer(pygame.USEREVENT, wavespawned[0][2])
            wavespawned[0][1] -= 1
            if wavespawned[0][1] <= 0:
                wavespawned.pop(0)
            if len(wavespawned) == 0:
                keepspawning = False
            if wave+1 == len(wavespawns)+1 and len(enemygrp) == 0:
                screen = "levelcomplete"
    if screen == "game":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        ebulletgrp.draw(window)
        enemygrp.draw(window)
        fieldgrp.draw(window)
        effectgrp.draw(window)

        if building != None:
            window.blit(buildimg, [highlight.rect.centerx + buildrect[0], highlight.rect.centery + buildrect[1]])
        else:
            highlight.draw()
        if showmenu:
            window.blit(gamemenubackdrop, [400, 600])
            ui.fontsize(10)
            ui.text(str(cash) + " bitcoin", [480, 600], window, centered=True)
            if not wavestarted:
                if building != None:
                    ui.color = [255, 0, 0]
                    ui.text("press b to cancel", [800, 600], window,
                            centered=True)
                    ui.color = [255, 255, 255]
                else:
                    ui.text("start wave " + str(wave + 1), [800, 600], window, centered=True)
            else:
                if building != None:
                    ui.color = [255, 0, 0]
                    ui.text("press b to cancel", [800, 600], window,
                            centered=True)
                    ui.color = [255, 255, 255]
                else:
                    ui.text("wave " + str(wave), [800, 600], window,
                            centered=True)  # the x coordinate is a coincidence I swear
            if building != None:
                window.blit(ti[building], [420, 630])
                ui.fontsize(21)
                ui.text(normalname(building), [510, 620], window)
                ui.fontsize(10)
                if cash >= buildingcosts[building]:
                    ui.color = [0, 255, 0]
                else:
                    ui.color = [255, 0, 0]
                ui.text("costs " + str(buildingcosts[building]) + " bitcoin", [510, 652], window)
                ui.color = [255, 255, 255]
                ui.fontsize(8)
                ui.text(str(descriptions[building][0]), [510, 675], window)
                ui.text(str(descriptions[building][1]), [510, 695], window)
            elif not highlight.gettower() == None:
                currenttower = highlight.gettower()
                window.blit(ti[currenttower.type], [600, 560])
                ui.fontsize(21)
                ui.text(normalname(str(currenttower.type)), [640, 640], window, centered=True)
                ui.fontsize(12)
                ui.text(str(int(currenttower.health)) + "/" + str(int(currenttower.maxhealth)) + " health", [640, 680], window, centered=True)
            else:
                currenttower = None
                gamebuttons.draw(window)
            if len(enemygrp) == 0 and not keepspawning:
                wavestarted = False
                if not wavebutton in gamebuttons:
                    gamebuttons.add(wavebutton)
            ui.fontsize(18)
        if data.addmoney > 0:
            cash += 1
            data.addmoney -= 1
        elif data.addmoney < 0:
            cash -= 1
            data.addmoney += 1
        else:
            projectedcash = cash

        if base.health <= 0:
            screen = "gameover"

        towergrp.update(bulletgrp, enemygrp, towergrp, effectgrp, clock)
        bulletgrp.update(enemygrp, towergrp, effectgrp, data)
        ebulletgrp.update(enemygrp, towergrp, effectgrp, data)
        enemygrp.update(fps, clock, data, ebulletgrp, highlight)
        fieldgrp.update()
        effectgrp.update(clock)
        ui.fontsize(18)

    if screen == "levelcomplete":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

        ui.fontsize(24)
        ui.text("level complete!", [640, 180], window, centered=True)

    if screen == "paused":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

    if screen == "gameover":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

        ui.fontsize(24)
        ui.color = [255, 0, 0]
        ui.text("level complete!", [640, 180], window, centered=True)
        ui.color = [255, 255, 255]
    pygame.display.flip()
    clock.tick(60)
    fps = clock.get_fps()
pygame.quit()