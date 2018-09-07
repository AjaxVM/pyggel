

import sys, time
from pyggel import clock
from pyggel.event import loop, handler

class MyHandler(handler.Handler):
    def __init__(self):
        super().__init__()

    def tick(self, delta):
        sys.stdout.write('\rfps: %s '%int(round(self.loop.clock.fps())))

def main():
    # c = clock.FpsClock(max_fps=100, max_deltas=1000)
    c = clock.FpsClock(max_fps=100, max_deltas=1000, tick_resolution_async=0.6)
    # c = clock.PreciseFpsClock(max_fps=100, max_deltas=1000)
    # loop = loop.Loop(limit_fps=100, clock=c)
    my_loop = loop.AsyncLoop(limit_fps=100, clock=c)

    my_loop.add_handler(MyHandler())

    my_loop.run()

main()
