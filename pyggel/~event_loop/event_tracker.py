
from . import event


class EventTracker:
    def __init__(self, handler):
        self._waiting_types = {}
        self._handling_types = {}
        self.handler = handler

    def setup_tracking(self, type):
        if not type in self._waiting_types:
            self._waiting_types[type] = 0
            self._handling_types[type] = 0

    def waiting_count(self, type):
        self.setup_tracking(type)
        return self._waiting_types[type]

    def handling_count(self, type):
        self.setup_tracking(type)
        return self._handling_types[type]

    def handle(self, type):
        self.setup_tracking(type)
        self._waiting_types[type] -= 1
        self._handling_types[type] += 1

    def finish(self, type):
        self.setup_tracking(type)
        self._handling_types[type] -= 1

    def schedule(self, event, delay=None):
        self.setup_tracking(event.type)
        self.handler.loop.schedule(EventTrackerEvent(event, self), delay)
        self._waiting_types[event.type] += 1

    def schedule_once(self, event, delay=None):
        self.setup_tracking(event.type)
        if not (self._waiting_types[event.type] or self._handling_types[event.type]):
            self.schedule(event, delay)
            return True
        return False


class EventTrackerEvent(event.Event):
    def __init__(self, event, event_tracker):
        self._event = event
        self._event_tracker = event_tracker

    @property
    def type(self):
        return self._event.type

    @property
    def params(self):
        return self._event.params

    @property
    def handled(self):
        return self._event.handled

    @property
    def processing(self):
        return self._event.processing

    def start(self):
        self._event.start()
        self._event_tracker.handle(self._event.type)

    def finish(self):
        self._event.finish()
        self._event_tracker.finish(self._event.type)
