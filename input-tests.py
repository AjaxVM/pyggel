
import string

import pygame
# from pygame.locals import *

from pyggel.event import handler, loop
from pyggel.input import WindowListener

class MyHandler(handler.Handler):
    def __init__(self, screen):
        super().__init__()

        self.screen = screen

    def tick(self, delta):
        pygame.display.set_caption('%s'%delta)
        pygame.display.flip()

    @handler.register('window.key.down')
    @handler.register('window.key.up')
    def handle_key_down(self, event):
        print({
            'name': event.name,
            'key': event.key,
            'char': event.char,
            'whitespace': event.is_whitespace,
            'control': event.is_control_char,
            'mod_shift': event.mods.shift,
            'mod_ctrl': event.mods.ctrl,
            'mod_alt': event.mods.alt
        })

    @handler.register('window.quit')
    def handle_quit(self, event):
        pygame.quit()
        self.loop.stop()


def main():

    pygame.init()

    screen = pygame.display.set_mode((640, 480))

    my_loop = loop.Loop()

    my_loop.add_handler(MyHandler(screen))
    my_loop.add_listener(WindowListener())

    my_loop.start()

main()


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
