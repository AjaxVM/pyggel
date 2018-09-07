
from collections import deque

def sum_deque1(d):
    tot = 0
    for i in range(len(d)):
        tot += i

    return tot

def sum_deque2(d):
    return sum([i for i in d])

def test_setter1():
    class a:
        pass

    b = a()

    b.test = None
    for i in range(1000000):
        b.test = None

def test_setter2():
    class a:
        pass

    b = a()

    b.test = None
    for i in range(1000000):
        if b.test:
            b.test = None
