

class Event:
    def __init__(self, name, **kwargs):
        self.name = name

        self._cancelled = False
        self._scheduled = False
        self._handling = False
        self._handled = False

        for key in kwargs:
            setattr(self, key, kwargs[key])

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
