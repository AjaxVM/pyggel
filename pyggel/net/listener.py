
from collections import deque
from ..event import listener
from .event import ConnectionEvent, ManagerEvent


class ConnectionListener(listener.Listener):
    def __init__(self):
        super().__init__()

        # if we get a network event, but are not assigned a loop, we will store them in _events
        # this way the listener can be used without our loop as desired
        self._events = None

    def set_manager(self, manager):
        self.manager = manager

    def set_loop(self, loop):
        super().set_loop(loop)

        # push any stored events into the loop queue
        for event in self.get_events():
            self._loop.dispatch(event)
        self._events = None

    def _dispatch(self, evt):
        if self._loop:
            self._loop.dispatch(evt)
        else:
            if not self._events:
                self._events = deque()
            self._events.append(evt)

    def get_events(self):
        if self._events:
            for i in range(len(self._events)):
                yield self._events.popleft()

    def check(self):
        # we don't need to do anything here, as we can asynchronously dispatch events
        # and we dispatch any "early" events as soon as we have the loop
        pass

    def new_connection(self, connection):
        if connection.manager.is_server:
            self._dispatch(ConnectionEvent('new', connection))
        else:
            self._dispatch(ConnectionEvent('connected', connection))

    def lost_connection(self, connection):
        if connection.manager.is_server:
            self._dispatch(ConnectionEvent('lost', connection))
        else:
            self._dispatch(ConnectionEvent('disconnected', connection))

    def message(self, connection, message):
        self._dispatch(ConnectionEvent('message', connection, message))

    def server_init_error(self, connection, err):
        self._dispatch(ConnectionEvent('error:server_init', connection, error=err))

    def client_connection_error(self, connection, err):
        self._dispatch(ConnectionEvent('error:client_connection', connection, error=err))

    def server_setup(self, manager):
        self._dispatch(ManagerEvent('server_setup', manager))

    def client_setup(self, manager):
        self._dispatch(ManagerEvent('client_setup', manager))
