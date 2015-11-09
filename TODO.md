## Future ##
  * Look into using compiled parts for optimizations (Cython, Pyrex, etc....)
  * add shader support

## Version 0.1-beta1 "stability" -- 0% ##
  * ferret out as many bugs as possible
  * test on as many platforms as possible
  * build python install script #low priority
  * finish writing nice doc-strings, tutorials, and an API reference manual.
  * Write a "Making a fast 3d game in PYGGEL" document, explaining some of the ways to make a PYGGEL game go faster... Such as StaticObjectGroups, VertexArray vs. Image3D particle effects, multiple "transitional" scenes - instead of one monster scene, etc.
  * Ensure API is consistent, guessable and intelligent...
  * Add some kind of shadow system!!!
  * implement Cal3D models #low
  * implement ODE (for at least collisions, but go for fully...) #medium
  * Add 3d sound module using pygame, OpenAL or pymedia #medium-low PyMedia seems best...

## Version 0.09-alpha5 "speed" -- 10% planning ##
  * VBO support #DONE!
  * scene transitions (fade in/out, swirly in/out, etc.)
  * ext module for generating static data good for stuffing into VBO's
  * profile engine and optimize bottlenecks...
  * texture packer and subimaging, for use primarily in ext VBO objects
  * handle GUI image data faster (instead of rebuilding each image for each widget, scale with opengl where needed from singleton)

## Version 0.08-alpha4 "features" -- 100% Released ##
  * look into creating a color picker and testing speed trade-offs... #DONE! replaced with during-render picker
  * implement FrameBuffer objects #DONE!
  * Splitting the view among viewports - and having Ortho match... #DONE! not going to do precisely, can fake with frame buffers and such now...
  * Write some doc-strings, a few more tutorials... #DONE!
  * Make Image/Image3D and Texture only bind if not current texture. Move texture binding out of display lists so you can actually check this - particles at least will be much faster... #DONE!
  * Remove and replace all data assets we didn't make ourselves, the gifs, the obj meshes, etc. #DONE!
  * Make sure all objects are rendering clock wise (or is it CCW?) so we can enable backface culling and some kind of shadows... #DONE! and was CCW :P
  * integrate Animator.py mesh class(es) into mesh.py, replacing the current ones #Done!
  * implement some form of testing for CW/CCW ordering of vertices #Done!
  * implement Frame based and interpolation based OBJ animator classes #Done!


## Version 0.07-alpha3 "features and stability" -- 100% Released! ##
  * Add a "scaletowindow" attribute to all 2d things - basically, use code to place things at optimum size (eg, 640, 480) and if the window is changed to like (800, 600) then the images and such are scaled and mouse events are scaled - so the code stays the same... #DONE! added equivalent functionality
  * Write a new input API - allowing seamless integration with the gui, but also giving some more/faster ways to look up the state of input devices... #Done!
  * Add a 2d gui! #Done! just need docs!
  * implement animated 2d images - sprite sheets, "gif's"?, multiple images, etc. #DONE!
  * add support for custom cursors through the view... #DONE!


## Version 0.06-alpha2 "speed" -- 100% Released! ##
  * Allow each scene to have eight lights, and have them generate automatically - instead of only 8 global lights... #DONE!
  * Add AABox, Sphere and QuadTree objects into PYGGEL - added to objects and the scene... #Done - Quad/Oct Tree's too slow...
  * Instead of a Quad/Oct Tree, use a "hash tree" - a dict of nodes #DONE!
  * use Sphere bounding volumes to perform frustum culling on all objects #Not happening, either as true frustum use, or with a SpaceTree object...
  * Add subImage rendering for 2D - ie, a lot of images in one, only rendering a part though... #Done!
  * Look into porting to use pyglet #Done - not porting
  * Look into adding support for VertexBuffer objects (in addition to the VertexArrays) #Sort of done - created a test, not any faster as far as I can tell, and I can't get them to display or correctly or update without recreation - so not much use. Perhaps will revisit at a later time.
  * Test new collision detection and partition culling features! #Failed, miserably, a lot of the functionality wasn't correctly implemented, and to get it working causes the code to become far to complicated, both the source and the API-usage - all features removed (VolumeStore, SpaceTree's, etc.)


## Version 0.05-alpha1 "start" -- 100% -- Released! ##
  * Toggling of display settings #Done!
  * Image2D/Image3D #Done!
  * OBJ mesh loading #Done!
  * Geometry classes #Done - ongoing (if/when we need more types)
  * Texture, DisplayList and VertexArray #Done!
  * Particle effects #Done!
  * Picking #Done - only select buffer picking for now - save color buffer picking for next release (if any...)
  * Camera class objects: Third-person, First-person #Done!
  * math3d class with Vector, Sphere and AABox features (among other standard 3d functions) #Done! (math functions ongoing...)
  * Font support #Done!