
import asyncio
from collections import deque
import heapq
import pygame
import time

from .clock import BaseClock

if hasattr(time, 'time_ns'):
    HAVE_NS_TIME = True
    NS_TO_MS_RATIO = 10 ** 6
else:
    HAVE_NS_TIME = False


class Queue:
    '''First in, first out queue'''
    def __init__(self):
        self.q = deque()
        self.size = 0

    def _clear_cancelled(self):
        # pops queue until we reach an element that is not cancelled
        # or we run out of elements
        while self.size and self.q[0]._cancelled:
            self._pop()

    def _pop(self):
        # assume current size is > 0
        # check should be performed by caller
        self.size -= 1
        return self.q.popleft()

    def add(self, item):
        self.q.append(item)
        self.size += 1

    def pop(self):
        # clear cancelled events
        self._clear_cancelled()
        # return next event, if any
        if self.size:
            return self._pop()

    def all(self):
        # loop through current events
        # pop them, and yield any that are not cancelled
        # this causes any events added while processing this group to await next call
        for i in range(self.size):
            event = self._pop()
            if event:
                yield event


class TimedQueue(Queue):
    '''Timed-based priority queue
       Only pops/alls items that were scheduled before now (or a time argument'''
    def __init__(self):
        self.q = []
        self.size = 0

    def _clear_cancelled(self):
        while self.size and self.q[0][1]._cancelled:
            self._pop()

    def _pop(self):
        self.size -= 1
        return heapq.heappop(self.q)[1]

    def ready(self, cur_time=None):
        if not cur_time:
            cur_time = time.time()
        return self.q[0][0] < cur_time

    def add_at(self, item, scheduled_time):
        heapq.heappush(self.q, (scheduled_time, item))
        self.size += 1

    def add(self, item, delay=0):
        self.add_at(item, time.time() + delay)

    def pop(self, cur_time=None):
        self._clear_cancelled()
        if self.size and self.ready(cur_time):
            return self._pop()

    def all(self, cur_time=None):
        if not cur_time:
            cur_time = time.time()

        for _ in range(self.size):
            if not self.ready(cur_time):
                break
            event = self._pop()[1]
            if not event._cancelled:
                yield event


class Event:
    def __init__(self, name, **kwargs):
        self.name = name

        self._cancelled = False
        self._scheduled = False
        self._handling = False
        self._handled = False

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def cancel(self):
        self._cancelled = True

    @property
    def handling(self):
        return self._handling

    @property
    def scheduled(self):
        return self._scheduled
    
    @property
    def handled(self):
        return self._handled


class Handler:
    def __init__(self, priority=0):
        self._priority = priority
        self._loop = None

        self._callbacks = {}
        self._check_for_registered()

    def _check_for_registered(self):
        for prop_name in dir(self):
            prop = getattr(self, prop_name)
            if callable(prop) and hasattr(prop, 'pyggel_event_handler_registration'):
                self.register(prop.pyggel_event_handler_registration, prop)

    @property
    def loop(self):
        return self._loop

    @property
    def priority(self):
        return self._priority

    def set_loop(self, loop):
        if self._loop:
            raise Exception('Handler already assigned to an event loop')

        self._loop = loop

    def handle_event(self, event):
        pass

    def register(self, event_name, callback):
        if event_name in self._callbacks:
            raise Exception(f'Event "{event_name}" already registered in Handler')

        self._callbacks[event_name] = callback

    def tick(self, delta):
        pass


def register(event_name):
    def handle_decorator(func):
        func.pyggel_event_handler_registratio = event_name
        return func
    return handle_decorator


class Listener:
    '''Object that represents some asynchronous event system (ie keyboard, mouse, network)
       expected to be "ready" when passed to handler
    '''
    def __init__(self):
        self._loop = None

    @property
    def loop(self):
        return self._loop

    def set_loop(self, loop):
        if self._loop:
            raise Exception('Listener already assigned to an event loop')

        self._loop = loop

    def check(self):
        pass


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

    def prioritize_handlers(self):
        # sort list of handlers by negative priority, so highest is processed first
        self._handlers.sort(key=lambda handler: -handler._priority)

    def add_handler(self, handler):
        handler.set_loop(self)
        self._handlers.append(handler)
        self.prioritize_handlers()

    def remove_handler(self, handler):
        self._handlers.remove(handler)

    def add_handlers(self, handlers):
        for handler in handlers:
            handler.set_loop(self)
            self._handlers.append(handler)
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

    def run(self):
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

    def run(self):
        if self._running:
            raise Exception('Already running')

        self._running = True
        self._stopping = False

        self.async_loop.run_until_complete(self._run())

        self._stopping = False
        self._running = False

