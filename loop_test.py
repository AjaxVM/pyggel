

import sys, time
from pyggel import event_loop, clock

class MyHandler(event_loop.Handler):
    def __init__(self):
        super().__init__()

    def tick(self, delta):
        sys.stdout.write('\rfps: %s '%int(round(self.loop.clock.fps())))

def main():
    # c = clock.FpsClock(max_fps=100, max_deltas=1000)
    c = clock.PreciseFpsClock(max_fps=100, max_deltas=1000)
    # loop = event_loop.Loop(limit_fps=100, clock=c)
    loop = event_loop.AsyncLoop(limit_fps=100, clock=c)

    loop.add_handler(MyHandler())

    # loop.clock.track_deltas = True
    # loop.clock.max_deltas = 100

    loop.run()

main()
