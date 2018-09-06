
import asyncio, random

from pyggel import net2
from pyggel.event import handler, loop

class MyHandler(handler.Handler):

    def __init__(self, server, client):
        super().__init__()

        self.server = server
        self.client = client

    def label(self, evt):
        if evt.connection.manager == self.server:
            return 'server'
        return 'client'

    @handler.register('connection')
    def test(self, evt):
        print('other', evt.name, self.label(evt))

    @handler.register('connection.new')
    def handle(self, evt):
        print('new', self.label(evt))
        evt.connection.send('hi')

    @handler.register('connection.message')
    def message(self, evt):
        print('message', self.label(evt), evt.message)
        if not evt.connection.manager.is_server:
            evt.connection.send('got it, goodbye')
            evt.connection.close()
        else:
            print('stopping')
            self.loop.stop()

    @handler.register('connection.error:server_init')
    def handle_server_error(self, evt):
        print('server_init_error', evt.message, evt.error)
        print('stopping')
        self.loop.stop()

    @handler.register('connection.error:client_connection')
    def handle_client_error(self, evt):
        print('client_conn_error', evt.message, evt.error)
        print('stopping')
        self.loop.stop()


def server_and_client():
    print('\nstart: server_and_client')
    print('this should be good')
    my_loop = loop.AsyncLoop()

    server_manager = net2.start_server()
    my_loop.add_listener(server_manager.listener)

    client_manager = net2.connect()
    my_loop.add_listener(client_manager.listener)

    hand = MyHandler(server_manager, client_manager)

    my_loop.add_handler(hand)

    my_loop.start()
    return my_loop, [server_manager, client_manager]


def client_no_server():
    print('\nstart: client_no_server')
    print('this should have a client connection error')
    my_loop = loop.AsyncLoop()

    client_manager = net2.connect()
    my_loop.add_listener(client_manager.listener)

    hand = MyHandler(None, client_manager.listener)

    my_loop.add_handler(hand)

    my_loop.start()
    return my_loop, [client_manager]


def double_server():
    print('\nstart: double_server')
    print('this should have a server bind error')
    my_loop = loop.AsyncLoop()

    server_manager = net2.start_server()
    my_loop.add_listener(server_manager.listener)

    server_manager2 = net2.start_server()
    my_loop.add_listener(server_manager2.listener)

    hand = MyHandler(None, None)

    my_loop.add_handler(hand)

    my_loop.start()
    return my_loop, [server_manager, server_manager2]


async def run_func(func):
    loop, managers = func()
    while loop.alive:
        await asyncio.sleep(1)

    for m in managers:
        if m.alive:
            m.kill()

async def main():
    await run_func(server_and_client)
    await run_func(client_no_server)
    await run_func(double_server)

asyncio.get_event_loop().run_until_complete(main())

# let's execute the good example again (outside of loop execution) to make sure it works when it manages the loop as well
server_and_client()
