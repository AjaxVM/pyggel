

class Listener:
    '''Object that represents some asynchronous event system (ie keyboard, mouse, network)
       expected to be "ready" when passed to handler
    '''
    def __init__(self):
        self._loop = None

    @property
    def loop(self):
        return self._loop

    def set_loop(self, loop):
        if self._loop:
            raise Exception('Listener already assigned to an event loop')

        self._loop = loop

    def check(self):
        print('boo')
        pass
