

'''
TODO: look at using pyuv to build an event loop that works for servers/clients better

actually, keep in mind loop run once mode so it can fit in our loop maybe?
'''

from .. import event_loop
from . import connection


class BaseServer():
    def __init__(self,
                 hostname='localhost',
                 port=7779,
                 max_clients=2,
                 client_opts={}):

        self.hostname = hostname
        self.port = port
        self.max_clients = max_clients

        self.connection = connection.Connection((self.hostname, self.port), socket=None, *client_opts)

    def stop(self):
        self.connection.kill()

    def start(self):
        self.connection.listen(self.max_clients)

        while self.connection.alive:
            # do stuff - figure out how to emulate managers
