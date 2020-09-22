import pygame, math
from pygame.math import Vector2

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, target, gamepos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/img.png")
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
    def pathfinding(self, listmap, goalpos):
        pass
        self.queue = []
        backtracked = []
        self.visited = {}
        maxtiles = 700
        iterations = 0
        self.queue.append([self.gpos, None])
        while len(self.queue) > 0:
            inbounds = True
            try:
                pos = self.queue[0][0]
            except:
                inbounds = False
            lastpos = self.queue[0][1]
            if inbounds:
                if self.checktile(listmap, pos, lastpos, goalpos):
                    break
            self.queue.pop(0)
            iterations += 1
            print(self.visited)
            if iterations >= maxtiles:
                backtraced = []
        if iterations >= maxtiles:
            backtraced = []
            pos = goalpos
            while str(pos) in self.visited and self.visited[str(pos)] != None:
                if pos != None:
                    backtraced.append([pos])
                pos = self.visited[str(pos)]
            backtraced.reverse()
        return backtraced
    def checktile(self, listmap, pos, lastpos, goalpos):
        try:
            fakevar = bool(listmap[pos[0]][pos[1]] == 1)
        except:
            return False
        if listmap[pos[0]][pos[1]] == 1:
            return False
        if str(pos) in self.visited:
            return False
        self.visited[str(pos)] = lastpos
        if pos == goalpos:
            return True
        self.queue.append([[pos[0], pos[1]+1], pos])
        self.queue.append([[pos[0]+1, pos[1]], pos])
        self.queue.append([[pos[0], pos[1]-1], pos])
        self.queue.append([[pos[0]-1, pos[1]], pos])
        return False
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
        if self.target[0]-5 < self.rect.centerx < self.target[0]+5 and self.target[1]-5 < self.rect.centery < self.target[1]+5:
            self.target = self.targetqueue[0]
            self.target = [(self.target[0]*40)-20, (self.target[1]*40)-20]
            self.targetqueue.pop(0)
        if self.health <= 0:
            self.kill()