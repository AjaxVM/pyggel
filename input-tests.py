
import string

import pygame
# from pygame.locals import *

from pyggel.event import handler, loop
from pyggel.input import InputListener

class MyHandler(handler.Handler):
    def __init__(self, screen):
        super().__init__()

        self.screen = screen

    def tick(self, delta):
        # pygame.display.set_caption('%s'%delta)
        pygame.display.flip()

    # @handler.register('input.key.down')
    # @handler.register('input.key.up')
    # def handle_key(self, event):
    #     print({
    #         'name': event.name,
    #         'key': event.key,
    #         'char': event.char,
    #         'whitespace': event.is_whitespace,
    #         'control': event.is_control_char,
    #         'mod_shift': event.mods.shift,
    #         'mod_ctrl': event.mods.ctrl,
    #         'mod_alt': event.mods.alt
    #     })

    # @handler.register('input.mouse.down')
    # @handler.register('input.mouse.up')
    # def handle_mouse(self, event):
    #     print({
    #         'name': event.name,
    #         'button': event.button,
    #         'mod_shift': event.mods.shift,
    #         'mod_ctrl': event.mods.ctrl,
    #         'mod_alt': event.mods.alt
    #     })

    # @handler.register('input.mouse.scroll')
    # def handle_scroll(self, event):
    #     print({
    #         'name': event.name,
    #         'direction': event.direction,
    #         'scroll_value': event.value,
    #         'mod_shift': event.mods.shift,
    #         'mod_ctrl': event.mods.ctrl,
    #         'mod_alt': event.mods.alt
    #     })

    @handler.register('input.window:close')
    @handler.register('input.key.down:escape')
    def handle_quit(self, event):
        self.loop.stop()

    @handler.register('input.window')
    def handle_window(self, event):
        print('window', event.action)

    @handler.register('input.key.down')
    def test(self, event):
        print('test', event.key, event.mouse.pos)

    @handler.register('input.mouse.motion')
    def handle_any_input(self, event):
        # print('hola', event.x, event.y, event.rel_x, event.rel_y)
        pass


def main():

    pygame.init()

    # pygame.event.set_grab(True)

    screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)

    my_loop = loop.Loop()

    hand = MyHandler(screen)

    my_loop.add_handler(hand)
    my_loop.add_listener(InputListener(mouse_motion=True))

    my_loop.start()

    pygame.quit()

main()


# TODO: maybe something like following for "hard-aliases"
# this would only work for key/mouse up/down though

# from pyggel.event import handler, event


# class Handler(handler.Handler):

#     @handler.register('window.key.pressed')
#     def test1(self, event):
#         print('test1', event.name, event.key, event.mods)

# # listener.map('key_forward', 'a')
# # listener.map('key_forward', 'window.key.pressed', key='a', mods=('ctrl', 'shift'))

# # listener.add_mappings([
# #     {
# #         'name': 'window.key.pressed',
# #         'key': 'w',
# #         'mods': ['shift'],
# #         'rename': 'run_forward'
# #     },
# #     {
# #         'name': 'window.key.pressed',
# #         'key': 'w',
# #         'mods': [],
# #         'rename': 'walk_forward'
# #     }
# # ])

# hand = Handler()
# hand.handle_event(event.KWEvent('window.key.pressed', key='c', mods=['shift']))
# hand.handle_event(event.KWEvent('window.key.pressed', key='a', mods=['shift']))
# hand.handle_event(event.KWEvent('window.key.pressed', key='b', mods=['shift', 'ctrl']))
