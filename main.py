import pygame, random
from game import objects, entities, ui

"""
L0ST_!N_CYBER$PACE
v1.0

by OrionDark7
Copyright (c) 2020 Orion Willams
See the LICENSE file for more info.

pyweek.org/e/slime30
oriondark7.com

Page w/Font Used: https://www.dafont.com/8-bit-pusab.font?l[]=10&l[]=1
"""

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode([1280, 720])
pygame.display.set_caption("Lost in Cyberspace")
clock = pygame.time.Clock()

p = {"a" : "./assets/", "g" : "./assets/graphics/", "t" : "./assets/graphics/towers/", "s":"./assets/sfx/"}

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
        self.smallrect = pygame.surface.Surface([20, 20])
        self.smallrect = self.smallrect.get_rect()
        self.image.fill([255, 255, 255])
        self.image.set_alpha(84)
        self.rect = self.image.get_rect()
        self.rect.center = 20, 20
    def draw(self):
        global window
        window.blit(self.image, self.rect.topleft)
    def gettower(self, towergrp):
        sprite = None
        oldrect = self.rect
        self.rect = self.smallrect
        self.rect.center = oldrect.center
        if pygame.sprite.spritecollide(self, towergrp, False):
            sprite = pygame.sprite.spritecollide(self, towergrp, False)[0]
        self.rect = oldrect
        self.rect.center = oldrect.center
        return sprite
    def update(self, tilegrp):
        global mouse
        if pygame.sprite.spritecollide(mouse, tilegrp, False):
            self.rect.center = pygame.sprite.spritecollide(mouse, tilegrp, False)[0].rect.center

class Data():
    def __init__(self):
        self.addmoney = 0
        self.metadata = {}
        self.gameover = False
        self.wave = 0
        self.base = None

def switchbuild():
    global building, buildimg, buildrect, buildindex
    building = builds[buildindex]
    buildimg = pygame.image.load(p["t"] + building + ".png")
    buildrect = buildimg.get_rect()
    buildrect = [-(buildrect.width / 2), -(buildrect.height / 2)]

def Enemy(pos, type="enemy"):
    global enemygrp, listmap
    if str(type) == "enemy" or str(type) == "enemyflying":
        newenemy = entities.Enemy([(pos[0]*40)+20, (pos[1]*40)+20], data.metadata["basepos"], pos, type, wave)
        newenemy.targetqueue = newenemy.pathfinding(listmap, data.metadata["basepos"])
        newenemy.goingbase = True
    if str(type) == "enemyshooter" or str(type) == "enemyshooterflying":
        newenemy = entities.Enemy([(pos[0] * 40) + 20, (pos[1] * 40) + 20], data.metadata["basepos"], pos, type, wave)
        if newenemy.closesttower("shooter", towergrp) == None:
            newenemy.targetqueue = newenemy.pathfinding(listmap, data.metadata["basepos"])
            newenemy.goingbase = True
        else:
            goto = GamePos(newenemy.closesttower("shooter", towergrp).rect.center)
            newenemy.targetqueue = newenemy.pathfinding(listmap, goto)
    if str(type) == "enemyfxf" or str(type) == "enemyfxfflying":
        newenemy = entities.Enemy([(pos[0] * 40) + 20, (pos[1] * 40) + 20], data.metadata["basepos"], pos, type, wave)
        if newenemy.closesttower("fxf", towergrp) == None:
            newenemy.targetqueue = newenemy.pathfinding(listmap, data.metadata["basepos"])
            newenemy.goingbase = True
        else:
            goto = GamePos(newenemy.closesttower("fxf", towergrp).rect.center)
            newenemy.targetqueue = newenemy.pathfinding(listmap, goto)
    if str(type) == "enemyboost" or str(type) == "enemyboostflying":
        newenemy = entities.Enemy([(pos[0] * 40) + 20, (pos[1] * 40) + 20], data.metadata["basepos"], pos, type, wave)
        if newenemy.closesttower("boost", towergrp) == None:
            newenemy.targetqueue = newenemy.pathfinding(listmap, data.metadata["basepos"])
            newenemy.goingbase = True
        else:
            goto = GamePos(newenemy.closesttower("boost", towergrp).rect.center)
            newenemy.targetqueue = newenemy.pathfinding(listmap, goto)
    if str(type) == "wallshooter":
        newenemy = entities.Enemy([(pos[0] * 40) + 20, (pos[1] * 40) + 20], data.metadata["basepos"], pos, type, wave)
        if newenemy.closesttower("wall", towergrp) == None:
            newenemy.targetqueue = newenemy.pathfinding(listmap, data.metadata["basepos"])
            newenemy.goingbase = True
        else:
            goto = GamePos(newenemy.closesttower("wall", towergrp).rect.center)
            newenemy.targetqueue = newenemy.pathfinding(listmap, goto)
    if len(newenemy.targetqueue) == 0:
        newenemy.targetqueue = newenemy.pathfinding(listmap, data.metadata["basepos"])
        newenemy.goingbase = True
    newenemy.target = [((newenemy.targetqueue[0][0]+1)*40)-20, ((newenemy.targetqueue[0][1]+1)*40)-20]
    newenemy.targetqueue.pop(0)
    enemygrp.add(newenemy)

