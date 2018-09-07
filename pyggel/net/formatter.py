
from collections import deque
import json

try:
    import msgpack
    HAVE_MSG_PACK = True
except:
    HAVE_MSG_PACK = False


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
