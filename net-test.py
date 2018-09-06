import random

from pyggel import net2
from pyggel.event import handler, loop

class MyHandler(handler.Handler):

    def __init__(self, server, client):
        super().__init__()

        self.server = server
        self.client = client

    def label(self, evt):
        if evt.connection.listener == self.server:
            return 'server'
        return 'client'

    @handler.register('connection')
    def test(self, evt):
        print('other', evt.aliases[0], self.label(evt))

    @handler.register('connection.new')
    def handle(self, evt):
        print('new', self.label(evt))
        evt.connection.send('hi')

    @handler.register('connection.message')
    def message(self, evt):
        print('message', self.label(evt), evt.message)
        if not evt.connection.is_server:
            evt.connection.send('got it, goodbye')
            evt.connection.close()


def main():
    my_loop = loop.AsyncLoop()

    server_listener = net2.start_server()
    my_loop.add_listener(server_listener)

    client_listener = net2.connect()
    my_loop.add_listener(client_listener)

    hand = MyHandler(server_listener, client_listener)

    my_loop.add_handler(hand)

    my_loop.start()

main()