def CheckAccesible(pos):
    global enemygrp, listmap
    newenemy = entities.Enemy([(pos[0]*40)+20, (pos[1]*40)+20], data.metadata["basepos"], pos, type="enemy")
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
    if str(name) == "fxf_damage":
        nname = "damage field"
    if str(name) == "shooter_rapid":
        nname = "rapid fire turret"
    if str(name) == "shooter":
        nname = "basic turret"
    if str(name) == "shooter_sniper":
        nname = "sniper turret"
    if str(name) == "boost_cooldown":
        nname = "overclock booster"
    if str(name) == "boost_damage":
        nname = "damage booster"
    if str(name) == "wall_strong":
        nname = "cyberwall"
    if str(name) == "healer_plus":
        nname = "healer plus"
    return nname

mouse = Mouse()
highlight = Highlight()

running = True
screen = "game"
fullscreen = False
prevscreen = "game"
fps = 60 #hopefully

howtoplay = pygame.image.load("./assets/graphics/story/howtoplay.png")
cash = 200
projectedcash = 200
path = []
playnext = None
currenttower = None
wave = 0
wavespawned = {}
wavespawns = [[["enemy",5,1000]], [["enemy",10,700]],
              [["enemy",7,1000],["enemy",7,600],["enemy",7,300]],
              [["enemyshooter",2,1000], ["enemy",10,700]],
              [["enemyshooter",3,700], ["enemy",10,1000], ["enemy",5,700]],
              [["enemy",25,500]],
              [["enemyflying",3,1000], ["enemy", 10, 700]],
              [["enemyflying",10,500], [["enemyshooterflying",3,700]]],
              [["enemyflying",25,700], ["enemy",5,1000]],
              [["enemyshooter",5,1000], ["enemyflying",5,700], ["enemyshooterflying",2,850], ["enemy",10,300]]]
wavestarted = False
keepspawning = False
building = None
buildimg = None
buildingcosts = {"shooter" : 100, "shooter_rapid" : 200, "shooter_sniper" : 175, "wall" : 25, "wall_strong" : 100, "healer" : 500, "healer_plus" : 1000,"fxf_slowness" : 1000, "fxf_damage" : 1700,
                 "boost_cooldown" : 1500, "boost_damage" : 2200}
buildindex = 0
builds = ["shooter", "shooter_rapid", "shooter_sniper", "wall", "wall_strong", "healer", "healer_plus", "fxf_slowness", "fxf_damage", "boost_cooldown", "boost_damage"]
descriptions = {"shooter" : ["shoots 2 bullets a second, each bullet does", "10hp of damage. medium range."],
                "shooter_rapid" : ["shoots around 7 bullets a second, each bullet does", "5hp of damage. short range."],
                "shooter_sniper" : ["shoots around 1 bullet a second, each bullet does", "20hp of damage. long range."],
                "wall" : ["i don't know, it exists? it protects stuff sometimes?", "it has 100 hitpoints, so that's pretty cool i guess."],
                "wall_strong" : ["what now? it's a wall, what do you want me to say?", "it has 400hp now, and that is pretty cool i'd say."],
                "healer" : ["this tower heals towers within a 2 tile radius.", "it heals 2hp every 5 seconds."],
                "healer_plus" : ["this tower heals towers within a 2 tile radius.", "it heals 5hp every 5 seconds."],
                "fxf_slowness" : ["all enemies that come within the effect field are", "slowed down to half speed for 2.5 seconds."],
                "fxf_damage" : ["all enemies that come within the effect field take", "damage every 2.5 seconds they are inside."],
                "boost_cooldown" : ["all towers in a 3 tile radius are sped", "up by 25%."],
                "boost_damage" : ["all shooting towers in a 3 tile radius", "have their damage boosted 50%."]}
