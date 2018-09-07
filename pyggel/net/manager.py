
from .connection import Connection


class ConnectionManager:
    def __init__(self, listener, formatter=None, is_server=False):
        self.listener = listener
        self.formatter = formatter
        self.is_server = is_server

        # _raw_manager should be the Asyncio Server or Client transport
        self._raw_manager = None

        self._alive = False

    @property
    def alive(self):
        return self._alive

    def set_raw_manager(self, manager):
        self._raw_manager = manager
        self._alive = True

    def kill(self):
        if not self._alive:
            raise Exception('Manager not active, nothing to kill')
        self._raw_manager.close()
        self._alive = False

    def connection(self, alive=True):
        return Connection(self, alive)
