import random

from pyggel import net2
from pyggel.event import handler, loop

class MyHandler(handler.Handler):

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

    @handler.register('connection')
    def test(self, evt):
        print('other', evt.aliases[0], 'server' if evt.connection.is_server else 'client')

    @handler.register('connection.new')
    def handle(self, evt):
        print('new', 'server' if evt.connection.is_server else 'client')
        evt.connection.send('hi')

    @handler.register('connection.message')
    def message(self, evt):
        print('message', 'server' if evt.connection.is_server else 'client', evt.message)
        evt.connection.close()
        # evt.connection.transport.write_eof()


def main():

    my_loop = loop.AsyncLoop()

    hand = MyHandler()

    my_loop.add_handler(hand)

    server_listener = net2.start_server()
    my_loop.add_listener(server_listener)

    client_listener = net2.connect()
    my_loop.add_listener(client_listener)

    my_loop.start()

main()
