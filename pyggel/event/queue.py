
from collections import deque
import heapq
import time


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
