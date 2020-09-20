import pygame

towers = {"shooter" : [1, 200, 50]}
#name - speed (actions/sec), range (pixels), hp

def GenerateMap():
    #just blank for now, maybe add presets later? 9.19.2020
    TileGroup = pygame.sprite.Group()
    TowerGroup = pygame.sprite.Group()

    for x in range(32):
        for y in range(18):
            NewTile = Tile([x*40, y*40], "regular")
            TileGroup.add(NewTile)
    TowerGroup.add(Tower([20, 60], "shooter"))

    return TileGroup, TowerGroup

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, type, occupied=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface([40, 40])
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.type = str(type)
        self.occupied = False
    def update(self):
        pass

class Tower(pygame.sprite.Sprite):
    def __init__(self, position, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface([35, 35])
        self.image.fill([0, 255, 0])
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = position
        self.type = str(type)
        self.attributes = towers[self.type]
        self.rotation = 0
    def update(self):
        pass
        #target, rotate, shoot, action cooldown

class Bullet(pygame.sprite.Sprite):
    def __init__(self, parent, position, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface([2, 10])
        self.image.fill([0, 255, 255])
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = position
        self.parent = parent