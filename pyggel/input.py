
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
        # probably not user events, since we have our own event system...

        # optimize our loop by throwing out events we do not need - especially mouse motion (unless used)
        accept = []
        if window:
            accept.extend(EVENT_MAPPINGS['window'])
        if keyboard:
            accept.extend(EVENT_MAPPINGS['keyboard'])
        if mouse:
            accept.extend(EVENT_MAPPINGS['mouse'])
        if mouse_motion:
            accept.extend(EVENT_MAPPINGS['mouse_motion'])

        # clear out what can be grabbed, then set with our limited list
        pygame.event.set_allowed(None)
        pygame.event.set_allowed(accept)

    def get_events(self):
        events = pygame.event.get()
        cur_mods = KeyboardModStatus()
        cur_mouse = MouseStatus()
        # TODO: attach current mouse position to these things

        for evt in events:
            if evt.type == QUIT or evt.type == ACTIVEEVENT:
                # Window events are responsible for picking name based on pygame event
                # since the rules are pretty branching
                yield WindowEvent(evt)
            if evt.type == KEYDOWN:
                yield KeyboardEvent('input.key.down', evt, cur_mods, cur_mouse)
            if evt.type == KEYUP:
                yield KeyboardEvent('input.key.up', evt, cur_mods, cur_mouse)
            if evt.type == MOUSEBUTTONDOWN:
                if evt.button in MouseScrollEvent.BUTTON_MAP:
                    yield MouseScrollEvent(evt, cur_mods, cur_mouse)
                else:
                    yield MouseButtonEvent('input.mouse.down', evt, cur_mods)
            if evt.type == MOUSEBUTTONUP:
                # scrolls generate up and down events, only need one
                if evt.button not in MouseScrollEvent.BUTTON_MAP:
                    yield MouseButtonEvent('input.mouse.up', evt, cur_mods)
            if evt.type == MOUSEMOTION:
                yield MouseMotionEvent(evt, cur_mods)

    def check(self):
        for evt in self.get_events():
            self._loop.dispatch(evt)


class InputBaseEvent(event.Event):
    def __init__(self, name, aliases=None, mods=None, mouse=None):
        super().__init__('input', name, aliases)

        if mods:
            self.mods = mods
        if mouse:
            self.mouse = mouse

    # override these methods, we'll manage them
    def qualify_name(self, name):
        return name

    def qualify_aliases(self, aliases):
        return aliases

class WindowEvent(InputBaseEvent):
    def __init__(self, pygame_event):
        name = 'input.window'
        if pygame_event.type == QUIT:
            aliases = ('input.window:close',)
            action = 'close'
        elif pygame_event.type == ACTIVEEVENT:
            state = pygame_event.state
            gain = pygame_event.gain

            if state == 1 and gain == 0:
                aliases = ('input.window:mouse_out',)
                action = 'mouse_out'
            elif state == 1 and gain == 1:
                aliases = ('input.window:mouse_in',)
                action = 'mouse_in'
            elif state == 2 and gain == 0:
                aliases = ('input.window:lost_focus',)
                action = 'lost_focus'
            elif state == 2 and gain == 1:
                # NOTE: I could never get this one to fire - since window.active seemed to handle it
                aliases = ('input.window:gained_focus',)
                action = 'gained_focus'
            elif state == 6 and gain == 0:
                # treat this as focus lost because effectively they are the same
                aliases = ('input.window:minimized','input.window:lost_focus')
                action = 'minimized'
            elif state == 6 and gain == 1:
                # treat this as focus gained as well, since they go hand-in-hand
                aliases = ('input.window:restored','input.window:gained_focus')
                action = 'restored'
        # TODO: handle resizes here too?

        super().__init__(name, aliases)
        self.raw = pygame_event
        self.action = action


class KeyboardEvent(InputBaseEvent):
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

    def __init__(self, name, pygame_event, mods, mouse):
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

        super().__init__(name, (name+':'+key,), mods, mouse)

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


class KeyboardModStatus:
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


class MouseStatus:
    def __init__(self):
        self.x, self.y = pygame.mouse.get_pos()

    @property
    def pos(self):
        return self.x, self.y


class MouseButtonEvent(InputBaseEvent):
    BUTTON_MAP = {
        1: 'left',
        2: 'middle',
        3: 'right'
    }

    def __init__(self, name, pygame_event, mods):
        button = self.button_name(pygame_event.button)
        super().__init__(name, (name+':'+button,), mods)

        self.raw = pygame_event
        self.button = button
        self.x, self.y = pygame_event.pos

    @property
    def pos(self):
        return self.x, self.y

    @staticmethod
    def button_name(button):
        if button in MouseButtonEvent.BUTTON_MAP:
            return MouseButtonEvent.BUTTON_MAP[button]
        else:
            return 'button_'+str(button) 


class MouseScrollEvent(InputBaseEvent):
    BUTTON_MAP = {
        4: 'up',
        5: 'down'
    }

    def __init__(self, pygame_event, mods):
        if pygame_event.button not in self.BUTTON_MAP:
            raise TypeError('Invalid input even')

        direction = self.BUTTON_MAP[pygame_event.button]
        name = 'input.mouse.scroll'
        super().__init__(name, (name+':'+direction,), mods)

        self.raw = pygame_event
        self.direction = direction
        self.value = -1 if direction == 'up' else 1
        self.x, self.y = pygame_event.pos

    @property
    def pos(self):
        return self.x, self.y


class MouseMotionEvent(InputBaseEvent):
    def __init__(self, pygame_event, mods):
        super().__init__('input.mouse.motion', None, mods)

        self.raw = pygame_event
        self.x, self.y = pygame_event.pos
        self.rel_x, self.rel_y = pygame_event.rel
        self.buttons = [MouseButtonEvent.button_name(button) for button in pygame_event.buttons]

    @property
    def pos(self):
        return self.x, self.y

    @property
    def rel(self):
        return self.rel_x, self.rel_y
