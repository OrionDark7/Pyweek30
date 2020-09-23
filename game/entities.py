import pygame, math
from pygame.math import Vector2

enemies = {"enemy":[500, 50, 0.05, False]}
#cooldown, hp, speed, airborne?

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target, gamepos, type="enemy"):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/enemy.png")
        self.originalimage = self.image
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position
        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.target = [(target[0]*40)-20, (target[1]*40)-20]
        self.targetqueue = []
        self.velocity = Vector2(target[0] - self.rect.centerx, target[1] - self.rect.centery).normalize()
        self.rotation = 0
        self.visited = {}
        self.gpos = gamepos
        self.health = 50
        self.queue = []
        self.cooldown = 0
        self.attributes = enemies["enemy"]
        self.speed = self.attributes[2]
        self.effect = None
    def pathfinding(self, listmap, goalpos, clock):
        if self.cooldown > 0:
            self.cooldown -= clock.get_time()
        if self.cooldown <= 0:
            if self.effect == "slowness":
                self.speed = self.attributes[2]
            self.effect = None
        self.queue = []
        self.visited = {}
        backtraced = []
        maxtiles = 2400
        iterations = 0
        found = False
        self.queue.append([self.gpos, None])
        while len(self.queue) > 0:
            print("START LOOP " + str(iterations))
            inbounds = True
            pos = self.queue[0][0]
            lastpos = self.queue[0][1]
            if self.checktile(listmap, pos, lastpos, goalpos):
                found = True
                break
            self.queue.pop(0)
            iterations += 1
            print("END LOOP")
            if iterations >= maxtiles:
                backtraced = []
                break
        if found:
            backtraced = []
            pos = goalpos
            print("IN")
            while str(pos) in self.visited and self.visited[str(pos)] != None:
                if pos != None:
                    backtraced.append(pos)
                pos = self.visited[str(pos)]
            backtraced.reverse()
            print(backtraced)
        return backtraced
    def checktile(self, listmap, pos, lastpos, goalpos):
        returnval = False
        outrange = False
        try:
            fakevar = bool(listmap[pos[0]][pos[1]] == 1)
        except:
            outrange = True
        if not outrange:
            if listmap[pos[0]][pos[1]] == 1:
                returnval = False
                self.visited[str(pos)] = lastpos
                print("LALALALALALA")
                return returnval
        else:
            returnval = False
            print(str(pos) + "< CHECK")
        if str(pos) in self.visited.keys():
            returnval = False
            return returnval
        else:
            self.visited[str(pos)] = lastpos
        print("GOT FAR")
        print(pos, goalpos)
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
    def update(self, fps):
        try:
            self.velocity = Vector2(self.target[0] - self.rect.centerx, self.target[1] - self.rect.centery).normalize() * fps * self.speed
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
            self.rotation = self.rotation
        elif (self.target[0] > self.rect.centerx and self.target[1] > self.rect.centery):
            self.rotation = self.rotation
        self.image = pygame.transform.rotate(self.originalimage, round(self.rotation))
        oldc = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = oldc
        if self.target[0]-5 < self.rect.centerx < self.target[0]+5 and self.target[1]-5 < self.rect.centery < self.target[1]+5:
            if not len(self.targetqueue) == 0:
                self.target = self.targetqueue[0]
                self.target = [((self.target[0]+1)*40)-20, ((self.target[1]+1)*40)-20]
                self.targetqueue.pop(0)
            else:
                pass #reroute or stay based on type of enemy
        if self.health <= 0:
            self.kill()