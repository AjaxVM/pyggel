
import pygame
from pygame.locals import *

from .event import event, listener


class WindowListener(listener.Listener):
    def dispatch(self, evt):
        self._loop.dispatch(evt)

    def check(self):
        # todo, only window events
        # have a keyboard listener for other events
        # and a mouse handler for those
        # etc.
        # can use pygame.event.get(QUIT,ACTIVEEVENT,VIDEORESIZE,VIDEOEXPOSE)
        # need to figure out how to clear the event queue (so it does not fill)
        # after all inputs are read... maybe as an event?
        # the reason for this is for not needing to iterate through all events if we don't need to
        # just dumping ones we don't care about
        events = pygame.event.get()
        cur_mods = KeyboardMods()

        for evt in events:
            if evt.type == QUIT:
                self.dispatch(WindowEvent('window.quit', evt))
            if evt.type == KEYDOWN or evt.type == KEYUP:
                self.dispatch(KeyboardEvent(evt, cur_mods))
            if evt.type == MOUSEMOTION:
                # todo
                pass
            if evt.type == MOUSEBUTTONDOWN


class WindowEvent(event.Event):
    def __init__(self, name, raw):
        super().__init__(name)
        self.raw = raw


class KeyboardEvent(event.Event):
    MAPPED_EVENTS = {}
    MAPPED_CHARS = {} # keyup events don't have unicode from pygame, so map here from the keydowns

    CONTROL_CHARACTERS = [
        '\b', # backspace
        '\t', # tab
        '\r', # return/enter
        '\x1b' # escape
    ]
    WHITESPACE_CHARACTERS = [
        '\t', # tab
        ' ', # space
    ]

    def __init__(self, pygame_event, mods):
        if pygame_event.type == KEYDOWN:
            super().__init__('window.key.down')
            char = pygame_event.unicode
            if not pygame_event.type in self.MAPPED_CHARS:
                self.MAPPED_CHARS[pygame_event.type] = char
        else:
            super().__init__('window.key.up')
            # handle edge case where we get a key up before a keydown
            if pygame_event.type in self.MAPPED_CHARS:
                char = self.MAPPED_CHARS[pygame_event.type]
            else:
                char = None
        self.raw = pygame_event
        self.mods = mods

        self.key = self.get_mapped_name(pygame_event)
        self.char = char
        self.is_whitespace = char in self.WHITESPACE_CHARACTERS
        self.is_control_char = char in self.CONTROL_CHARACTERS

    @staticmethod
    def get_mapped_name(pygame_event):
        if pygame_event.key not in KeyboardEvent.MAPPED_EVENTS:
            KeyboardEvent.MAPPED_EVENTS[pygame_event.key] = 'key.%s'%pygame.key.name(pygame_event.key).replace(' ', '_')

        return KeyboardEvent.MAPPED_EVENTS[pygame_event.key]


class KeyboardMods:
    def __init__(self):
        self._mods = pygame.key.get_mods()

    @property
    def shift(self):
        return bool(self._mods & KMOD_SHIFT)

    @property
    def lshift(self):
        return bool(self._mods & KMOD_LSHIFT)

    @property
    def rshift(self):
        return bool(self._mods & KMOD_RSHIFT)

    @property
    def ctrl(self):
        return bool(self._mods & KMOD_CTRL)
    
    @property
    def lctrl(self):
        return bool(self._mods & KMOD_LCTRL)

    @property
    def rctrl(self):
        return bool(self._mods & KMOD_RCTRL)
    
    @property
    def alt(self):
        return bool(self._mods & KMOD_LALT)

    @property
    def lalt(self):
        return bool(self._mods & KMOD_ALT)

    @property
    def ralt(self):
        return bool(self._mods & KMOD_RALT)
    
    @property
    def meta(self):
        return bool(self._mods & KMOD_META)

    @property
    def lmeta(self):
        return bool(self._mods & KMOD_LMETA)

    @property
    def rmeta(self):
        return bool(self._mods & KMOD_RMETA)
    
    @property
    def caps(self):
        return bool(self._mods & KMOD_CAPS)
    
    @property
    def num(self):
        return bool(self._mods & KMOD_NUM)

    @property
    def mode(self):
        return bool(self._mods & KMOD_MODE)

