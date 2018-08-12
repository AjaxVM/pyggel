# prep lib for net stuff before blowing into it's own dir


import asyncio
from collections import deque
import json

try:
    import msgpack
    HAVE_MSG_PACK = True
except:
    HAVE_MSG_PACK = False


class TextPacker:
    '''Class for formatting text messages for network communication, and unformatting/streaming data into messages'''
    def __init__(self, delimiter='\r\n'):
        self.delimiter = delimiter
        self.__buf = ''
        self._msg_buf = deque()

    def pack(self, data):
        return (data + self.delimiter).encode()

    def unpack(self, data):
        return data[:-len(self.delimiter)].decode()

    def _unpack_raw(self, data):
        # this is meant to be used by unpack_feed to decode each message
        return data.decode()

    def unpack_feed(self, data):
        data = data.decode()

        if self.delimiter in data:
            messages = data.split(self.delimiter)
            if self.__buf:
                messages[0] = self._buf + messages[0]

            # if last message was complete this will be empty string, otherwise it is start of next
            self.__buf = messages.pop()
            self._msg_buf.extend(self._unpack_raw(message) for message in messages)
        else:
            self.__buf += data

    def unpack_consume(self):
        for i in range(len(self._msg_buf)):
            yield self._msg_buf.popleft()


class JsonPacker(TextPacker):
    def __init__(self, delimiter='\n'):
        super().__init__(delimiter)

    def pack(self, data):
        return super().pack(json.dumps(data))

    def unpack(self, data):
        return json.loads(super().unpack(data))

    def _unpack_raw(self, data):
        return json.loads(data.decode())


class MsgpackPacker(TextPacker):
    def __init__(self):
        # we don't need to define a delimiter or buffer, since msgpack handles that
        # but make sure this works
        if not HAVE_MSG_PACK:
            raise Exception('msgpack not installed')

        self._unpacker = msgpack.Unpacker(use_list=False, raw=False)

    def pack(self, data):
        return msgpack.packb(data, use_bin_type=True)

    def unpack(self, data):
        return msgpack.unpackb(data, use_list=False, raw=False)

    def _unpack_raw(self, data):
        raise NotImplementedError('MsgpackPacker does not use this method')

    def unpack_feed(self, data):
        self._unpacker.feed(data)

    def unpack_consume(self):
        yield from self._unpacker

