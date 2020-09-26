import pygame, math, random
from pygame.math import Vector2
from game import objects, ui

pygame.init()
pygame.mixer.init()

enemies = {"enemy":[1000, 50, 0.03, False], "enemyflying":[500, 70, 0.06, True], "enemyshooter":[500, 70, 0.03, False], "enemyshooterflying":[500, 100, 0.06, True],
           "enemyfxf":[500, 70, 0.03, False], "enemyfxfflying":[500, 100, 0.06, True], "enemyboost":[500, 70, 0.03, False], "enemyboostflying":[500, 100, 0.06, True],
           "wallshooter":[500, 80, 0.03, False]}
sfxnames = ["basehit", "build", "enemyshoot", "playershoot", "select"]
shooters = ["enemy", "enemyflying", "enemyshooter", "enemyshooterflying", "enemyfxf", "enemyfxfflying", "enemyboost", "enemyboostflying", "wallshooter"]
sfx = {}
for name in sfxnames:
    sfx[name] = pygame.mixer.Sound("./assets/sfx/"+str(name)+".wav")
#cooldown, hp, speed, airborne?

def effect(position, text, speed, cooldown, effectgrp, color=[255, 255, 255]):
    prevsize = ui.size
    ui.fontsize(10)
    effectgrp.add(ui.effect(position, text, speed, cooldown, color))
    ui.fontsize(prevsize)

