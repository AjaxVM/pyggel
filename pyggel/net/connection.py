

import select, socket
from . import packet

# todo: use generators/yield where possible for speed

class Connection:
    def __init__(self,
                 address,
                 socket = None,
                 read_buffer_size=1024,
                 data_delimiter='{:::}'):

        self._alive = bool(socket)
        self.is_server = False

        self.socket = socket or self._generate_socket()
        self.address = address

        self.read_buffer_size = read_buffer_size
        self.data_delimiter = data_delimiter

        self._data = ''

    def _generate_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        return sock

    def _process_data(self):
        messages = self._data.split(self.data_delimiter)
        if not self._data.endswith(self.data_delimiter):
            # we have a partial message for the last one, keep that
            self._data = messages[-1]
            messages = messages[:-1]

        return [packet.Packet(i) for i in messages]

    @property
    def alive(self):
        return self._alive

    def kill(self):
        if not self._alive:
            self.socket.close()
            self._alive = False
            self.is_server = False
            return
        raise Exception('Not connected')

    def connect(self):
        if self.is_server:
            raise Exception('Cannot connect when serving')
        elif self._alive: 
            raise Exception('Already connected')

        self.socket.connect(self.address)
        self._alive = True

    def listen(self, client_backlog=8):
        if self.is_server:
            raise Exception('Already serving')
        elif self._alive:
            raise Exception('Cannot serve when connected as client')
            
        self.socket.bind(self.address)
        self.socket.listen(client_backlog)
        self._alive = True
        self.is_server = True

    def ready_for_read(self, wait_timeout=0):
        return bool(select.select([self.socket], [], [], wait_timeout))

    def accept_connection(self):
        # wait for, and return a new Connection, if we are serving
        # connection is configured with the same parameters we are
        if not self._alive:
            raise Exception('Not connected')
        elif not self.is_server:
            raise Exception('Not running as server')

        if self._alive and self.is_server:
            sock, address = self.socket.accept()
            return Connection(address,
                              socket=sock,
                              read_buffer_size=self.read_buffer_size,
                              data_delimiter=self.data_delimiter)

    def read(self):
        if not self._alive:
            raise Exception('Not connected')
        elif self.is_server:
            raise Exception('Cannot read when serving')

        try:
            data = self.socket.recv(self.read_buffer_size)
        except:
            # sockets are supposed to return empty data if they are dead
            # but sometimes we get an error - so handle the same
            data = ''

        if data:
            self._data += data.decode()

        packets = self._process_data()
        if not data:
            # bye bye
            self.kill()
            packet.append(packet.Packet(None, packet.Status.DISCONNECT))

        return packets

    def send(self, data):
        if not self._alive:
            raise Exception('Not connected')
        if self.is_server:
            raise Exception('Cannot write when serving')

        try:
            self.socket.send((data + self.data_delimiter).encode())
        except:
            self.kill()
