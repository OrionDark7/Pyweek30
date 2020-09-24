import pygame
from pygame.color import THECOLORS

pygame.init()
pygame.font.init()

size = 18
color = THECOLORS["white"]
font = pygame.font.Font("./assets/font/8-bit-pusab.ttf", size)

def text(txt, position, surface, centered=False):
    render = font.render(str(txt), 1, color)
    change = render.get_rect().width/2
    if centered:
        surface.blit(render, [position[0] - change, position[1]])
    else:
        surface.blit(render, position)