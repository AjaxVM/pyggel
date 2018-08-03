
import asyncio

from . import simple_queue


class SimpleLoop:
    def __init__(self, event_queue=None):
        self._handlers = []
        self._event_queue = event_queue or simple_queue.Queue()
        self._alive = False
        self._stopping = False
        self._running_forever = False

    @property
    def alive(self):
        return self._alive

    @property
    def stopping(self):
        return self._stopping

    def _allow_run(self):
        return self._alive and not self._stopping

    def _dispatch_builtin(self, name):
        for handler in self._handlers:
            if self._allow_run():
                getattr(handler, name)()

    def _dispatch_event(self, event):
        event.start()
        for handler in self._handlers:
            if self._allow_run():
                handler.handle(event)
        event.finish()

    def _tick(self):
        self._dispatch_builtin('tick')

        for event in self._event_queue.consume():
            self._dispatch_event(event)

    def add_handler(self, handler):
        if handler in self._handlers:
            raise ValueError('Handler already assigned to this loop')
        if handler.loop:
            raise ValueError('Handler already assigned to another loop')

        handler.loop = self

        self._handlers.append(handler)

    def schedule(self, event, delay=None):
        if self._alive:
            self._event_queue.schedule(event, delay)

    def stop(self):
        if self._stopping:
            raise Exception('Already stopping')
        if not self._alive:
            raise Exception('Not started')

        self._stopping = True

    def start(self):
        if self._alive:
            raise Exception('Already running')
        self._alive = True
        self._stopping = False
        self._dispatch_builtin('start')

        while self._allow_run():
            self._tick()

        self._dispatch_builtin('stop')
        self._stopping = False
        self._alive = False


#TODO: if we schedule event handle tasks immediately it will be different than the original loop
#where new handlers could be registered while an event is being processed and then it processes...
#how do we either prevent new handlers handling event or make async support added handlers?

class AsyncLoop(SimpleLoop):
    def __init__(self):
        self._handlers = []
        self._alive = False

    async def _run(self):
        while self._alive:
            self._dispatch_builtin('tick')

            await asyncio.sleep(0)

    def _dispatch_event(self, loop, delay, func, *args):
        # internal function to basically schedule the asyncio loop call based on delay
        if delay:
            loop.call_later(delay, func, *args)
        else:
            loop.call_soon(func, *args)

    def schedule(self, event, delay=None):
        async_loop = asyncio.get_event_loop()

        self._dispatch_event(async_loop, delay, event.start)
        for handler in self._handlers:
            if self._alive:
                self._dispatch_event(async_loop, delay, handler.handle, event)

        self._dispatch_event(async_loop, delay, event.finish)

    def start(self):
        if self._alive:
            raise Exception('Already running')

        self._alive = True
        self._stopping = False
        self._dispatch_builtin('start')

        async_loop = asyncio.get_event_loop()
        async_loop.run_until_complete(self._run())

        self._dispatch_builtin('stop')
        self._stopping = False
        self._alive = False
