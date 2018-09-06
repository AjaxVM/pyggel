import random

from pyggel import net2
from pyggel.event import handler, loop

class MyHandler(handler.Handler):

    def __init__(self, server, client):
        super().__init__()

        self.server = server
        self.client = client

    # TODO: need a way to differentiate connections as being client or server or something...
    # maybe connection label as a param to the factory/start_server/connect?
    # that seems to work, but maybe not quite what we want

    # TODO: maybe make events different depending on the side, ie
    #       server:
    #           connection.listening, connection.new, connection.message, connection.lost_client
    #       client:
    #           connection.connected, connection.disconnected, connection.message

    # actually this is weird, we get connection.new on the server, but the connection.is_server is True, which is wrong
    # it's more that the handler is the server but it is the connection to the client

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
        evt.connection.close()
        # evt.connection.transport.write_eof()


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
