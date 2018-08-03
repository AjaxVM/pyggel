

class Status:
    OK = 'OK'
    ERROR = 'ERROR'
    DISCONNECT = 'DISCONNECT'


class Packet:
    def __init__(self, data=None, status=Status.OK):
        self.data = data
        self.error = error


class Transport:
    def __init__(self, connection, packet, manager=None):
        self.connection = connection
        self.packet = packet
        self.manager = manager # TODO: maybe this should be a property of connection?

    @property
    def data(self):
        return self.packet.data

    @property
    def status(self):
        return self.packet.status

    @property
    def alive(self):
        return self.connection.alive

    def write(self, data):
        if self.manager:
            # todo: as above, maybe this makes more sense at the connection level?
            self.manager.write(self.connection, data)
        else:
            self.connection.send(data)

    def end(self):
        if self.connection.alive:
            self.connection.kill()
    

