

class Handler:
    '''
        Maps event names to callback methods/handlers
        If subclassed, will automatically register any @register
            decorated methods
        NOTE: only one function can be registered for any given event
    '''
    def __init__(self, priority=0):
        self._priority = priority
        self._loop = None

        self._callbacks = {}
        self._check_for_registered()

    def _check_for_registered(self):
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if callable(prop) and hasattr(prop, 'pyggel_event_handler_registration'):
                for event_type in prop.pyggel_event_handler_registration:
                    self.register(event_type, prop)

    def _trigger_reindex_loop(self):
        # trigger loop to reindex which events we are tracking
        # this is to allow discarding events that nothing is watching for
        if self._loop:
            self._loop.reindex_events()

    @property
    def loop(self):
        return self._loop

    @property
    def priority(self):
        return self._priority

    def set_loop(self, loop):
        if self._loop:
            raise Exception('Handler already assigned to an event loop')

        self._loop = loop

    def handle_event(self, event):
        if event.has_alias:
            # check if we are handling an alias first (they are more specific)
            for alias in event.aliases:
                if alias in self._callbacks:
                    self._callbacks[alias](event)
                    return
        # event has no alias, or we are not handling the alias, check for event_name handler
        if event.name in self._callbacks:
            self._callbacks[event.name](event)

    def register(self, event_name, callback):
        if event_name in self._callbacks:
            raise TypeError('Callback already register for event "%s"'%event_name)

        self._callbacks[event_name] = callback
        self._trigger_reindex_loop()

    def deregister(self, event_name):
        if event_name in self._callbacks:
            del self._callbacks[event_name]
            self._trigger_reindex_loop()

    def get_registered(self):
        return tuple(self._callbacks)

    def tick(self, delta):
        pass


def register(event_name):
    def handle_decorator(func):
        if not hasattr(func, 'pyggel_event_handler_registration'):
            func.pyggel_event_handler_registration = []
        func.pyggel_event_handler_registration.append(event_name)
        return func
    return handle_decorator


# TODO: consider a handler/register that allow to specify
#       properties of events to match
# ie: @handler.register('window.key.pressed', key=['a', 'b'], mods=['shift', 'ctrl'])
# ref commit: 218a59aa56b00e1d41297374a688aeb36b772d2c
