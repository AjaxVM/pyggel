# Introduction #

Here is a list of the features and capabilities that are planned for PYGGEL...


# Overview #
PYGGEL is planned to be a general 3d game library/engine for Python.
The main features of it will be a 3d tile engine, gui and a networking library.

# 3d (opengl) stuff #
  * picking #done
  * shadows
  * animated models
  * camera class (keeps track of position/rotation, renders objects hidden by others, etc.) #done - though more accurate representation of absolute pos of LookAtCamera would be nice...

# 3d (functional) stuff #
  * Collision detection (line, ray, sphere, cube, polygon)
  * Cached A**(generates once, and then updated when new stuff happens, like an obstacle
is placed of something. Can include active objects - like units - bu not by default)**


# input stuff #
Everything flows through the gui - basically there is an app class always run, so even if you have no widgets active it still goes through the gui.
Events are returned like pygame and pyglibs.gui

# scene core #
  * tile based, but free-form (anything inside the tiles) map engine
  * multiple kinds of objects



And that is the gist of it for now!