
from ..event import event


class ConnectionEvent(event.Event):
    def __init__(self, connection, name, message=None, error=None):
        super().__init__('connection', name)
        self.connection = connection
        self.message = message
        self.error = error
