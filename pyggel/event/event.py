

class Event:
    def __init__(self, base_name, name=None, aliases=None):
        self.base_name = base_name
        self.name = self.qualify_name(name)

        self.has_alias = bool(aliases)
        self.aliases = self.qualify_aliases(aliases)

        self._cancelled = False
        self._scheduled = False
        self._handling = False
        self._handled = False

    def qualify_name(self, name):
        return self.base_name + '.' + name

    def qualify_aliases(self, aliases):
        if not aliases:
            return
        # TODO: this seems good by default, but what if someone wants to use, for instance, an input.key and input.mouse event
        # interchangeably, and just refer to it by the alias (like a "hard" alias - maybe have another system on top of this?)
        new_aliases = []
        for alias in aliases:
            new_aliases.append(self.name + ':' + alias)
        return new_aliases

    def cancel(self):
        self._cancelled = True

    @property
    def cancelled(self):
        return self._cancelled

    @property
    def handling(self):
        return self._handling

    @property
    def scheduled(self):
        return self._scheduled
    
    @property
    def handled(self):
        return self._handled


class KWEvent(Event):
    '''Same as Event, but maps any keyword arguments to parameters'''
    def __init__(self, name, **kwargs):
        super().__init__(name)

        self.__dict__.update(kwargs)