ti = {}
for tower in builds:
    ti[tower] = pygame.transform.scale2x(pygame.image.load(p["t"]+str(tower)+".png"))
ti["base"] = pygame.image.load(p["t"]+"base.png")

sfxnames = ["basehit", "build", "enemyshoot", "playershoot", "select", "wavestart", "delete"]
sfx = {}
for name in sfxnames:
    sfx[name] = pygame.mixer.Sound(p["s"]+str(name)+".wav")
    sfx[name].set_volume(0.3)

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
ebuildbutton = ui.button("exit builds (b)", [640, 600], [255, 255, 255], [255, 255, 255], True)
gamebuttons.add(buildbutton)
gamebuttons.add(wavebutton)
gamebuttons.add(pausebutton)
gamebuttons.add(hidebutton)

pausebuttons = pygame.sprite.Group()
ui.fontsize(20)
resumebutton = ui.button("resume game", [640, 220], [255, 255, 255], [255, 255, 255], True)
phowtobutton = ui.button("how to play", [640, 320], [255, 255, 255], [255, 255, 255], True)
psettingsbutton = ui.button("settings", [640, 420], [255, 255, 255], [255, 255, 255], True)
pquitbutton = ui.button("quit game", [640, 520], [255, 255, 255], [255, 255, 255], True)
pausebuttons.add(resumebutton)
pausebuttons.add(phowtobutton)
pausebuttons.add(psettingsbutton)
pausebuttons.add(pquitbutton)

backbutton = ui.button("back", [20, 20], [255, 0, 0], [255, 0, 0])

howtobackdrop = pygame.surface.Surface([1260, 700])
howtobackdrop.fill([0, 0, 0, 128])
howtobackdrop.set_alpha(128)

pausemenubackdrop = pygame.surface.Surface([360, 480])
pausemenubackdrop.fill([0, 0, 0, 128])
pausemenubackdrop.set_alpha(128)

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

