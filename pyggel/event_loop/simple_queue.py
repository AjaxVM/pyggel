
import time


class Queue:
    def __init__(self):
        self.events = []
        self.timed_events = []

    def schedule(self, event, delay=None):
        if delay:
            self.timed_events.append(DelayedEventWrapper(event, delay))
        else:
            self.events.append(event)

    def consume(self):
        check_events = len(self.events)
        check_delayed = len(self.timed_events)

        for i in range(check_events):
            yield self.events.popleft()

        i = 0
        cur_time = time.time() # make sure we don't potentially change order with execution time
        for _ in range(check_delayed):
            delayed = self.timed_events[i]
            if cur_time - delayed.init_time < delayed.delay:
                i += 1
                continue
            yield self.timed_events.pop(i).event


class DelayedEventWrapper:
    def __init__(self, event, delay):
        self.event = event
        self.delay = delay
        self.init_time = time.time()
