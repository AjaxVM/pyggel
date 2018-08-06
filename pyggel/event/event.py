

class Event:
    def __init__(self, name):
        self.name = name

        self._cancelled = False
        self._scheduled = False
        self._handling = False
        self._handled = False     

    def cancel(self):
        self._cancelled = True

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