data.wave = wave
data.base = base

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
                ebuildbutton.update(mouse)
            elif screen == "paused":
                pausebuttons.update(mouse)
            elif screen == "howto":
                backbutton.update(mouse)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #LEFT BUTTON
                if screen == "howto":
                    if backbutton.click(mouse):
                        screen = prevscreen
                        sfx["select"].play()
                elif screen == "settings":
                    if backbutton.click(mouse):
                        screen = prevscreen
                        sfx["select"].play()
                elif screen == "paused":
                    if resumebutton.click(mouse):
                        screen = "game"
                        sfx["select"].play()
                    if phowtobutton.click(mouse):
                        prevscreen = screen
                        screen = "howto"
                        sfx["select"].play()
                    if psettingsbutton.click(mouse):
                        prevscreen = screen
                        screen = "settings"
                        sfx["select"].play()
                    if pquitbutton.click(mouse):
                        running = False
                elif screen == "game":
                    if building != None and ebuildbutton.click(mouse):
                        building = None
                        sfx["select"].play()
                    elif building != None:
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
                                    sfx["build"].play()
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
                                    sfx["build"].play()
                                else:
                                    effect([640, 580], "not enough money!", -0.05, 750, color=[255, 0, 0])
                            else:
                                effect([640, 580], "tower obstructs enemy path!", -0.05, 750, color=[255, 0, 0])
                        else:
                            effect([640, 580], "tile is occupied!", -0.05, 750, color=[255, 0, 0])
                    else:
                        if pausebutton.click(mouse) and showmenu:
                            screen = "paused"
                            sfx["select"].play()
                        elif wavebutton.click(mouse) and not wavestarted and showmenu and building == None:
                            if CheckAccesible([31, 9]) and CheckAccesible([31, 8]):
                                wavebutton.kill()
                                wavestarted = True
                                keepspawning = True
                                wave += 1
                                path = GetPath([31, 9])
                                sfx["select"].play()
                                playnext = "wavestart"
                                pygame.time.set_timer(pygame.USEREVENT + 1, 60)
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
                            sfx["select"].play()
                        elif hidebutton.click(mouse) and showmenu and building == None:
                            showmenu = False
                            sfx["select"].play()
            elif event.button == 4 and building != None:
                if buildindex == len(builds)-1:
                    buildindex = 0
                else:
                    buildindex += 1
                switchbuild()
                sfx["select"].play()
            elif event.button == 5 and building != None:
                if buildindex == 0:
                    buildindex = len(builds)-1
                else:
                    buildindex -= 1
                switchbuild()
                sfx["select"].play()
        if event.type == pygame.KEYDOWN:
            if screen == "paused":
                if event.key == pygame.K_ESCAPE:
                    screen = "game"
                    sfx["select"].play()
            elif screen == "game":
                if event.key == pygame.K_ESCAPE:
                    screen = "paused"
                    sfx["select"].play()
                if event.key == pygame.K_d:
                    if highlight.gettower(towergrp) != None:
                        if highlight.gettower(towergrp).type != "base":
                            data.addmoney += round(buildingcosts[highlight.gettower(towergrp).type]*0.5)
                            pos = GamePos(highlight.rect.center)
                            listmap[pos[0]][pos[1]] = 0
                            effect(highlight.rect.center,
                                   "+" + str(round(buildingcosts[highlight.gettower(towergrp).type] * 0.5)) + "B", -0.05,
                                   500, [85, 209, 72])
                            highlight.gettower(towergrp).kill()
                        else:
                            effect([640, 580], "are you trying to lose?", -0.05, 750, color=[255, 0, 0]) #seriously, why would you do this?
                if event.key == pygame.K_m and building == None:
                    showmenu = not showmenu
                    sfx["select"].play()
                if event.key == pygame.K_b and building == None:
                    buildindex = 0
                    switchbuild()
                    sfx["select"].play()
                elif event.key == pygame.K_b and building != None:
                    building = None
                    buildimg = None
                    sfx["select"].play()
                if bool(event.key == pygame.K_LEFT or event.key == pygame.K_DOWN) and building != None:
                    if buildindex == 0:
                        buildindex = len(builds)-1
                    else:
                        buildindex -= 1
                    switchbuild()
                    sfx["select"].play()
                if bool(event.key == pygame.K_RIGHT or event.key == pygame.K_UP) and building != None:
                    if buildindex == len(builds)-1:
                        buildindex = 0
                    else:
                        buildindex += 1
                    switchbuild()
                    sfx["select"].play()
                if event.key == pygame.K_w and not wavestarted:
                    if CheckAccesible([31, 9]) and CheckAccesible([31, 8]):
                        wavebutton.kill()
                        wavestarted = True
                        keepspawning = True
                        wave += 1
                        path = GetPath([31, 9])
                        sfx["select"].play()
                        playnext = "wavestart"
                        pygame.time.set_timer(pygame.USEREVENT+1, 60)
                        try:
                            wavespawned = wavespawns[wave - 1]
                        except:
                            screen = "levelcomplete"
                        pygame.time.set_timer(pygame.USEREVENT, 1000)
                    else:
                        effect([640, 580], "base not accesible!", -0.0375, 1000, color=[255, 0, 0])
                #if event.key == pygame.K_l:
                #    drawlistmap()
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        window = pygame.display.set_mode([1280, 720], pygame.FULLSCREEN)
                    else:
                        window = pygame.display.set_mode([1280, 720])
        if event.type == pygame.USEREVENT and wavestarted and keepspawning and screen == "game":
            #Enemy([31, random.randint(8, 9)], wavespawned[0][0])
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
        if event.type == pygame.USEREVENT+1 and playnext != None:
            sfx[str(playnext)].play()
            playnext = None
            pygame.time.set_timer(pygame.USEREVENT + 1, 60)
    if screen == "game":
        data.wave = wave
        data.base = base

        if base.health <= 0:
            screen = "gameover"
            data.gameended = True

        window.fill([255, 255, 255])

        tilemap.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        ebulletgrp.draw(window)
        enemygrp.draw(window)
        fieldgrp.draw(window)
        effectgrp.draw(window)

        if building != None:
            if building.startswith("shooter"):
                tempsurface = pygame.surface.Surface([objects.towers[building][1], objects.towers[building][1]])
                tempsurface.fill([0, 0, 0])
                tempsurface.set_colorkey([0, 0, 0])
                tempsurface.convert_alpha()
                tempsurface.set_alpha(64)
                pygame.draw.circle(tempsurface, [255, 255, 255], [objects.towers[building][1]/2, objects.towers[building][1]/2], objects.towers[building][1]/2)
                window.blit(tempsurface, [highlight.rect.centerx-objects.towers[building][1]/2, highlight.rect.centery-objects.towers[building][1]/2])
            window.blit(buildimg, [highlight.rect.centerx + buildrect[0], highlight.rect.centery + buildrect[1]])
        else:
            highlight.draw()
        if showmenu:
            window.blit(gamemenubackdrop, [400, 600])
            ui.fontsize(10)
            ui.text(str(cash) + " bitcoin", [480, 600], window, centered=True)
            if not wavestarted:
                if building != None:
                    ui.text("scroll to switch", [800, 600], window,
                            centered=True)
                    ui.color = [255, 255, 255]
                else:
                    ui.text("start wave " + str(wave + 1), [800, 600], window, centered=True)
            else:
                if building != None:
                    ui.text("scroll to switch", [800, 600], window,
                            centered=True)
                    ui.color = [255, 255, 255]
                else:
                    ui.text("wave " + str(wave), [800, 600], window,
                            centered=True)  # the x coordinate is a coincidence I swear
            if building != None:
                ebuildbutton.draw(window)
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
            elif not highlight.gettower(towergrp) == None:
                currenttower = highlight.gettower(towergrp)
                window.blit(ti[currenttower.type], [600, 560])
                ui.fontsize(21)
                ui.text(normalname(str(currenttower.type)), [640, 635], window, centered=True)
                ui.fontsize(12)
                ui.text(str(int(currenttower.health)) + "/" + str(int(currenttower.maxhealth)) + " health", [640, 675 ], window, centered=True)
                ui.fontsize(9)
                ui.text("press d to delete this tower. you will get a 50% refund", [640, 700],
                        window, centered=True)
            else:
                currenttower = None
                gamebuttons.draw(window)
            if len(enemygrp) == 0 and not keepspawning:
                wavestarted = False
                if not wavebutton in gamebuttons:
                    gamebuttons.add(wavebutton)
            ui.fontsize(18)
        if data.addmoney > 4:
            cash += 4
            data.addmoney -= 4
        elif data.addmoney < -4:
            cash -= 4
            data.addmoney += 4
        elif -3 < data.addmoney < 3:
            cash += data.addmoney
            data.addmoney = 0
            projectedcash = cash
        else:
            projectedcash = cash


        towergrp.update(bulletgrp, enemygrp, towergrp, effectgrp, clock)
        bulletgrp.update(enemygrp, towergrp, effectgrp, data)
        ebulletgrp.update(enemygrp, towergrp, effectgrp, data)
        enemygrp.update(fps, clock.get_time(), data, ebulletgrp, effectgrp, towergrp, highlight, listmap)
        fieldgrp.update(highlight, towergrp)
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
        ui.text("you win!", [640, 180], window, centered=True)

    if screen == "paused":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

        window.blit(pausemenubackdrop, [460, 120])
        ui.color = [255, 255, 255]
        ui.fontsize(30)
        ui.text("PAUSED", [640, 120], window, centered=True)

        pausebuttons.draw(window)

    if screen == "gameover":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

        window.blit(pausemenubackdrop, [460, 120])
        ui.fontsize(30)
        ui.color = [255, 0, 0]
        ui.text("game over!", [640, 120], window, centered=True)
        ui.color = [255, 255, 255]

    if screen == "howto":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

        window.blit(howtobackdrop, [10, 10])
        backbutton.draw(window)

        ui.color = [255, 255, 255]
        ui.fontsize(36)
        ui.text("HOW TO PLAY", [640, 10], window, centered=True)

        window.blit(howtoplay, [15, 80])

    if screen == "settings":
        window.fill([255, 255, 255])

        tilemap.draw(window)
        fieldgrp.draw(window)
        towergrp.draw(window)
        bulletgrp.draw(window)
        enemygrp.draw(window)

    pygame.display.flip()
    clock.tick(60)
    fps = clock.get_fps()
pygame.quit()