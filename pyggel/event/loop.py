
import asyncio

from ..clock import BaseClock
from .queue import Queue, TimedQueue


class Loop:
    def __init__(self, handlers=None, listeners=None, clock=None, limit_fps=None):
        self._handlers = []
        self._listeners = []

        self._running = False
        self._stopping = False

        self._clock = clock or BaseClock()
        self.limit_fps = limit_fps if limit_fps and limit_fps > 0 else None

        self._scheduled_events = TimedQueue()
        self._immediate_events = Queue()
        self._handling_event = False

        self._event_index = set() # events we are currently tracking

        if handlers:
            self.add_handlers(handlers)

        if listeners:
            self.add_listeners(listeners)

    @property
    def running(self):
        return self._running
    
    @property
    def stopping(self):
        return self._stopping

    @property
    def alive(self):
        return self._running and not self._stopping

    @property
    def clock(self):
        return self._clock

    def _handle_event(self, event):
        # TODO: these status updates might be unnecessy overhead - is there a real use case?
        self._handling_event = True
        event._scheduled = False
        event._handling = True
        for handler in self._handlers:
            # events can be cancelled once processing starts (ie for ui to stop propagation)
            # TODO: handlers should have "priority" - higher is sorter first (get first shot at events)
            # so we can support ui taking events first and letting only uncaught ones continue to game
            if event._cancelled:
                break
            handler.handle_event(event)
        event._handling = False
        event._handled = True
        self._handling_event = False

    def _run_once(self, delta):
        # send tick command
        for handler in self._handlers:
            handler.tick(delta)

        # check if we have any new events
        # listener.check should collect any events and call dispatch to send to handlers
        for listener in self._listeners:
            listener.check()

        # dispatch any queued events that are ready
        for event in self._immediate_events.all():
            self._handle_event(event)

        for event in self._scheduled_events.all():
            self._handle_event(event)

    def reindex_events(self):
        self._event_index = set()
        for handler in self._handlers:
            for event_type in handler.get_registered():
                self._event_index.add(event_type)

    def prioritize_handlers(self):
        # sort list of handlers by negative priority, so highest is processed first
        self._handlers.sort(key=lambda handler: -handler._priority)

    def add_handler(self, handler):
        handler.set_loop(self)
        self._handlers.append(handler)
        self.reindex_events()
        self.prioritize_handlers()

    def remove_handler(self, handler):
        self._handlers.remove(handler)
        self.reindex_events()

    def add_handlers(self, handlers):
        for handler in handlers:
            handler.set_loop(self)
            self._handlers.append(handler)
        self.reindex_events()
        self.prioritize_handlers()

    def add_listener(self, listener):
        listener.set_loop(self)
        self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def add_listeners(self, listeners):
        for listener in listeners:
            self.add_listener(listener)

    def dispatch(self, event, delay=0):
        if not event.name in self._event_index:
            return
        if delay:
            event._scheduled = True
            self._scheduled_events.add(event, delay)
        elif self._handling_event:
            event._scheduled = True
            # currently handling an event, so stick it in a queue instead, so we don't just chain down
            self._immediate_events.add(event)
        else:
            # immediately run this, so we don't have the overhead of queueing it
            self._handle_event(event)

    def get_delta(self):
        return self._clock.tick()

    def start(self):
        if self._running:
            raise Exception('Already running')

        self._running = True
        self._stopping = False

        while self.alive:
            self._run_once(self.get_delta())
            if self._clock.tick_limit:
                self._clock.tick_limit()

        self._stopping = False
        self._running = False

    def stop(self):
        if not self._running:
            raise Exception('Not running')
        if self._stopping:
            raise Exception('Already stopping')

        self._stopping = True


class AsyncLoop(Loop):
    '''asyncio compatible Loop'''
    def __init__(self, async_loop=None, handlers=None, listeners=None, clock=None, limit_fps=None):
        super().__init__(handlers, listeners, clock, limit_fps)
        self.async_loop = async_loop or asyncio.get_event_loop()

    async def _run(self):
        while self.alive:
            self._run_once(self.get_delta())
            if self._clock.tick_limit_async:
                await self._clock.tick_limit_async()
            else:
                await self._clock.sleep_async(0)

    def start(self):
        if self._running:
            raise Exception('Already running')

        self._running = True
        self._stopping = False

        self.async_loop.run_until_complete(self._run())

        self._stopping = False
        self._running = False
