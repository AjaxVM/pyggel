

class Event:
    def __init__(self, name, aliases=None):
        self.name = name

        self.has_alias = bool(aliases)
        self.aliases = aliases

        self._cancelled = False
        self._scheduled = False
        self._handling = False
        self._handled = False     

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
