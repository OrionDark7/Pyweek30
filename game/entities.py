import pygame, math, random
from pygame.math import Vector2
from game import objects

enemies = {"enemy":[500, 50, 0.05, False]}
#cooldown, hp, speed, airborne?

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target, gamepos, type="enemy"):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/"+str(type)+".png")
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
        self.speed = self.attributes[2]
        self.health = self.attributes[1]
        self.shootcooldown = self.attributes[0]
        self.effect = None
        self.mask = pygame.mask.from_surface(self.image)
        self.rotated = 360
        self.shooting = False
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
        return backtraced
    def checktile(self, listmap, pos, lastpos, goalpos):
        returnval = False
        outrange = False
        try:
            fakevar = bool(listmap[pos[0]][pos[1]] == 1)
        except:
            outrange = True
        if not outrange:
            if listmap[pos[0]][pos[1]] > 0:
                #if listmap[pos[0]][pos[1]] == 2:
                #    print("in")
                #    returnval = True
                #    goalpos = pos
                #else:
                returnval = False
                self.visited[str(pos)] = lastpos
                #print("LALALALALALA")
                return returnval
            elif listmap[pos[0]][pos[1]] == -2:
                pos = goalpos
        else:
            returnval = False
            #print(str(pos) + "< CHECK")
        if str(pos) in self.visited.keys():
            returnval = False
            return returnval
        else:
            self.visited[str(pos)] = lastpos
        #print("GOT FAR")
        #print(pos, goalpos)
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
    def update(self, fps, clock, data, bulletgrp, highlight):
        if self.shooting:
            self.shootcooldown -= clock.get_time()
        if self.fxcooldown > 0:
            self.fxcooldown -= clock.get_time()
        if self.shootcooldown <= 0:
            pos = (self.rect.centerx + self.velocity.x * 10, self.rect.centery + self.velocity.y * 10)
            tempvelocity = Vector2(self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery).normalize() * clock.get_fps() * 0.1
            bulletgrp.add(objects.Bullet(self, pos, tempvelocity, self.rotation))
            self.shootcooldown = self.attributes[0]
        if self.fxcooldown <= 0:
            if self.effect == "slowness":
                self.speed = self.attributes[2]
            self.effect = None
            try:
                self.velocity = Vector2(self.target[0] - self.rect.centerx, self.target[1] - self.rect.centery).normalize() * fps * self.speed
            except:
                pass
            if not self.shooting:
                self.position += self.velocity
                self.rect.center = round(self.position[0]), round(self.position[1])
                if self.target[0] < self.rect.centerx:
                    self.rotation = 180
                elif self.target[0] > self.rect.centerx:
                    self.rotation = 0
                if self.target[1] < self.rect.centery:
                    self.rotation = 90
                elif self.target[1] > self.rect.centery:
                    self.rotation = 270
                if self.rotated != self.rotation:
                    if self.rotated < self.rotation:
                        self.rotated += 10
                    if self.rotated > self.rotation:
                        self.rotated -= 10
        else:
            self.rotation = math.atan(abs(self.shootingtarget.rect.centery - self.rect.centery) / abs(self.shootingtarget.rect.centerx - self.rect.centerx)) * 57.2958
            self.rotation = math.round(self.rotation)
            if self.rotated != self.rotation:
                if self.rotated < self.rotation:
                    self.rotated += 5
                if self.rotated > self.rotation:
                    self.rotated -= 5
        self.image = pygame.transform.rotate(self.originalimage, round(self.rotated))
        oldc = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = oldc
        if self.target[0]-5 < self.rect.centerx < self.target[0]+5 and self.target[1]-5 < self.rect.centery < self.target[1]+5:
            self.rect.center = self.target
            if not len(self.targetqueue) == 0:
                self.target = self.targetqueue[0]
                self.target = [((self.target[0]+1)*40)-20, ((self.target[1]+1)*40)-20]
                self.targetqueue.pop(0)
            else:
                if self.type == "enemy":
                    self.shootcooldown = self.attributes[0]
                    self.shooting = True
                    oldpos = highlight.rect.center
                    highlight.rect.center = self.originaltarget
                    self.shootingtarget = highlight.gettower()
        if self.health <= 0:
            self.kill()
            data.addmoney = int(round(self.attributes[1]/random.randint(9, 11)))