
import asyncio
from collections import deque
import time
import pygame

if hasattr(time, 'time_ns'):
    HAVE_NS_TIME = True
    NS_TO_MS_RATIO = 10 ** 6
else:
    HAVE_NS_TIME = False

class BaseClock:
    '''
        Base clock that does not support framerate limits.
        
        Uses time.time_ns() if available, and falls back to time.time()
        Interface is in ms
    '''

    # tick_limit should be defined as a method on classes that limit fps
    tick_limit = None
    tick_limit_async = None

    def __init__(self):
        self.last_tick = None

    def time(self):
        if HAVE_NS_TIME:
            return time.time_ns() / NS_TO_MS_RATIO
        # fall back to time.time() - convert to ms
        return time.time() * 1000

    def sleep(self, ms):
        # convert ms -> seconds
        if ms > 0:
            time.sleep(ms / 1000)

    async def sleep_async(self, ms):
        # sleep_async should *always* at least sleep(0) as that is our method
        # to allow coroutines a chance to run
        if ms > 0:
            await asyncio.sleep(ms / 1000)
        else:
            await asyncio.sleep(0)

    def tick(self):
        new = self.time()
        if self.last_tick:
            delta = new - self.last_tick
        else:
            delta = 0
        self.last_tick = new

        return delta


class TrackingClock(BaseClock):
    '''BaseClock with delta tracking/average'''

    def __init__(self, max_deltas=10):
        super().__init__()

        self._max_deltas = max_deltas
        self.past_deltas = deque(maxlen=max_deltas)

    @property
    def max_deltas(self):
        return self._max_deltas

    def tick(self):
        delta = super().tick()
        if delta:
            self.past_deltas.append(delta)
        return delta

    def average(self):
        # return avg delta ms over [max_deltas] ticks
        if self.past_deltas:
            return sum(self.past_deltas) / len(self.past_deltas)
        # handle startup situation and we have no deltas
        return 0

    def worst(self):
        # return the lowest fps over [max_deltas] ticks
        return max(self.past_deltas) if self.past_deltas else 0

    def best(self):
        # return best fps over [max_deltas] ticks
        return min(self.past_deltas) if self.past_deltas else 0


class FpsClock(TrackingClock):
    '''
        Clock with fps tracking/limiting options

        This clock uses time.sleep for limiting fps, which has
        accuracy issues but is good for power conservation

        tick_resolution/tick_resolution_async are used to try to 
    '''
    def __init__(self,
                 max_fps=None,
                 max_deltas=10,
                 tick_resolution=0.5,
                 tick_resolution_async=0.1
                ):
        super().__init__(max_deltas)
        self.max_fps = max_fps
        self._fps_to_ms = 1 / self.max_fps * 1000
        self.tick_resolution = tick_resolution
        self.tick_resolution_async = tick_resolution_async

    def _calc_tick_wait(self):
        if self.max_fps and self.last_tick:
            cur_time = self.time()
            target = self.last_tick + self._fps_to_ms
            if cur_time < target:
                return target

    def tick_limit(self):
        # we define tick_limit so it can be used to limit fps
        target = self._calc_tick_wait()
        if target:
            if self.tick_resolution:
                while self.time() + self.tick_resolution < target:
                    self.sleep(self.tick_resolution)
            else:
                self.sleep(target - self.time())

    async def tick_limit_async(self):
        target = self._calc_tick_wait()
        if target:
            if self.tick_resolution_async:
                _slept = False
                while self.time() + self.tick_resolution_async < target:
                    await self.sleep_async(self.tick_resolution_async)
                    if not _slept:
                        _slept = True
                if not _slept:
                    # we are expected to yield to other coroutines during this, even if we want to run asap
                    await self.sleep_async(0)
            else:
                await self.sleep_async(target - self.time())
        else:
            await self.sleep_async(0)

    def fps(self):
        # return average fps over last [max_deltas] ticks
        average_delta = self.average()
        if average_delta:
            # calculate frames for last 1000ms to conver to seconds
            return 1000 / average_delta
        return 0

    def best_fps(self):
        #return best fps over last [max_deltas] ticks
        best = self.best()
        if best:
            return 1000 / best
        return 0

    def worst_fps(self):
        worst = self.worst()
        if worst:
            return 1000 / worst
        return 0


class PreciseFpsClock(FpsClock):
    '''Same as fps clock, but uses a greedy busy loop for more accurate sleeping'''
    def __init__(self, max_fps=None, max_deltas=10):
        super().__init__(max_fps, max_deltas, None, None)

    def tick_limit(self):
        target = self._calc_tick_wait()
        if target:
            while self.time() < target:
                pass

    async def tick_limit_async(self):
        # async version still uses busy loop, but will first sleep(0)
        # to allow coroutines to run before delaying
        # then use the same blocking greedy loop for accuracy
        await self.sleep_async(0)
        self.tick_limit()

