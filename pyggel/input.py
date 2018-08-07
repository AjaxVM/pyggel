
import pygame
from pygame.locals import *

from .event import event, listener


# TODO: how to wrap pygame.event.set_grab, hiding mouse or keeping it centered?


EVENT_MAPPINGS = {
    'window': (QUIT, ACTIVEEVENT),
    'window_resize': (VIDEORESIZE,),
    'keyboard': (KEYDOWN, KEYUP),
    'mouse': (MOUSEBUTTONDOWN, MOUSEBUTTONUP),
    'mouse_motion': (MOUSEMOTION,),
    'joystick': (JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP),
}
# we do not use the following pygame events at this time:
# USEREVENT - since we have our own event systm
# VIDEOEXPOSE - since we are always redrawing the entire screen


class InputListener(listener.Listener):
    '''
        Listener for events in game window (such as window events (like quit/minimize), keyboard, etc.)

        If not using the pyggel event loop, "get_events" returns an iterator for manual processing
    '''
    def __init__(self,
                 window=True,
                 keyboard=True,
                 mouse=True,
                 mouse_motion=False):
        super().__init__()

        # TODO: support joy stick and user events?

        # optimize our loop by throwing out events we do not need - especially mouse motion (unless used)
        accept = []
        if window:
            accept.extend(EVENT_MAPPINGS['window'])
        if keyboard:
            accept.extend(EVENT_MAPPINGS['keyboard'])
        if mouse:
            accept.extend(EVENT_MAPPINGS['mouse'])
        if mouse_motion:
            accept.extend(EVENT_MAPPINGS['mousemotion'])

        pygame.event.set_allowed(accept)

    def get_events(self):
        events = pygame.event.get()
        cur_mods = KeyboardMods()

        for evt in events:
            if evt.type == QUIT or evt.type == ACTIVEEVENT:
                # Window events are responsible for picking name based on pygame event
                # since the rules are pretty branching
                yield WindowEvent(evt)
            if evt.type == KEYDOWN:
                yield KeyboardEvent('input.key.down', evt, cur_mods)
            if evt.type == KEYUP:
                yield KeyboardEvent('input.key.up', evt, cur_mods)
            if evt.type == MOUSEBUTTONDOWN:
                if evt.button in MouseScrollEvent.BUTTON_MAP:
                    yield MouseScrollEvent('input.mouse.scroll', evt, cur_mods)
                else:
                    yield MouseButtonEvent('input.mouse.down', evt, cur_mods)
            if evt.type == MOUSEBUTTONUP:
                # scrolls generate up and down events, only need one
                if evt.button not in MouseScrollEvent.BUTTON_MAP:
                    yield MouseButtonEvent('input.mouse.up', evt, cur_mods)

    def dispatch(self, evt):
        self._loop.dispatch(evt)

    def check(self):
        for evt in self.get_events():
            self.dispatch(evt)


class WindowEvent(event.Event):
    def __init__(self, pygame_event):
        name = 'window'
        if pygame_event.type == QUIT:
            aliases = ('window:close',)
            action = 'close'
        elif pygame_event.type == ACTIVEEVENT:
            state = pygame_event.state
            gain = pygame_event.gain

            if state == 1 and gain == 0:
                aliases = ('window:mouse_out',)
                action = 'mouse_out'
            elif state == 1 and gain == 1:
                aliases = ('window:mouse_in',)
                action = 'mouse_in'
            elif state == 2 and gain == 0:
                aliases = ('window:lost_focus',)
                action = 'lost_focus'
            elif state == 2 and gain == 1:
                # NOTE: I could never get this one to fire - since window.active seemed to handle it
                aliases = ('window:gained_focus',)
                action = 'gained_focus'
            elif state == 6 and gain == 0:
                # treat this as focus lost because effectively they are the same
                aliases = ('window:minimized','window:lost_focus')
                action = 'minimized'
            elif state == 6 and gain == 1:
                # treat this as focus gained as well, since they go hand-in-hand
                aliases = ('window:restored','window:focus.gained')
                action = 'restored'
        # TODO: handle resizes here too?

        super().__init__(name, aliases)
        self.raw = pygame_event
        self.action = action


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

    def __init__(self, name, pygame_event, mods):
        if pygame_event.type == KEYDOWN:
            char = pygame_event.unicode
            if not pygame_event.type in self.MAPPED_CHARS:
                self.MAPPED_CHARS[pygame_event.type] = char
        else:
            # handle edge case where we get a keyup before a keydown
            if pygame_event.type in self.MAPPED_CHARS:
                char = self.MAPPED_CHARS[pygame_event.type]
            else:
                char = None

        key = self.get_mapped_name(pygame_event)

        # init, with alias
        # todo: maybe support input mapping (ie: key.a -> move_left) with alias?
        super().__init__(name, (name+':'+key,))

        self.raw = pygame_event
        self.key = key
        self.mods = mods

        self.char = char
        self.is_whitespace = char in self.WHITESPACE_CHARACTERS
        self.is_control_char = char in self.CONTROL_CHARACTERS

    @staticmethod
    def get_mapped_name(pygame_event):
        if pygame_event.key not in KeyboardEvent.MAPPED_EVENTS:
            KeyboardEvent.MAPPED_EVENTS[pygame_event.key] = pygame.key.name(pygame_event.key).replace(' ', '_')

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


class MouseButtonEvent(event.Event):
    BUTTON_MAP = {
        1: 'left',
        2: 'middle',
        3: 'right'
    }

    def __init__(self, name, pygame_event, mods):
        if pygame_event.button in self.BUTTON_MAP:
            button = self.BUTTON_MAP[pygame_event.button]
        else:
            button = 'button_'+str(pygame_event.button)
        super().__init__(name, (name+':'+button,))

        self.raw = pygame_event
        self.button = button
        self.mods = mods
        self.x, self.y = pygame_event.pos


class MouseScrollEvent(event.Event):
    BUTTON_MAP = {
        4: 'up',
        5: 'down'
    }

    def __init__(self, name, pygame_event, mods):
        if pygame_event.button not in self.BUTTON_MAP:
            raise TypeError('Invalid input even')

        direction = self.BUTTON_MAP[pygame_event.button]
        super().__init__(name, (name+':'+direction,))

        self.raw = pygame_event
        self.direction = direction
        self.value = -1 if direction == 'up' else 1
        self.mods = mods
        self.x, self.y = pygame_event.pos

