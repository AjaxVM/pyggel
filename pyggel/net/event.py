
from ..event import event


class ConnectionEvent(event.Event):
    def __init__(self, name, connection, message=None, error=None):
        super().__init__('connection', name)
        self.connection = connection
        self.message = message
        self.error = error


class ManagerEvent(event.Event):
	def __init__(self, name, manager):
		super().__init__('net', name)
		self.manager = manager
