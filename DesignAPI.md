# Note #
This page is outdated - it was the original "target" api for a version of pyggel intended to be more of a 3d tile engine.
It is no longer a goal to match this api, or to include all features listed here, but the page is kept because there are some features I don't want to forget LOL

# Introduction #
This is the API we currently are working towards, will change once we start breaking ground on the code.


# Details #

```
#importing

import pyggel



#inititiating

pyggel.view.init(screen_size)


#fullscreen

pyggel.view.set_fullscreen(True) #or false

pyggel.view.toggle_fullscreen()


#hardware rendering...

pyggel.view.set_hardware_render(True) #or false

pyggel.view.toggle_hardware_render()


#Various other settings handled same way


#enable shadow

pyggel.view.set_shadows(True) #or false

pyggel.view.toggle_shadows()


#how to set shadows for different object types (explained farther down)

pyggel.view.set_shadow_for_map(False) #whether the map can cast shadows... Only if set_shadows is True

pyggel.view.set_shadow_for_static_objects(False) #whether static objects cast shadows

pyggel.view.set_shadow_for_active_objects(False) #whether active objects cast shadows

pyggel.view.set_shadow_for_projectile_objects(False) #whether projectiles cast shadows

pyggel.view.set_shadow_for_nologic_object(False) #whether NoLogic objects cast shadows


#creating a scene

my_scene = pyggel.Scene()


#setting fill color

my_scene.color_fill(r, g, b) #no alpha for this!

#setting background image

my_scene.background_image("filename.png")


#rendering scene (note this will automatically clear the view

my_scene.render() #this will render anything at all in the scene


#setting the screen map

#from a file

my_scene.set_map(pyggel.map.from_file("map_file.txt"))

#from a construct

construct = pyggel.map.Construct(size, cell_size=(1,1))

new_tile_type = pyggel.map.TileType(image="filename.png", name="grass")

construct.add_tile_type(new_tile_type)

for x in xrange(10):

	for z in xrange(10):

		y = 0

		construct.set_cell((x, y, z), "grass", smooth_transition=False, height=1)

					#this basically fills the grid with grass.

					#x, y, z are the coordinates of the cell (Note, you can stack cells in the y axis!

					#smooth transition basically will make it so that if the surrounding objects

					#are not at the same height, and they are within

					#height is how tall the tile is - note, top of object is y pos, bottom y - height

my_scene.set_map(construct)


#Adding a static object (a house or something) to the scene

obj = pyggel.objects.StaticObject(model, pos, rotation=(0,0,0), snap_to_map=True) #this creates a new static object.

				#model is the filename (or model object) of the model this object

				#will use, note, the engine automatically caches loading of files

				#that are loaded, thus if you want a model that is unique

				#you will need to do a pyggel.model.LoadUnique(filename)

				#pos is the 3d position of the model (cellx, celly, x, y, z) the cell positions

				#are the position in the scenes grid this object is in, the x, y, z values are the

				#positions inside the cell this object is (-1 to 1 for x and z, any value for y)

				#rotation is the x, y, z rotation of the object.

				#snap_to_map will set the y position of the object to match the center of the closest

				#grid cell that is *under* the object, unless it is under all,

				#then it sets it to the closest cell above the object.

				#A note now so I dont forget later - pos = the (x, z) 
center of the object and the (y)

				#bottom of the object, ie the feet.

my_scene.add_object(obj, somename=None) #add the object to the scene. somename is a variable that if set can be used

					#to get access to the object later, otherwise you will need to keep track

					#of the obj variable itself.


#Adding an active object (a character) to the scene

obj = pyggel.objects.ActiveObject(model, pos, can_fly=False, speed=0.1) #create an active object.

				#model, and are the same as for static models (snap_to_map is assumed and no rotation!)

				#can_fly indicates whether the object can fly or not - basically, if

				#it can fly, and set_flying(True) is called, then the object will be allowed to move in the

				#y axis - basically height. A* will now only be used to see if the object should

				#fly over/under the other object - which can be set to be handled automagically,

				#or by the user...

				#speed is how fast the obj will move across a tile, ie, 0.1 will move the unit from one

				#end of a tile to the other in 20 frames (-1 pos to +1 pos)

my_scene.add_object(obj, somename=None)



#Adding a projectile object (a bullet or arrow) to the scene

obj = pyggel.objects.ProjectileObject(model, startpos, goto, arc=None, speed=0.1) #create object

				#model is the model of the object

				#startpos is the position (cellx, celly)(x, y, z) the object starts at

				#endpos is the position (cellx, celly)(x, y, z) the object will end at

				#arc is the amount of arcing the object will do to get where it is going, or None

				#speed is how fast the object moves

				#This object will "die" if it hits a map tile or an object

my_scene.add_object(obj, somename=None)



#Adding a NoLogic object (small plant, etc.) to the scene

#Basically, a NoLogic object is an object that is merely rendered into the scene,

#but does not interact with anything else at all

obj = pyggel.objects.NoLogicObject(model, pos, rotation, snap_to_map=False) #create object, you know the rest

my_scene.add_object(obj, somename=None)


#Handling an object

obj = my_scene.objects.by_name(somename) #get the object from the scene

obj = someObj #or get it from wherever you stored it yourself

obj.move(x, z) #there is no y control here, as that is handled by jumping or flying.

	       #object is snapped to grid after moving

	       #if the object cannot move to the new location (either the new tile is not smooth,

	       #it is more than 1 height higher than the current location, or there is a static objbect this one would

	       #collide with) then the object is not moved, and False is returned, otherwise it is True

	       #will also disallow movement off the map

obj.moveto((cellx, celly), (x, y)) #attempts to move to the new location, if a path is not pound then False is returned,

				   #else, True is returned.

				   #will always return True, and move in a straight line to the new location, if

			  	   #pathfinding is not enabled!

obj.moving() #returns whether the object is currently moving or not

obj.set_flying(True, new_height) #tells the object to start flying, and moves it to the new height

obj.need_adjust_flying_height() #returns (True, top, bottom) if the object is flying and it needs to change height to go

				#over/under an obstacle - top and bottom are the heights of the top/bottom of the obstacle

obj.set_speed(new_speed) #sets the objects new speed. Original is cached so you can:

obj.return_speed() #set the speed back to the original value - this is good for slow or hasten attributes

obj.collide(other) #determines if the object is colliding with another (using sphere, cube and polygon testing)

obj.distance(other) #determine the distance between the two objects

obj.rotate(x, y, z) #this will be overridden if object is told to move, so that it is facing the destination

obj.delete() #remove the object from the scene, this works for all objects

obj.set_pos((x,y,z) #changes the object position to the new

obj.set_rotation((x,y,z)) #will be overridden by moving object


#NoLogic objects do not have set_flying, need_adjust_flying_height or collide methods


#Handling a projectile

obj = my_scene.objects.by_name(somename)

obj = someObj

obj.dead() #returns (True, objectOrMapGridLocation) if it has collided with anything and died, or None.

	   #Note, this automatically removes the object from the scene if it returns True!

obj.set_pos((x,y,z)) #this changes the current position of the projectile - but not the goto position

obj.set_goto((x,y,z)) #changes the goto position

obj.resurrect() #if the object was killed, recreate it at the position it was, and readd to scene

		#if this is done, you must change either the pos and/or goto so that it does not die immediately again!

obj.rewind() #undoes the last move of the projectile - ie, it got killed, you resurrect, you want it to move back at least!



#enabling A* pathfinding in the scene

my_scene.set_pathfinding(True) #this is the normal one - if there is a static object in the cell, it is invalid

my_scene.set_careful_pathfinding(True) #this is a slower but more precise method, checks for path inside each cell as

				       #well as over the entire grid,

				       #it also supports overlapping of objects on multiple grid cells.

				       #NOTE: This will disable normal A*, just as enabling normal will disable this.

my_scene.enable_path_caching(True) #this makes the scene cache a path from each point to another - if any new static

				   #objects are added - it recalculates any path that collided...



#Controlling collisions

pyggel.collisions.set_polygon_detail(number=None) #tells the collision code that when a scene object creates a

						 #collision object, it will weed out polygon points til there are no more

						 #than number, by continually iterating through the points and removing

						 #every other one. Also will move the two points on either side of the

						 #removal closer to the removed point.

						 #if number is None, then no cutting down on points occurs

						 #Note, if any object is created, and this is changed, then the objects

						 #created before the change will remain unaffected.

pyggel.collisions.apply_polygon_detail_changes() #this will reset all object collision polygons to be changed to fit the

						 #last detail change - basically override last line of above comments

pyggel.collisions.set_fuzzy(0) #basically set the amount of overlapping allowed in map/staticObject object moving collision

			       #testing... 0 turns off...



#loading images

image = pyggel.image.load("name.png") #this caches the load for unique do:

image = pyggel.image.load_unique("name.png")

#Images have opengl textures associated with them, and support blitting to, cropping, resizing, etc.

#handling images

image.blit(other, (x, y)) #puts the pixels from other image to this image using (x,y) offset - uses Pygame

image.resize(size) #scales image to new size - uses PIL

image.rotate(amount) #uses PIL or Pygame to rotate that image around the z axis by amount

image.bind() #binds the images GL texture so primitives can use it

image.render(scene, (x, y, z)) #renders the object at x,y,z - opengl coords - to the scene

image.project(scene, (x, y, z)) #renders the object at x,y,z in relation to the

				#screen view (ie, as if the camera has not moved)

image.colorize(matrix) #colorizes the image using PIL - there should be some default matrices you can use

image.replace_colorize(old_color, new_color, threshold=1) #changes any pixels within threshold of old_color in image to

							  #new color - uses Pygame or PIL
image.set_rotation((x,y,z))



#Rendering primitives to the screen

#basic rendering (basically just calls OpenGL rendering calls, nothing else)

obj = pyggel.draw.Primitive(type, args, kwargs) #create a draw object

	#type can be any of (line, lines, triangle, quad, polygon, circle, sphere, cylinder)

	#args are different for each type, but for line they are:

	#	start_point=(x,y,z), end_point=(x,y,z), start_color=(r,g,b,a), end_color=(r,g,b,a)

	#for lines, triangle, quad and polygon you have:

	#	points=((x,y,z)*points), colors=((r,g,b,a)*points), image=None, tex_coords=((x,y)*points))

	#	colors can be only one color, if so it will apply to all points

	#	image must be None or a pyggel.image.Image object (object after loading)

	#	tex_coords must be None or a list of (x,y) points for each point in the object for texture coords

	#		if None and image is set, then will use whole image,

	#		but assume the coords are the edges of the image...

	#for circle and sphere they are:

	#	pos = (x, y, z), radius=1, color=(r,g,b,a), image=None) #no tex_coord setting, or multiple colors

	#for cylinder they are:

	#	pos = (x,y,z), radius=1, height=1, color=(r,g,b,a),image=None)

my_scene.add_primitive(obj, somename=None) #add to scene



#"projection" rendering (basically, rendering the primitive where you place it on screen regardless of camera pos)


obj = pyggel.draw.Projection(type, args, kwargs) #same as above just about

my_scene.add_primitive(obj, somename=None)


#controlling render primitives

obj = my_scene.primitives.by_name(somename) #if you gave it a name, otherwise keep track of it yourself

obj = someObj

obj.move((x, y, z)) #move the object (ie all points and or the exact pos)

obj.rotate((x, y, z)) #rotate the primitive around it's center position

obj.change_color(color_or_colors) #change the point-by-point or all colors

obj.change_image(image) #change the image to use

obj.change_tex_coords(new) #oy vey - is this really necessary? Not hard to implement I guess, but sheesh...

obj.set_pos((x, y, z))

obj.set_rotation((x, y, z))



#Rendering text

font = pyggel.text.Font(name=None, size=20) #create a font object

text = pyggel.text.Text2d(font, "Some text") #2d text is always rendered as a projection!

text.render(scene, pos=(0,0))

#text can be formatted, with default color being (255, 255, 255, 255)

#formatting works in tags, tags are:

#	<i> - italic

	<b> - bold

	<u> - underline

	<c r g b a> - color (r, g, b, a)



#you can also do 3d text...

text = pyggel.text.Text3d(font, "3D text...")

text.render(scene, pos=(0,0,0)) #this will actually render to the world tile pos you give...



#Manipulating camera

camera = my_scene.camera() #this creates a camera controller class - Note - only one camera can be active for a scene

			   #mainly because it is easier to implement - but why would we need another camera anyways?

			   #a hotseat racing sim? Which really isn't what this would be intended for...

camera.move((x, y, z)) #move the view

camera.rotate_ip((x, y, z)) #rotates the view stationarily, in place - the position doesn't change

camera.rotate((x, y, z)) #moves the camera around where it is pointing at (basically regular rotation...)

camera.set_pos((x, y, z)) #just set the dang position!

camera.set_rotation((x,y,z), ip=(x,y,z)) #sets the rotation to the first arg, and the ip rotation by the second



#manipulating lights

light = pyggel.light.Light(pos, directional=False, color=(r,g,b,a), etc...) Create a new light Object...

my_scene.add_light(light, somename=None) #blah blah blah

light.turn_on(priority=False, main=False) #this will turn on the light. Priority is a simple flag for your lights.

			#basically, because opengl only support 8 lights, you have to disable some to add more

			#Thus, if there are too many lights, it will pick the light farthest away that

			#is not priority to disable. Otherwse, if all are priority - it will pick the farthest away

			#that is not a main light.

			#So, like, a Sun would be a main light, an overhead lamp a priority, and a candle nothing.

light.turn_off() #turn it off - when turned off, this will turn on the next closest or priority light (if any)

		 #that was turned off to allow this one, assuming it was actually enabled at the time


pyggel.light.TurnOffAll() #turn off all lights currently in use regardless of distance

pyggel.light.TurnOnAll() #turn everything on - only the 8 closest priority or main lights are turned on

x = pyggel.light.GetAll() #returns a list of all light objects created


#manipulating gui/input

#This is a long part I will get to later
```