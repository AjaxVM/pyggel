# prep lib for net stuff before blowing into it's own dir


import asyncio
from collections import deque
import json

try:
    import msgpack
    HAVE_MSG_PACK = True
except:
    HAVE_MSG_PACK = False

from .event import event, listener, loop


class TextFormat:
    '''Class for formatting text messages for network communication, and unformatting/streaming data into messages'''
    def __init__(self, delimiter='\r\n'):
        self.delimiter = delimiter
        self.raw_buffer = b''
        self.msg_buffer = deque()

    def format(self, data):
        return (data + self.delimiter).encode()

    def unformat(self, data):
        self._stream_in(data)
        return self._stream_consume()

    def _decode(self, data):
        # this is meant to be used by _stream_in to decode each message, if needed
        return data

    def _stream_in(self, data):
        data = data.decode()

        # short-circuit if we have one, entire message
        if data.count(self.delimiter) == 1 and data.endswith(self.delimiter) and not self.raw_buffer:
            self.msg_buffer.append(self._decode(data[:-len(self.delimiter)]))
            return

        if self.delimiter in data:
            messages = data.split(self.delimiter)
            if self.raw_buffer:
                messages[0] = self.raw_buffer + messages[0]

            # if last message was complete this will be empty string, otherwise it is start of next
            self.raw_buffer = messages.pop()
            self.msg_buffer.extend(self._decode(message) for message in messages)
        else:
            self.raw_buffer += data

    def _stream_consume(self):
        for i in range(len(self.msg_buffer)):
            yield self.msg_buffer.popleft()


class JsonFormat(TextFormat):
    def __init__(self, delimiter='\n'):
        super().__init__(delimiter)

    def format(self, data):
        return super().format(json.dumps(data))

    def _decode(self, data):
        return json.loads(data)


class MsgpackFormat(TextFormat):
    def __init__(self):
        # we don't need to define a delimiter or buffer, since msgpack handles that
        # but make sure this works
        if not HAVE_MSG_PACK:
            raise Exception('msgpack not installed')

        self._unpacker = msgpack.Unpacker(use_list=False, raw=False)

    def format(self, data):
        return msgpack.packb(data, use_bin_type=True)

    def _decode(self, data):
        raise NotImplementedError

    def _stream_in(self, data):
        self._unpacker.feed(data)

    def _stream_consume(self):
        yield from self._unpacker


class Connection(asyncio.Protocol):
    def __init__(self, manager, alive=True):
        self._closed = False

        self._alive = alive

        self._manager = manager

        self.id = id(self)
        self.transport = None

    @property
    def alive(self):
        return self._alive

    @property
    def ready(self):
        return self.transport and self._alive

    @property
    def manager(self):
        return self._manager

    # event callbacks
    def connection_made(self, transport):
        self.transport = transport
        self._manager.listener.new_connection(self)

    def connection_lost(self, transport):
        # don't submit lost event if it was closed already
        self._alive = False

        if not self._closed:
            self._closed = True
            self._manager.listener.lost_connection(self)

    def data_received(self, data):
        for message in self._manager.formatter.unformat(data):
            self._manager.listener.message(self, message)

    # actions
    def close(self):
        if not self._alive:
            raise Exception('Connection is not alive, cannot close')
        if self._closed:
            raise Exception('Connection already closed')
        self._closed = True
        if self.ready:
            self.transport.write_eof()

    def send(self, message):
        if not self._alive:
            raise Exception('Connection not alive, cannot send')
        if not self.ready:
            raise Exception('Connection not ready, cannot send')
        self.transport.write(self._manager.formatter.format(message))


# class ConnectionFactory:
class ConnectionManager:
    def __init__(self, listener, formatter=None, is_server=False):
        self.listener = listener
        self.formatter = formatter
        self.is_server = is_server

        # _raw_manager should be the Asyncio Server or Client transport
        self._raw_manager = None

        self._alive = False

    @property
    def alive(self):
        return self._alive

    def set_raw_manager(self, manager):
        self._raw_manager = manager
        self._alive = True

    def kill(self):
        if not self._alive:
            raise Exception('Manager not active, nothing to kill')
        self._raw_manager.close()
        self._alive = False

    def connection(self, alive=True):
        return Connection(self, alive)


class ConnectionListener(listener.Listener):
    def __init__(self):
        super().__init__()

        # if we get a network event, but are not assigned a loop, we will store them in _events
        # this way the listener can be used without our loop as desired
        self._events = None

    def set_manager(self, manager):
        self.manager = manager

    def set_loop(self, loop):
        super().set_loop(loop)

        # push any stored events into the loop queue
        for event in self.get_events():
            self._loop.dispatch(event)
        self._events = None

    def _dispatch(self, evt):
        if self._loop:
            self._loop.dispatch(evt)
        else:
            if not self._events:
                self._events = deque()
            self._events.append(evt)

    def get_events(self):
        if self._events:
            for i in range(len(self._events)):
                yield self._events.popleft()

    def check(self):
        # we don't need to do anything here, as we can asynchronously dispatch events
        # and we dispatch any "early" events as soon as we have the loop
        pass

    def new_connection(self, connection):
        if connection.manager.is_server:
            self._dispatch(ConnectionEvent(connection, 'new'))
        else:
            self._dispatch(ConnectionEvent(connection, 'connected'))

    def lost_connection(self, connection):
        if connection.manager.is_server:
            self._dispatch(ConnectionEvent(connection, 'lost'))
        else:
            self._dispatch(ConnectionEvent(connection, 'disconnected'))

    def message(self, connection, message):
        self._dispatch(ConnectionEvent(connection, 'message', message))

    def server_init_error(self, connection, err):
        self._dispatch(ConnectionEvent(connection, 'error:server_init', error=err))

    def client_connection_error(self, connection, err):
        self._dispatch(ConnectionEvent(connection, 'error:client_connection', error=err))


class ConnectionEvent(event.Event):
    def __init__(self, connection, name, message=None, error=None):
        super().__init__('connection', name)
        self.connection = connection
        self.message = message
        self.error = error


async def _start_server(loop, manager, hostname, port):
    try:
        manager.set_raw_manager(await loop.create_server(manager.connection, hostname, port))
    except Exception as err:
        manager.listener.server_init_error(manager.connection(False), err)


async def _connect(loop, manager, hostname, port):
    try:
        client = await loop.create_connection(manager.connection, hostname, port)
        manager.set_raw_manager(client[0]) # send the transport in
    except Exception as err:
        manager.listener.client_connection_error(manager.connection(False), err)


def start_server(hostname='localhost', port=7779, async_loop=None, manager=None, listener=None, formatter=None):
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


def connect(hostname='localhost', port=7779, async_loop=None, manager=None, listener=None, formatter=None):
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
