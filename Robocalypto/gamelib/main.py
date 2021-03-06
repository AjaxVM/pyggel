#! /usr/bin/env python

import sys, os

import pyggel
from pyggel import *

import game

def main():
    
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pyggel.view.init([800, 600])
    g = game.Game()
    g.run()
    pyggel.quit()

if __name__ == "__main__":
    main()
