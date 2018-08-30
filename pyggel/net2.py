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
    def __init__(self, listener, formatter=None, label=None):
        self.formatter = formatter or TextFormat()
        self._listener = listener
        self._closed = False
        self.label = label

        self.id = id(self)
        self.transport = None

    # event callbacks
    def connection_made(self, transport):
        self.transport = transport
        self._listener.new_connection(self)

    def connection_lost(self, transport):
        # don't submit lost event if it was closed already
        if not self._closed:
            self._closed = True
            self._listener.lost_connection(self)

    def data_received(self, data):
        for message in self.formatter.unformat(data):
            self._listener.message(self, message)

    # actions
    def close(self):
        if self._closed:
            raise Exception('Connection already closed')
        self._closed = True
        self.transport.write_eof()

    def send(self, message):
        self.transport.write(self.formatter.format(message))


class ConnectionFactory:
    def __init__(self, listener, formatter=None, label=None):
        self.listener = listener
        self.formatter = formatter
        self.label = label

    def __call__(self):
        return Connection(self.listener, self.formatter, self.label)


class ConnectionListener(listener.Listener):
    def __init__(self):
        super().__init__()

        # if we get a network event, but are not assigned a loop, we will store them in _events
        # this way the listener can be used without our loop as desired
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
        # TODO: this could recursively loop if not added to a loop and this is called... lol
        for evt in self.get_events():
            self._dispatch(evt)

    def new_connection(self, connection):
        self._dispatch(ConnectionEvent(connection, 'new'))

    def lost_connection(self, connection):
        self._dispatch(ConnectionEvent(connection, 'lost'))

    def message(self, connection, message):
        self._dispatch(ConnectionEvent(connection, 'message', message))


class ConnectionEvent(event.Event):
    def __init__(self, connection, name, message=None):
        super().__init__('connection', ('connection.'+name,))
        self.connection = connection
        self.message = message


# TODO: what system do we want to use for this?
# currently have two functions but there is a lot shared

# TODO: more advanced support for connection/socket params
def start_server(hostname='localhost', port=7779, async_loop=None, listener=None, formatter=None, label='server'):
    factory = ConnectionFactory(listener or ConnectionListener(), formatter, label)

    if not async_loop:
        # user isn't managing this, so just grab the current loop
        async_loop = asyncio.get_event_loop()
    elif hasattr(async_loop, 'async_loop'):
        # handle if we are getting one of our loops
        async_loop = async_loop.async_loop
    elif not isinstance(async_loop, asyncio.AbstractEventLoop):
        raise Exception('async_loop myst be an asyncio loop, or a pyggel AsyncLoop')

    # setup the create server part - do we actually want to do this or spawn a background process so game keeps playing?
    async_loop.run_until_complete(async_loop.create_server(factory, hostname, port))

    return factory.listener


# TODO: most of this logic is identical to start_server... at least until we have the advanced socket options
def connect(hostname='localhost', port=7779, async_loop=None, listener=None, formatter=None, label='client'):
    factory = ConnectionFactory(listener or ConnectionListener(), formatter, label)

    # TODO: if we consolidate pyggel AsyncLoop to an asyncio one this check is cleaner
    if not async_loop:
        # user isn't managing this, so just grab the current loop
        async_loop = asyncio.get_event_loop()
    elif hasattr(async_loop, 'async_loop'):
        # handle if we are getting one of our loops
        async_loop = async_loop.async_loop
    elif not isinstance(async_loop, asyncio.AbstractEventLoop):
        raise Exception('async_loop myst be an asyncio loop, or a pyggel AsyncLoop')

    # connect to server - again, should this be a background thing?
    async_loop.run_until_complete(async_loop.create_connection(factory, hostname, port))

    return factory.listener
