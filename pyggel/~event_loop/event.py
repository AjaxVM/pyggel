

class Event:
    def __init__(self, type='event', params={}):
        self._type = type
        self._params = params

        self._handled = False
        self._processing = False

    @property
    def type(self):
        return self._type
    
    @property
    def params(self):
        return self._params

    @property
    def handled(self):
        return self._handled
    
    @property
    def processing(self):
        return self._processing

    def start(self):
        self._processing = True

    def finish(self):
        self._handled = True
        self._processing = False
