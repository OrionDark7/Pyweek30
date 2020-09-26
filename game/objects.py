import pygame, math, random
from pygame.math import Vector2
from game import ui

pygame.init()
pygame.mixer.init()

towers = {"shooter" : [500, 600, 50],
          "shooter_rapid" : [150, 300, 40],
          "shooter_sniper" : [1250, 850, 45],
          "base" : [0, 0, 500],
          "wall" : [0, 0, 100],
          "healer" : [5000, 190, 50],
          "fxf_slowness" : [2500, 280, 200]}
bullets = {"shooter" : [10], "shooter_rapid" : [5], "shooter_sniper" : [20], "enemy":[5], "enemyflying":[7],  "enemyshooter":[5], "enemyshooterflying":[7], "enemyfxf":[6], "enemyfxfflying":[8]}
sfxnames = ["basehit", "build", "enemyshoot", "playershoot", "select"]
sfx = {}
for name in sfxnames:
    sfx[name] = pygame.mixer.Sound("./assets/sfx/"+str(name)+".wav")
#name - speed (ms/action), range (pixels), hp
#name - damage

def heffect(position, cooldown, effectgrp, color=[255, 255, 255]):
    effectgrp.add(ui.heffect(position, cooldown, color))

def effect(position, text, speed, cooldown, effectgrp, color=[255, 255, 255]):
    prevsize = ui.size
    ui.fontsize(10)
    effectgrp.add(ui.effect(position, text, speed, cooldown, color))
    ui.fontsize(prevsize)

def GenerateMap():
    #just blank for now, maybe add presets later? 9.19.2020
    TileGroup = pygame.sprite.Group()
    TowerGroup = pygame.sprite.Group()
    FieldGroup = pygame.sprite.Group()
    listmap = []
    metadata = {}
    base = None

    for x in range(32):
        listmap.append([])
        for y in range(18):
            listmap[x].append(0)
            if [x,y] == [31,8] or [x,y] == [31,9]:
                NewTile = Tile([x * 40, y * 40], "enemyspawn")
                listmap[x][y] = -1
            else:
                NewTile = Tile([x*40, y*40], "tile")
            TileGroup.add(NewTile)
    base = Tower([40, 360], "base", [0, 9], FieldGroup)
    TowerGroup.add(base)
    metadata["base"] = [0, 9]
    listmap[0][8] = -2
    listmap[0][9] = -2
    listmap[1][8] = -2
    listmap[1][9] = -2
    #TowerGroup.add(Tower([20, 420], "shooter",  [0, 11], FieldGroup))
    #listmap[0][11] = 1
    #TowerGroup.add(Tower([20, 300], "shooter", [0, 8], FieldGroup))
    #listmap[0][8] = 1
    return TileGroup, TowerGroup, listmap, metadata, base

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, type, occupied=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/tiles/"+str(type)+".png")
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.type = str(type)
        self.gpos = [self.rect.left/40, self.rect.top/40]
        self.occupied = False

