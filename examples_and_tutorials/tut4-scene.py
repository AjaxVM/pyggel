"""tut4-scene.py

This tutorial introduces the scene object and basic usage"""

import _set_path #this just makes sure we grab pyggel/data directories - so if we are running from the install directory it still works ;)

import pyggel
from pyggel import *

def main():
    pyggel.init(screen_size=(640,480)) #initialize everything
    #for now, pyggel.init just calls pyggel.view init...

    event_handler = pyggel.event.Handler()

    """Scenes, in PYGGEL control the rendering, updating and picking of 2d and 3d objects in an application.
       There are numerous things you need to pay attention with in the scene object, because it controls so many things,
       many of these things can't be addressed in a single tutorial, so they will be spread over a few,
       but for now here is a reference to them:
           objects:
               objects are added to the scene based on their type, which determines the OpenGL settings when rendered.
               Each type of object has an associated add_type/remove_type method, to add/remove objects from the scene.
               The types of objects are:
                   2d - renders last, on top of any 3d elements, no lighting/depth testing etc. blending on
                   3d - basic 3d object, no blending (but alpha testing is allowed), depth testing on
                   3d_blend - same as plain 3d, except blending is on
                   3d_always - same as 3d_blend, except depth testing is turned off
               Generally any object can be added to any of these groups - but they won't always look right.
               A general rule is that any object followed with a 3D should *always* go in one of the 3d containers,
               anything with 2D should always go into 2d, and anything else depends on the object - but it should be pretty obvious,
               ie, mesh.OBJ/BasicMesh should always go in 3d simply becaus you don't need 3d meshes in 2d
               (generally speaking, you'd have to hack a bit to make it work...)
           skyboxes:
               skyboxes are "background" objects that are rendered before everything else, to gives the appearance of an infinite world.
               to add a skybox simply call scene.add_skybox(skybox) - if skybox is None it removes the skybox.
               Objects that you can use for the sckybox are geometry.Skybox, geometry.Skyball and None
           lights:
               Almost every scene needs them. Scenes may have up to 8 lights attached to them at any time.
               To add/remove a light simply call scene.add_light(light)/scene.remove_light(light).
               Acceptable light objects are pyggel.light.Light objects, only.

           rendering:
               Ok, here is the main point of the scene - to efficiently and accurately render all your objects.
               To render you simply call scene.render() - render takes an optional argument to pass a camera to use to render.
           picking:
               Now here is the other main function of the scene - to pick objects, ie, to figure out which object the mouse is hitting.
               picking is integrated into the rendering loop, so setting it up is quite simple:
                   scene.pick = True #this tells the render method to also pick while it runs
                   picked_object = scene.render() #when you call render, the return object will be None or the picked object.
               And that is all there is to it.

       Alright. Now that you know what a scene is and what it does, let's make one!"""
    scene = pyggel.scene.Scene()

    clock = pygame.time.Clock() #pyggel automatically imports OpenGL/Pygame
                                #for a full list of everything included,
                                #look in pyggel/include.py

    while 1:
        clock.tick(60) #limit FPS
        pyggel.view.set_title("FPS: %s"%int(clock.get_fps()))

        event_handler.update() #get the events!

        if event_handler.quit or K_ESCAPE in event_handler.keyboard.hit: #were the quit 'X' box on the window or teh ESCAPE key hit?
           pyggel.quit() #close the window and clean up everything
           return None #close the loop

        pyggel.view.clear_screen() #clear screen for new drawing...
        item = scene.render() #render the scene, also, see if anything was picked
        if item and item.hit: #see if anything was picked
            print "something hit! But since we have nothing in the scene this will never be called O.o"
        pyggel.view.refresh_screen() #flip the display buffer so anything drawn now appears

main()
