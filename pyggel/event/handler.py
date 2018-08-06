
from collections import abc


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
                for event_name, params in prop.pyggel_event_handler_registration:
                    self.register(event_name, prop, **params)

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
            for cb in self._callbacks[event.name]:
                cb.call(event)

    def register(self, event_name, callback, **kwargs):
        if event_name not in self._callbacks:
            self._callbacks[event_name] = []

        self._callbacks[event_name].append(CallbackRegistration(callback, kwargs))

    def deregister(self, event_name, callback=None):
        # if callback is not None, will remove callback from event_name
        # if callback is None, will remove all callbacks for event_name

        if event_name in self._callbacks:
            if callback:
                for cb in self._callbacks[event_name]:
                    if cb.func == callback:
                        self._callbacks[event_name].remove(cb)
            else:
                del self._callbacks[event_name]

    def tick(self, delta):
        pass


class CallbackRegistration:
    def __init__(self, func, params):
        self.func = func
        self.params = None
        self.build_params(params)

    def build_params(self, params):
        if not params:
            return

        self.params = []
        for param in params:
            self.params.append(CallbackParam(param, params[param]))
        return self.params

    def call(self, event):
        if self.params:
            for param in self.params:
                if not param.check(event):
                    return

        self.func(event)


class CallbackParam:
    def __init__(self, prop, value):
        self.prop = prop
        self.values = []
        self.parse_value(value)

    def is_array(self, val):
        return isinstance(val, abc.Sequence) and not isinstance(val, str)

    def parse_value(self, value):
        if self.is_array(value):
            self.values = value
        else:
            self.values = [value]

    def check(self, event):
        # todo: define rules in documentation
        value = getattr(event, self.prop)
        if self.is_array(value):
            if len(value) != len(self.values):
                return False
            for val in self.values:
                if not val in value:
                    return False
        else:
            for val in self.values:
                if value == val:
                    return True
            return False
        return True


def register(event_name, **kwargs):
    def handle_decorator(func):
        if not hasattr(func, 'pyggel_event_handler_registration'):
            func.pyggel_event_handler_registration = []
        func.pyggel_event_handler_registration.append((event_name, kwargs))
        return func
    return handle_decorator