class EffectField(pygame.sprite.Sprite):
    def __init__(self, type, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/fields/"+type+".png")
        self.originalimage = self.image
        self.attributes = towers[type]
        self.originalimage = pygame.transform.scale(self.originalimage, [280, 280])
        self.originalimage.set_alpha(128)
        self.rotation = 0
        self.mask = pygame.mask.from_surface(self.originalimage)
        self.rect = self.image.get_rect()
        self.diameter = self.rect.width
        self.rect.center = position
        self.type = str(type)
        self.scale = -2
        self.goingup = True
    def update(self, highlight, towergrp):
        if self.rotation == 360:
            self.rotation = 0
        else:
            self.rotation += 1
        if self.goingup and self.scale < 2:
            self.scale += 2
        elif self.goingup and self.scale == 2:
            self.goingup = False
        elif not self.goingup and self.scale > -2:
            self.scale -= 2
        elif not self.goingup and self.scale == 2:
            self.goingup = True
        self.image = pygame.transform.scale(self.originalimage, (self.diameter + self.scale, self.diameter + self.scale))
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.attributes = towers[self.type]
        oldc = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = oldc
        oldc2 = highlight.rect.center
        highlight.rect.center = self.rect.center
        if highlight.gettower(towergrp) == None:
            self.kill()
        highlight.rect.center = oldc2
    def check(self, sprites):
        for s in sprites:
            s.mask = pygame.mask.from_surface(s.image)
            if pygame.sprite.collide_mask(self, s):
                if self.type == "fxf_slowness":
                    s.speed = s.attributes[2] * 0.5
                    s.fxcooldown = self.attributes[0]
                    s.effect = "slowness"

class Tower(pygame.sprite.Sprite):
    def __init__(self, position, type, gamepos, fieldgrp):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("./assets/graphics/towers/"+type+".png")
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
        self.health = self.attributes[2]
        self.maxhealth = self.health
        self.attachedfield = None
        self.rotated = 0
        if self.type.startswith("shooter") or self.type.startswith("fxf") or self.type.startswith("healer"):
            self.rangesurface = pygame.surface.Surface([self.attributes[1], self.attributes[1]])
            self.rangesurface = self.rangesurface.get_rect()
        if self.type.startswith("fxf"):
            self.attachedfield = EffectField(self.type, self.rect.center)
            fieldgrp.add(self.attachedfield)
    def heal(self, rate):
        if not self.type == "base":
            self.health+=rate
            if self.health > self.maxhealth:
                self.health = self.maxhealth
    def update(self, bulletgrp, enemygrp, towergrp, effectgrp, clock):
        self.cooldown -= clock.get_time()
        if self.target != None:
            if not self.target.alive():
                self.target = None
            elif not self.rangesurface.colliderect(self.target.rect):
                self.target = None
        if self.cooldown <= 0:
            if self.target != None:
                self.velocity = Vector2(self.target.rect.centerx - self.rect.centerx, self.target.rect.centery - self.rect.centery).normalize() * clock.get_fps() * 0.1
            if self.type.startswith("shooter") and self.target != None:
                pos = (self.rect.centerx + self.velocity.x*10, self.rect.centery + self.velocity.y*10)
                newbullet = Bullet(self, pos, self.velocity, self.rotation)
                bulletgrp.add(newbullet)
                sfx["playershoot"].play()
            elif self.type.startswith("healer"):
                oldrect = self.rect
                self.rect = self.rangesurface
                self.rect.center = oldrect.center
                if pygame.sprite.spritecollide(self, towergrp, False):
                    sprites = pygame.sprite.spritecollide(self, towergrp, False)
                    for s in sprites:
                        s.heal(2)
                        if not s.type == "base":
                            heffect(s.rect.center, 500, effectgrp, [85, 209, 72])
                self.rect = oldrect
            self.cooldown = self.attributes[0]
        if self.type.startswith("fxf"):
            self.attachedfield.rect.center = self.rect.center
            oldrect = self.rect
            self.rect = self.rangesurface
            self.rect.center = oldrect.center
            if pygame.sprite.spritecollide(self, enemygrp, False):
                sprites = pygame.sprite.spritecollide(self, enemygrp, False)
                self.attachedfield.check(sprites)
            self.rect = oldrect
        elif self.type.startswith("shooter"):
            if self.target == None:
                oldrect = self.rect
                self.rect = self.rangesurface
                self.rect.center = oldrect.center
                if pygame.sprite.spritecollide(self, enemygrp, False):
                    sprites = pygame.sprite.spritecollide(self, enemygrp, False)
                    if len(sprites) > 1:
                        spritedistances = []
                        for sprite in sprites:
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
                self.originalrotation = self.rotation
                if (self.target.rect.centerx < self.rect.centerx and self.target.rect.centery < self.rect.centery):
                    self.rotation = -self.originalrotation
                if (self.target.rect.centerx < self.rect.centerx and self.target.rect.centery < self.rect.centery):
                    self.rotation = -self.originalrotation+180
                if (self.target.rect.centerx < self.rect.centerx and self.target.rect.centery > self.rect.centery):
                    self.rotation = self.originalrotation+180
                if (self.target.rect.centerx > self.rect.centerx and self.target.rect.centery > self.rect.centery):
                    self.rotation = -self.originalrotation
                if self.rotated != self.rotation:
                    if self.rotated < self.rotation:
                        self.rotated += 1
                    if self.rotated > self.rotation:
                        self.rotated -= 1
                self.image = pygame.transform.rotate(self.originalimage, round(self.rotation))
                oldc = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = oldc

class Bullet(pygame.sprite.Sprite):
    def __init__(self, parent, position, velocity, rotation):
        pygame.sprite.Sprite.__init__(self)
        if parent.type.startswith("enemy"):
            self.image = pygame.image.load("./assets/graphics/enemybullet.png")
        else:
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
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, enemygrp, towergrp, effectgrp, data):
        self.position += self.velocity
        self.rect.center = self.position.x, self.position.y
        if not self.parent.type.startswith("enemy"):
            if not self.rect.colliderect(self.parent.rangesurface):
                self.kill()
        if (self.rect.right < 0 or self.rect.left > 1280 or self.rect.top > 720 or self.rect.bottom < 0):
            self.kill()
        if self.parent.type.startswith("enemy"):
            if pygame.sprite.spritecollide(self, towergrp, False):
                sprite = pygame.sprite.spritecollide(self, towergrp, False)[0]
                sprite.mask = pygame.mask.from_surface(sprite.image)
                if pygame.sprite.collide_mask(self, sprite):
                    sprite.health -= self.attributes[0]
                    if sprite.type == "base":
                        sfx["basehit"].play()
                    if sprite.health <= 0:
                        sprite.kill()
                        heffect(sprite.rect.center, 500, effectgrp, [255, 0, 0])
                    else:
                        heffect(sprite.rect.center, 250, effectgrp, [255, 128, 0])
                    self.kill()
        else:
            if pygame.sprite.spritecollide(self, enemygrp, False):
                sprite = pygame.sprite.spritecollide(self, enemygrp, False)[0]
                sprite.mask = pygame.mask.from_surface(sprite.image)
                if pygame.sprite.collide_mask(self, sprite):
                    sprite.health -= self.attributes[0]
                    if sprite.health <= 0:
                        cash = int(round(sprite.attributes[1] / random.randint(9, 11)))
                        effect(sprite.rect.center, "+" + str(cash) + "B", -0.05, 500, effectgrp, [85, 209, 72])
                        data.addmoney += cash
                    self.kill()