import pygame
import pygame.freetype
from pygame.locals import *

class CharWise(object):
    def __init__(self, font, text, target):
        self.font = font
        self.text = text
        self.target = target

    def render_pygame(self, pos, color=(255,255,255)):
        self.target.blit(self.font.render(self.text, True, color), pos)

    def render_1(self, pos, color=(255,255,255), marker_color=(255,0,0)):
        indent = 0

        for char in self.text:
            glyph = self.font.render(char, True, color)
            metrics = self.font.metrics(char)[0]

            self.target.blit(glyph, (pos[0]+indent, pos[1]))
            # pygame.draw.line(self.target, marker_color, (pos[0]+indent, 0), (pos[0]+indent, pos[1]+10))
            pygame.draw.rect(self.target, marker_color, pygame.Rect(pos[0]+indent, pos[1]+metrics[2], metrics[1], metrics[3]), 1)
            indent += metrics[0] + metrics[4]

class CharWiseF(object):
    def __init__(self, font, text, target):
        self.font = font
        self.text = text
        self.target = target

    def render_pygame(self, pos, color=(255,255,255)):
        self.target.blit(self.font.render(self.text, color)[0], pos)

    def render_1(self, pos, color=(255,255,255), marker_color=(255,0,0)):
        indent = 0

        for char in self.text:
            glyph = self.font.render(char, color)[0]
            rect = self.font.get_rect(char)
            metrics = self.font.get_metrics(char)[0]
            # self.target.blit(glyph, (pos[0]+indent, pos[1]-metrics[3]))
            # # pygame.draw.line(self.target, marker_color, (pos[0]+indent, pos[1]+metrics[3]), (pos[0]+indent, pos[1]+metrics[3]))
            # # pygame.draw.rect(self.target, marker_color, pygame.Rect(pos[0]+indent, pos[1]+metrics[2], metrics[1], metrics[3]), 1)
            # pygame.draw.rect(self.target, marker_color, pygame.Rect(pos[0]+indent, pos[1]+metrics[2], rect.width, rect.height), 1)
            # indent += rect.width

            origin = pos[0] + indent, pos[1]
            bearing = rect.x, rect.y
            xMin, xMax = metrics[0:2]
            yMin, yMax = metrics[2:4]
            advance = metrics[4]

            print(advance)

            render_rect = pygame.Rect(origin[0] + (bearing[0] if indent else 0), origin[1] - bearing[1] + self.font.get_sized_ascender(), xMax-xMin, yMax - yMin)
            self.target.blit(glyph, render_rect)
            # pygame.draw.rect(self.target, marker_color, render_rect, 1)
            pygame.draw.line(self.target, marker_color, pos, (pos[0]+250, pos[1]))
            indent += advance - (bearing[0] if not indent else 0)

def main():
    pygame.init()

    screen = pygame.display.set_mode((640, 480))

    font = pygame.font.Font(None, 32)
    font2 = pygame.freetype.Font(None, 32)

    cw = CharWise(font, 'Hello Worldgy', screen)
    cwf = CharWiseF(font2, 'Hello Worldgy', screen)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        screen.fill((0,0,0))

        cw.render_pygame((0,0))
        cw.render_1((0, 30))

        cwf.render_pygame((250, 0))
        cwf.render_1((250, 50))

        # text = font.render('Hello Worldgy', True, (255,255,255))
        # screen.blit(text, (0,0))

        # text = font2.render('Hello Worldgy', (255,255,255))[0]
        # screen.blit(text, (250,0))

        # indent = 0
        # indent2 = 0
        # for char in 'Hello Worldgy':
        #     metrics = font.metrics(char)
        #     text = font.render(char, True, (255,255,255))
        #     # print(char, metrics, text.get_size())
        #     if indent:
        #         indent += metrics[0][0]
        #     screen.blit(text, (indent, 100))
        #     # indent += text.get_width() + metrics[0][0] # min offset
        #     pygame.draw.line(screen, (255,0,0), (indent, 0), (indent, 200))
        #     indent += metrics[0][4]

        #     metrics = font2.get_metrics(char)
        #     rect = font2.get_rect(char)
        #     print(char, rect, metrics)
        #     text = font2.render(char, (255,255,255))[0]
        #     screen.blit(text, (indent2+250, -metrics[0][3]+100))
        #     pygame.draw.line(screen, (255,0,0), (indent2+250, 0), (indent2+250, 200))
        #     indent2 += rect.width

        pygame.display.flip()
        # return

main()
