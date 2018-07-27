
import inspect


class Handler:
    def __init__(self):
        self.loop = None

        self._callbacks = {}

        self._check_for_callback_methods()

    def _check_for_callback_methods(self):
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if callable(prop) and hasattr(prop, 'pyggel_event_handler'):
                for event_type in prop.pyggel_event_handler:
                    self.register(event_type, prop)

    def start(self):
        pass

    def stop(self):
        pass

    def tick(self):
        # called every time we loop
        pass

    def handle(self, event):
        # called for each event, check if any callbacks exist for this func        
        if event.type in self._callbacks:
            for caller in self._callbacks[event.type]:
                caller.call(event, self.loop)

    def register(self, event_type, func):
        if not event_type in self._callbacks:
            self._callbacks[event_type] = []

        self._callbacks[event_type].append(HandlerCaller(func))


class HandlerCaller:
    def __init__(self, func):
        self.func = func

        _def = inspect.getargspec(func)

        args = [i for i in _def.args if not i == 'self']

        self.param_count = 0

        if len(args) > 2:
            raise TypeError('Invalid handler function')
        elif _def.varargs or len(args) == 2:
            self.param_count = 2
        elif len(args) == 1:
            self.param_count = 1

    def call(self, *args):
        self.func(*args[:self.param_count])


def register(event_name):
    def handle_decorator(func):
        if not hasattr(func, 'pyggel_event_handler'):
            func.pyggel_event_handler = []

        func.pyggel_event_handler.append(event_name)
        return func
    return handle_decorator
