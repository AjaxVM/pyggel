
import asyncio

from ..event import loop
from .formatter import TextFormat
from .listener import ConnectionListener
from .manager import ConnectionManager


async def _start_server(loop, manager, hostname, port):
    try:
        server = await loop.create_server(manager.connection, hostname, port)
        manager.set_raw_manager(server)
        manager.listener.server_setup(manager)
    except Exception as err:
        manager.listener.server_init_error(manager.connection(False), err)


async def _connect(loop, manager, hostname, port):
    try:
        client = await loop.create_connection(manager.connection, hostname, port)
        manager.set_raw_manager(client[0]) # send the transport in
        manager.listener.client_setup(manager)
    except Exception as err:
        manager.listener.client_connection_error(manager.connection(False), err)


def server(hostname='localhost', port=7779, async_loop=None, manager=None, listener=None, formatter=None):
    if manager and (listener or formatter):
        raise Exception('if manager is defined, listener and formatter may not be used')

    if not manager:
        manager = ConnectionManager(
            listener or ConnectionListener(),
            formatter or TextFormat(),
            is_server = True
        )

    if not async_loop:
        # user isn't managing this, so just grab the current loop
        async_loop = asyncio.get_event_loop()
    elif isinstance(async_loop, loop.AsyncLoop):
        # handle if we are getting one of our loops
        async_loop = async_loop.async_loop
    elif not isinstance(async_loop, asyncio.AbstractEventLoop):
        raise Exception('async_loop myst be an asyncio loop, or a pyggel AsyncLoop')

    # schedule setup of server
    async_loop.create_task(_start_server(async_loop, manager, hostname, port))

    return manager


def client(hostname='localhost', port=7779, async_loop=None, manager=None, listener=None, formatter=None):
    if manager and (listener or formatter):
        raise Exception('if manager is defined, listener and formatter may not be used')

    if not manager:
        manager = ConnectionManager(
            listener or ConnectionListener(),
            formatter or TextFormat(),
            is_server = False
        )

    if not async_loop:
        # user isn't managing this, so just grab the current loop
        async_loop = asyncio.get_event_loop()
    elif hasattr(async_loop, 'async_loop'):
        # handle if we are getting one of our loops
        async_loop = async_loop.async_loop
    elif not isinstance(async_loop, asyncio.AbstractEventLoop):
        raise Exception('async_loop myst be an asyncio loop, or a pyggel AsyncLoop')

    # schedule connection to server
    async_loop.create_task(_connect(async_loop, manager, hostname, port))

    return manager
