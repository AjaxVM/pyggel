

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
                for event_name in prop.pyggel_event_handler_registration:
                    self.register(event_name, prop)

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
        if event.name in self._callbacks:
            self._callbacks[event.name](event)

    def register(self, event_name, callback):
        if event_name in self._callbacks:
            raise Exception(f'Event "{event_name}" already registered in Handler')

        self._callbacks[event_name] = callback

    def tick(self, delta):
        pass


def register(event_name):
    def handle_decorator(func):
        if not hasattr(func, 'pyggel_event_handler_registration'):
            func.pyggel_event_handler_registration = []
        func.pyggel_event_handler_registration.append(event_name)
        return func
    return handle_decorator
