import pygame
from pygame.color import THECOLORS

pygame.init()
pygame.font.init()
pygame.mixer.init()

size = 18
color = THECOLORS["white"]
hicolor = THECOLORS["white"]
font = pygame.font.Font("./assets/font/8-bit-pusab.ttf", size)

def fontsize(newsize):
    global size, font
    size = int(newsize)
    font = pygame.font.Font("./assets/font/8-bit-pusab.ttf", size)

def text(txt, position, surface, centered=False):
    render = font.render(str(txt), 1, color)
    change = render.get_rect().width/2
    if centered:
        surface.blit(render, [position[0] - change, position[1]])
    else:
        surface.blit(render, position)

class effect(pygame.sprite.Sprite):
    def __init__(self, position, text, speed, cooldown, color=[255, 255, 255]): #cooldown is in ms
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(str(text), 1, color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.alpha = 255
        self.cooldown = int(cooldown)
        self.max = self.cooldown
        self.speed = speed
    def update(self, clock):
        self.cooldown -= clock.get_time()
        self.alpha = round((self.cooldown/self.max)*255)
        self.image.set_alpha(self.alpha)
        self.rect.centery += clock.get_fps() * self.speed
        if self.cooldown <= 0:
            self.kill()

class heffect(pygame.sprite.Sprite):
    def __init__(self, position, cooldown, color=[255, 255, 255]): #cooldown is in ms
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface([40, 40])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.alpha = 240
        self.cooldown = int(cooldown)
        self.max = self.cooldown
        self.position = position
    def update(self, clock):
        self.cooldown -= clock.get_time()
        self.alpha = round((self.cooldown/self.max)*240)
        self.image.set_alpha(self.alpha)
        try:
            self.image = pygame.transform.scale(self.image, [round((self.cooldown/self.max)*40), round((self.cooldown/self.max)*40)])
        except:
            self.kill()
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        if self.cooldown <= 0:
            self.kill()

class button(pygame.sprite.Sprite):
    def __init__(self, text, position, bcolor=None, hcolor=None, centered=False):
        pygame.sprite.Sprite.__init__(self)
        if bcolor == None:
            bcolor = color
        if hcolor == None:
            hcolor = hicolor
        self.image = font.render(str(text), 1, bcolor)
        self.nimage = self.image
        self.himage = font.render(str(text), 1, hcolor)
        self.originalrect = self.image.get_rect()
        self.backborder = pygame.surface.Surface([self.originalrect.width + 16, self.originalrect.height + 16])
        self.backborder.set_alpha(128)
        self.image = self.backborder
        self.rect = self.image.get_rect()
        self.image.blit(self.nimage, [(self.rect.width-self.originalrect.width)/2, (self.rect.height-self.originalrect.height)/2])
        self.image1 = pygame.surface.Surface([self.rect.width, self.rect.height])
        self.image1.fill([0, 0, 0, 0])
        self.image1.blit(self.backborder, [0, 0])
        self.image1.blit(self.himage, [(self.rect.width - self.originalrect.width) / 2,
                                      (self.rect.height - self.originalrect.height) / 2])
        self.image2 = pygame.surface.Surface([self.rect.width, self.rect.height])
        self.image2.fill([0, 0, 0, 0])
        self.image2.blit(self.backborder, [0, 0])
        self.image2.blit(self.nimage, [(self.rect.width - self.originalrect.width) / 2,
                                       (self.rect.height - self.originalrect.height) / 2])
        if centered:
            self.rect.center = position
        else:
            self.rect.topleft = position
        self.clicked = False
        self.hovered = False
        self.position = position
        self.centered = centered
    def click(self, mouse):
        self.clicked = False
        if self.rect.collidepoint(mouse.rect.topleft):
            self.clicked = True
        return self.clicked
    def update(self, mouse):
        self.hovered = False
        self.rect = self.image.get_rect()
        if self.centered:
            self.rect.center = self.position
        else:
            self.rect.topleft = self.position
        if self.rect.collidepoint(mouse.rect.topleft):
            self.hovered = True
        if self.hovered:
            self.image = self.image1
            self.image.set_alpha(255)
        else:
            self.image = self.image2
            self.image.set_alpha(128)
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)