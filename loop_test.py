

import asyncio
from pyggel import event_loop

class MyHandler(event_loop.handler.Handler):
    def __init__(self):
        super().__init__()
        self.evt = event_loop.event_tracker.EventTracker(self)

    def tick(self):
        if self.evt.schedule_once(event_loop.event.Event('laugh'), 1):
            print('snicker')

        self.evt.schedule_once(event_loop.event.Event('random'), 0.3)

    @event_loop.handler.register('laugh')
    def do_something(self, event):
        print('hahaha')
        self.evt.schedule_once(event_loop.event.Event('cough'), 2)


def handle_cough(event, loop):
    print('cough')
    loop.schedule(event_loop.event.Event('wheeze'), 0.5)

def handle_wheeze(event):
    print(event.type)

def handle_random():
    print('woah.... dude')

def main():
    loop = event_loop.loop.SimpleLoop()
    # loop = event_loop.loop.AsyncLoop()
    handler = MyHandler()
    handler.register('cough', handle_cough)
    handler.register('wheeze', handle_wheeze)
    handler.register('random', handle_random)
    loop.add_handler(handler)
    loop.start()

main()
