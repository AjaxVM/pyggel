
import asyncio


class Connection(asyncio.Protocol):
    def __init__(self, manager, alive=True):
        self._closed = False

        self._alive = alive

        self._manager = manager

        self.id = id(self)
        self.transport = None

    @property
    def alive(self):
        return self._alive

    @property
    def ready(self):
        return self.transport and self._alive

    @property
    def manager(self):
        return self._manager

    # event callbacks
    def connection_made(self, transport):
        self.transport = transport
        self._manager.listener.new_connection(self)

    def connection_lost(self, transport):
        # don't submit lost event if it was closed already
        self._alive = False

        if not self._closed:
            self._closed = True
            self._manager.listener.lost_connection(self)

    def data_received(self, data):
        for message in self._manager.formatter.unformat(data):
            self._manager.listener.message(self, message)

    # actions
    def close(self):
        if not self._alive:
            raise Exception('Connection is not alive, cannot close')
        if self._closed:
            raise Exception('Connection already closed')
        self._closed = True
        if self.ready:
            self.transport.write_eof()

    def send(self, message):
        if not self._alive:
            raise Exception('Connection not alive, cannot send')
        if not self.ready:
            raise Exception('Connection not ready, cannot send')
        self.transport.write(self._manager.formatter.format(message))
