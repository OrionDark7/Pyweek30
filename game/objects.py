import pygame, math
from pygame.math import Vector2

towers = {"shooter" : [500, 600, 50], "base" : [0, 0, 250], "wall" : [0, 0, 100]}
bullets = {"shooter" : [10]}
#name - speed (ms/action), range (pixels), hp
#name - damage

def GenerateMap():
    #just blank for now, maybe add presets later? 9.19.2020
    TileGroup = pygame.sprite.Group()
    TowerGroup = pygame.sprite.Group()
    listmap = []

    for x in range(32):
        listmap.append([])
        for y in range(18):
            listmap[x].append(0)
            NewTile = Tile([x*40, y*40], "regular")
            TileGroup.add(NewTile)
    TowerGroup.add(Tower([40, 360], "base", [0, 9]))
    TowerGroup.add(Tower([20, 420], "shooter",  [0, 11]))
    listmap[0][11] = 1
    TowerGroup.add(Tower([20, 300], "shooter", [0, 8]))
    listmap[0][8] = 1
    return TileGroup, TowerGroup, listmap

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, type, occupied=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/tile.png")
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.type = str(type)
        self.gpos = [self.rect.left/40, self.rect.top/40]
        self.occupied = False
    def update(self):
        pass

class Tower(pygame.sprite.Sprite):
    def __init__(self, position, type, gamepos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/"+type+".png")
        self.originalimage = self.image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.type = str(type)
        self.attributes = towers[self.type]
        self.rotation = 0
        self.target = None
        self.gpos = list(gamepos)
        self.cooldown = self.attributes[0]
        self.rangesurface = self.rect
        if self.type.startswith("shooter"):
            self.rangesurface = pygame.surface.Surface([self.attributes[1], self.attributes[1]])
            self.rangesurface = self.rangesurface.get_rect()
    def update(self, bulletgrp, enemygrp, clock):
        self.cooldown -= clock.get_time()
        if self.target != None:
            if not self.target.alive():
                self.target = None
        if self.cooldown <= 0:
            if self.target != None:
                self.velocity = Vector2(self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery).normalize() * clock.get_fps() * 0.1
            if self.type.startswith("shooter") and self.target != None:
                pos = (self.rect.centerx + self.velocity.x*10, self.rect.centery + self.velocity.y*10)
                newbullet = Bullet(self, pos, self.velocity, self.rotation)
                bulletgrp.add(newbullet)
            self.cooldown = self.attributes[0]
        if self.type.startswith("shooter"):
            if self.target == None:
                oldrect = self.rect
                self.rect = self.rangesurface
                self.rect.center = oldrect.center
                if pygame.sprite.spritecollide(self, enemygrp, False):
                    sprites = pygame.sprite.spritecollide(self, enemygrp, False)
                    if len(sprites) > 1:
                        spritedistances = []
                        for sprite in sprites:
                            print(abs((sprite.rect.centerx - self.rect.centerx)^2 + (sprite.rect.centery - self.rect.centery)^2))
                            distance = math.sqrt(abs((sprite.rect.centerx - self.rect.centerx)^2 + (sprite.rect.centery - self.rect.centery)^2))
                            spritedistances.append(distance)
                        shortest = min(spritedistances)
                        sidx = spritedistances.index(shortest)
                        self.target = sprites[sidx]
                    else:
                        self.target = sprites[0]
                self.rect = oldrect
            elif self.target != None:
                #print(self.target.rect.center)
                try:
                    self.rotation = math.atan(abs(self.target.rect.centery - self.rect.centery) / abs(self.target.rect.centerx - self.rect.centerx)) * 57.2958
                    self.rotation = math.round(self.rotation)
                except:
                    pass
                if (self.target.rect.centery < self.rect.centerx and self.target.rect.centery < self.rect.centery):
                    self.rotation = -self.rotation
                elif (self.target.rect.centerx > self.rect.centerx and self.target.rect.centery > self.rect.centery):
                    self.rotation = -self.rotation
                self.image = pygame.transform.rotate(self.originalimage, round(self.rotation))
                oldc = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = oldc

class Bullet(pygame.sprite.Sprite):
    def __init__(self, parent, position, velocity, rotation):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/bullet.png")
        self.originalimage = self.image
        self.rotation = rotation
        self.image = pygame.transform.rotate(self.originalimage, round(self.rotation) + 90)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position
        self.position = Vector2(self.rect.centerx, self.rect.centery)
        self.parent = parent
        self.attributes = bullets[self.parent.type]
        self.velocity = velocity
    def update(self, enemygrp):
        self.position += self.velocity
        self.rect.center = self.position.x, self.position.y
        if (self.rect.right < 0 or self.rect.left > 1280 or self.rect.top > 720 or self.rect.bottom < 0):
            self.kill()
        if pygame.sprite.spritecollide(self, enemygrp, False):
            sprite = pygame.sprite.spritecollide(self, enemygrp, False)[0]
            sprite.health -= self.attributes[0]
            if sprite.health <= 0:
                sprite.kill()
            self.kill()