def GamePos(pos):
    return [int((pos[0]-20)/40), int((pos[1]-20)/40)]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target, gamepos, type="enemy"):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/enemies/"+str(type)+".png")
        self.originalimage = self.image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = [(target[0]*40)+20, (target[1]*40)+20]
        self.originaltarget = self.target
        self.targetqueue = []
        self.velocity = Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery).normalize()
        self.rotation = 360
        self.type = str(type)
        self.visited = {}
        self.gpos = gamepos
        self.queue = []
        self.fxcooldown = 0
        self.attributes = enemies[type]
        self.airborne = self.attributes[3]
        self.speed = self.attributes[2]
        self.health = self.attributes[1]
        self.shootcooldown = self.attributes[0]
        self.effect = None
        self.mask = pygame.mask.from_surface(self.image)
        self.rotated = 360
        self.shooting = False
    def closesttower(self, type, towergrp):
        distances = []
        remainingtowers = []
        for tower in towergrp:
            if tower.type.startswith(str(type)):
                remainingtowers.append(tower)
                distance = math.sqrt(abs((tower.rect.centerx - self.rect.centerx) ^ 2 + (tower.rect.centery - self.rect.centery) ^ 2))
                distances.append(distance)
        if type == "boost":
            for tower in towergrp:
                if tower.type.startswith(str("healer")):
                    remainingtowers.append(tower)
                    distance = math.sqrt(abs(
                        (tower.rect.centerx - self.rect.centerx) ^ 2 + (tower.rect.centery - self.rect.centery) ^ 2))
                    distances.append(distance)
        try:
            shortest = min(distances)
        except:
            return None
        sindex = distances.index(shortest)
        if len(remainingtowers) == 0:
            return None
        return remainingtowers[sindex]
    def pathfinding(self, listmap, goalpos):
        self.queue = []
        self.visited = {}
        backtraced = []
        maxtiles = 2400
        iterations = 0
        found = False
        self.queue.append([self.gpos, None])
        while len(self.queue) > 0:
            #print("START LOOP " + str(iterations))
            inbounds = True
            pos = self.queue[0][0]
            lastpos = self.queue[0][1]
            if self.checktile(listmap, pos, lastpos, goalpos):
                found = True
                break
            self.queue.pop(0)
            iterations += 1
            #print("END LOOP")
            if iterations >= maxtiles:
                backtraced = []
                break
        if found:
            backtraced = []
            pos = goalpos
            #print("IN")
            while str(pos) in self.visited and self.visited[str(pos)] != None:
                if pos != None:
                    backtraced.append(pos)
                pos = self.visited[str(pos)]
            backtraced.pop(0)
            backtraced.reverse()
        self.originaltarget = [(goalpos[0]*40)+20, (goalpos[1]*40)+20]
        return backtraced
    def checktile(self, listmap, pos, lastpos, goalpos):
        returnval = False
        outrange = False
        try:
            fakevar = bool(listmap[pos[0]][pos[1]] == 1)
        except:
            outrange = True
        if not outrange:
            if not pos == goalpos:
                if listmap[pos[0]][pos[1]] > 0 and not self.airborne:
                    returnval = False
                    self.visited[str(pos)] = lastpos
                    return returnval
                elif listmap[pos[0]][pos[1]] == 2 and not self.airborne and self.type.startswith("wall"):
                    pos = goalpos
                    self.originaltarget = [(pos[0]*40)+20, (pos[1]*40)+20]
                elif listmap[pos[0]][pos[1]] == -2 and self.type == "enemy":
                    pos = goalpos
        else:
            returnval = False
        if str(pos) in self.visited.keys():
            returnval = False
            return returnval
        else:
            self.visited[str(pos)] = lastpos
        if pos == goalpos:
            returnval = True
        if not returnval:
            if not pos[0] < 0 and not pos[1]+1 < 0 and not pos[0]>31 and not pos[1]+1>15:
                self.queue.append([[pos[0], pos[1]+1], pos])
            if not pos[0]+1 < 0 and not pos[1] < 0 and not pos[0]+1>31 and not pos[1]>15:
                self.queue.append([[pos[0]+1, pos[1]], pos])
            if not pos[0] < 0 and not pos[1] - 1 < 0 and not pos[0]>31 and not pos[1]-1>15:
                self.queue.append([[pos[0], pos[1]-1], pos])
            if not pos[0]-1 < 0 and not pos[1] < 0 and not pos[0]-1>31 and not pos[1]>15:
                self.queue.append([[pos[0]-1, pos[1]], pos])
        return returnval
    def update(self, fps, clock, data, bulletgrp, effectgrp, towergrp, highlight, listmap):
        if not data.gameover:
            if self.shooting:
                self.shootcooldown -= clock
                oldpos = highlight.rect.center
                highlight.rect.center = self.originaltarget
                self.shootingtarget = highlight.gettower(towergrp)
                highlight.rect.center = oldpos
                exitloop = False
                if self.shootingtarget == None:
                    exitloop = True
                if exitloop:
                    print("exitloop")
                    if str(self.type) == "enemy" or str(self.type) == "enemyflying":
                        self.targetqueue = self.pathfinding(listmap, data.metadata["basepos"])
                    elif str(self.type) == "enemyshooter" or str(self.type) == "enemyshooterflying":
                        if self.closesttower("shooter", towergrp) == None:
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, data.metadata["basepos"])
                        else:
                            goto = GamePos(self.closesttower("shooter", towergrp).rect.center)
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, goto)
                    elif str(self.type) == "enemyfxf" or str(self.type) == "enemyfxfflying":
                        if self.closesttower("fxf", towergrp) == None:
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, data.metadata["basepos"])
                        else:
                            goto = GamePos(self.closesttower("fxf", towergrp).rect.center)
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, goto)
                    elif str(self.type) == "enemyboost" or str(self.type) == "enemyboostflying":
                        if self.closesttower("boost", towergrp) == None:
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, data.metadata["basepos"])
                        else:
                            goto = GamePos(self.closesttower("boost", towergrp).rect.center)
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, goto)
                    elif str(self.type) == "wallshooter":
                        if self.closesttower("wall", towergrp) == None:
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, data.metadata["basepos"])
                        else:
                            goto = GamePos(self.closesttower("wall", towergrp).rect.center)
                            self.gpos = GamePos(self.rect.center)
                            self.targetqueue = self.pathfinding(listmap, goto)
                    if len(self.targetqueue) == 0:
                        self.targetqueue = self.pathfinding(listmap, data.metadata["basepos"])
                    if not len(self.targetqueue) == 0:
                        self.target = [((self.targetqueue[0][0] + 1) * 40) - 20, ((self.targetqueue[0][1] + 1) * 40) - 20]
                        self.targetqueue.pop(0)
                    self.shooting = False
                    self.shootingtarget = None
            if self.fxcooldown > 0:
                self.fxcooldown -= clock
            if self.shootcooldown <= 0 and self.type in shooters and self.shooting:
                pos = self.rect.center
                tempvelocity = Vector2(self.shootingtarget.rect.centerx - self.rect.centerx, self.shootingtarget.rect.centery - self.rect.centery).normalize() * fps * 0.1
                bulletgrp.add(objects.Bullet(self, pos, tempvelocity, self.rotation))
                self.shootcooldown = self.attributes[0]
                sfx["enemyshoot"].play()
            if self.fxcooldown <= 0:
                if self.effect == "slowness":
                    self.speed = self.attributes[2]
                self.effect = None
                try:
                    self.velocity = Vector2(self.target[0] - self.rect.centerx, self.target[1] - self.rect.centery).normalize() * fps * self.speed
                except:
                    pass
            else:
                try:
                    self.velocity = Vector2(self.target[0] - self.rect.centerx, self.target[1] - self.rect.centery).normalize() * fps * self.speed
                except:
                    pass
            if not self.shooting:
                self.position += self.velocity
                self.rect.center = round(self.position[0]), round(self.position[1])
                self.velocity = Vector2(round(self.velocity.x), round(self.velocity.y))
                if self.velocity.x < 0:
                    self.rotation = 180
                if self.velocity.x > 0:
                    self.rotation = 0
                if self.velocity.y < 0:
                    self.rotation = 90
                if self.velocity.y > 0:
                    self.rotation = 270
                if self.rotated != self.rotation:
                    if self.rotated < self.rotation:
                        self.rotated += 10
                    if self.rotated > self.rotation:
                        self.rotated -= 10
            if self.shooting:
                if self.rect.centerx == self.shootingtarget.rect.centerx:
                    if self.rect.centery < self.shootingtarget.rect.centery:
                        self.rotation = 270
                    elif self.rect.centery > self.shootingtarget.rect.centery:
                        self.rotation = 90
                elif self.rect.centery == self.shootingtarget.rect.centery:
                    if self.rect.centerx < self.shootingtarget.rect.centerx:
                        self.rotation = 0
                    elif self.rect.centerx > self.shootingtarget.rect.centerx:
                        self.rotation = 0
                else:
                    self.rotation = math.atan(abs(self.shootingtarget.rect.centery - self.rect.centery) / abs(self.shootingtarget.rect.centerx - self.rect.centerx)) * 57.2958
                self.rotation = round(self.rotation)
                if self.shootingtarget.rect.centerx < self.rect.centerx and self.shootingtarget.rect.centery < self.rect.centerx:
                    self.rotation = -self.rotation+180
                if self.shootingtarget.rect.centerx < self.rect.centerx and self.shootingtarget.rect.centery > self.rect.centerx:
                    self.rotation = -self.rotation+180
            if self.rotated != self.rotation:
                if self.rotated < self.rotation:
                    self.rotated += 5
                if self.rotated > self.rotation:
                    self.rotated -= 5
            self.image = pygame.transform.rotate(self.originalimage, round(self.rotation))
            oldc = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = oldc
            if self.target[0]-5 < self.rect.centerx < self.target[0]+5 and self.target[1]-5 < self.rect.centery < self.target[1]+5:
                self.rect.center = self.target
                self.gpos = GamePos(self.rect.center)
                if len(self.targetqueue) != 0:
                    self.target = self.targetqueue[0]
                    self.target = [((self.target[0]+1)*40)-20, ((self.target[1]+1)*40)-20]
                    self.targetqueue.pop(0)
                elif len(self.targetqueue) == 0:
                    if self.type in shooters:
                        self.shooting = True
                        oldpos = highlight.rect.center
                        highlight.rect.center = self.originaltarget
                        self.shootingtarget = highlight.gettower(towergrp)
                        highlight.rect.center = oldpos
            if self.health <= 0:
                self.kill()
                cash = int(round(self.attributes[1]/random.randint(9, 11)))
                effect(self.rect.center, "+"+str(cash)+"B", 0.05, 100, effectgrp, [85, 209, 72])
                data.addmoney += cash