"""
pyggel.geometry
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The geometry module contains classes used to render 3d geometric primitives.
"""

from include import *
import view, data, misc
from data import Texture, BlankTexture
from scene import BaseSceneObject


class Cube(BaseSceneObject):
    """A geometric cube that can be colored and textured"""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, mirror=True,
                 hide_faces=[]):
        """Create a cube
           size is the absolute size of the cube
           pos is the position of the cube
           rotation is the rotation of the cube
           colorize is the color of the cube (0-1 RGBA)
           texture can be None, a data.Texture object or a string representing the filename of a texture to load
           mirror indicates whether each face of the cube has the full texture on it (so each is identicle) or
               if True, each face will have the entire texture mapped to it
               if False, the Texture is considered a cube map, like this:
                   blank, blank, top, blank,
                   back, left, front, right,
                   blank, blank, bottom, blank
           hide_faces must be a list of the sides of the cube not to add:
               acceptable values are left, right, top, bottom, back, front"""
        BaseSceneObject.__init__(self)

        self.hide_faces = hide_faces

        self.size = size
        self.pos = pos
        self.rotation = rotation
        if type(texture) is type(""):
            texture = Texture(texture)
        if texture:
            self.texture = texture
        else:
            self.texture = BlankTexture()
        self.colorize = colorize

        self.mirror = mirror

        self.corners = ((-1, -1, 1),#topleftfront
                      (1, -1, 1),#toprightfront
                      (1, 1, 1),#bottomrightfront
                      (-1, 1, 1),#bottomleftfront
                      (-1, -1, -1),#topleftback
                      (1, -1, -1),#toprightback
                      (1, 1, -1),#bottomrightback
                      (-1, 1, -1))#bottomleftback

        sides = ((7,4,0,3, 2, 2, 5),#left
                      (2,1,5,6, 3, 4, 4),#right
                      (7,3,2,6, 5, 0, 3),#top
                      (0,4,5,1, 4, 5, 2),#bottom
                      (3,0,1,2, 0, 1, 0),#front
                      (6,5,4,7, 1, 3, 1))#back
        self.sides = []
        if not "left" in hide_faces:
            self.sides.append(sides[0])
        if not "right" in hide_faces:
            self.sides.append(sides[1])
        if not "top" in hide_faces:
            self.sides.append(sides[2])
        if not "bottom" in hide_faces:
            self.sides.append(sides[3])
        if not "front" in hide_faces:
            self.sides.append(sides[4])
        if not "back" in hide_faces:
            self.sides.append(sides[5])
        self.normals = ((0, 0, 1), #front
                        (0, 0, -1), #back
                        (0, -1, 0), #top
                        (0, 1, 0), #bottom
                        (1, 0, 0), #right
                        (-1, 0, 0)) #left

        self.split_coords = ((2,2),#top
                             (0,1),#back
                             (1,1),#left
                             (2,1),#front
                             (3,1),#right
                             (2,0))#bottom

        self.scale = 1

        self.display_list = data.DisplayList()

        self._compile()

    def get_dimensions(self):
        """Return a tuple of the size of the cube - to be used by the quad tree and collision testing"""
        return self.size, self.size, self.size

    def get_pos(self):
        """Return the position of the quad"""
        return self.pos

    def _compile(self):
        """Compile the cube's rendering into a data.DisplayList"""
        self.display_list.begin()

        ox = .25
        oy = .33
        last_tex = None

        glBegin(GL_QUADS)
        for i in self.sides:
            ix = 0
            x, y = self.split_coords[i[5]]
            x *= ox
            y *= oy
            if self.mirror:
                coords = ((1,1), (1,0), (0,0), (0,1))
            else:
                coords = ((x+ox, y+oy), (x+ox, y), (x, y), (x, y+oy))

            glNormal3f(*self.normals[i[6]])

            for x in i[:4]:
                glTexCoord2fv(coords[ix])
                a, b, c = self.corners[x]
                glVertex3f(a,b,c)
                ix += 1
        glEnd()
        self.display_list.end()

    def render(self, camera=None):
        """Render the cube
           camera is None or the camera object the scene is using to render this object"""
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glScalef(.5*self.size,.5*self.size,.5*self.size)
        try:
            if not self.scale == (1,1,1):
                glScalef(*self.scale)
        except:
            if not self.scale == 1:
                glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size)
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        """Return a copy of the quad - uses the same display list"""
        n = Cube(self.size, self.pos, self.rotation, self.colorize, self.texture, self.mirror, self.hide_faces)
        n.display_list = self.display_list
        n.scale = self.scale
        return n

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

class Quad(Cube, BaseSceneObject):
    """A simple 3d square object."""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, hide_faces=[]):
        """Create the Quad
           size is the quad
           pos is the position of the quad
           rotation is the rotation of the quad
           colorize is the color of the quad
           texture can be None, a string filename of an image to load or a data.Texture object - entire texture is mapped to the face
           hide_faces are the same as for Cube, except only front and back are allowed"""

        BaseSceneObject.__init__(self)
        self.size = size
        self.pos = pos
        self.rotation = rotation
        if type(texture) is type(""):
            texture = Texture(texture)
        if texture:
            self.texture = texture
        else:
            self.texture = BlankTexture()
        self.colorize = colorize

        self.scale = 1

        self.display_list = data.DisplayList()

        self.hide_faces = hide_faces

        self._compile()

    def _compile(self):
        """Compile the Quad into a data.DisplayList"""
        self.display_list.begin()

        glBegin(GL_QUADS)
        glNormal3f(0,1,0)
        if not "back" in self.hide_faces:
            glTexCoord2f(1,1)
            glVertex3f(-1,1,0)
            glTexCoord2f(0,1)
            glVertex3f(1, 1, 0)
            glTexCoord2f(0,0)
            glVertex3f(1, -1, 0)
            glTexCoord2f(1,0)
            glVertex3f(-1, -1, 0)
        if not "front" in self.hide_faces:
            glTexCoord2f(1,0)
            glVertex3f(-1, -1, 0)
            glTexCoord2f(0,0)
            glVertex3f(1, -1, 0)
            glTexCoord2f(0,1)
            glVertex3f(1, 1, 0)
            glTexCoord2f(1,1)
            glVertex3f(-1, 1, 0)
        glEnd()
        self.display_list.end()

    def copy(self):
        """Return a copy of the Quad, sharing the same display list"""
        n = Quad(self.size, self.pos, self.rotation, self.colorize, self.texture)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

    def render(self, camera=None):
        """Render the Quad
           camera is None or the camera object the scene is using to render this object"""
        Cube.render(self, camera)

class Plane(Quad):
    """Like a Quad, except the texture is tiled on the face, which increases performance over a lot of quads tiled"""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, tile=1, hide_faces=[]):
        """Create the Plane
           size of the plane
           pos is the position of the quad
           rotation is the rotation of the quad
           colorize is the color of the quad
           texture can be None, a string filename of an image to load or a data.Texture object - entire texture is mapped to the face
           tile is the number of times to tile the texture across the Plane,
           hide_faces are the same as for a Quad"""

        self.tile = tile

        Quad.__init__(self, size, pos, rotation, colorize, texture, hide_faces)

    def _compile(self):
        """Compile Plane into a data.DisplayList"""
        self.display_list.begin()

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_REPEAT)

        glBegin(GL_QUADS)
        glNormal3f(0,1,0)
        if not "back" in self.hide_faces:
            glTexCoord2f(self.tile,0)
            glVertex3f(-1,1,0)
            glTexCoord2f(0,0)
            glVertex3f(1, 1, 0)
            glTexCoord2f(0,self.tile)
            glVertex3f(1, -1, -0)
            glTexCoord2f(self.tile,self.tile)
            glVertex3f(-1, -1, -0)
        if not "front" in self.hide_faces:
            glTexCoord2f(self.tile,self.tile)
            glVertex3f(-1, -1, -0)
            glTexCoord2f(0, self.tile)
            glVertex3f(1, -1, -0)
            glTexCoord2f(0,0)
            glVertex3f(1, 1, 0)
            glTexCoord2f(self.tile, 0)
            glVertex3f(-1,1,0)
        glEnd()
        self.display_list.end()

    def render(self, camera=None):
        """Render the Plane
           camera is None or the camera object the scene is using to render this object"""
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        s = self.size / self.tile if (self.size and self.tile) else self.size
        glScalef(.5*self.size,.5*self.size,.5*self.size)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.texture.bind()
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        """Return a copy of the Plane - sharing the same display list..."""
        n = Plane(self.size, self.pos, self.rotation, self.colorize, self.texture, self.tile)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

class Skybox(Cube):
    """A skybox object, which basically creates an infinitly far-away box, where all rendering is inside.
       Used to simulate a sky, or other things where you want to fill the view with something other than a blank color"""
    def __init__(self, texture, colorize=(1,1,1,1)):
        """Create the Skybox
           texture can be the same as a Cube, None, data.Texture, string filename or  list of 6 data.Texture objects
           colorize - the color of the Skybox"""
        Cube.__init__(self, 1, colorize=colorize, texture=texture, mirror=False)
        self._compile()

    def render(self, camera):
        """Render the Skybox
           camera is the camera object the scene is using to render the Skybox"""
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        gb_cull = glGetBooleanv(GL_CULL_FACE)
        glDisable(GL_CULL_FACE)

        glPushMatrix()
        camera.set_skybox_data()
        Cube.render(self)
        glPopMatrix()
        glDepthMask(GL_TRUE)
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        if gb_cull:
            glEnable(GL_CULL_FACE)

    def copy(self):
        """Return a copy of the Skybox - sharing the same data.DisplayList"""
        n = Skybox(self.texture, self.colorize)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

class Sphere(BaseSceneObject):
    """A geometric Sphere object that can be colored and textured"""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, detail=30):
        """Create the Sphere
           size is the radius of the Sphere
           pos ithe position of the sphere
           rotation is the rotation of the sphere
           colorize is the color of the sphere
           texture can be None, a string filename of an image to load or a data.Texture object that will be mapped to the sphere
           detail is the level of detail for the Sphere, higher = a more smooth sphere"""
        BaseSceneObject.__init__(self)

        self.size = size
        self.pos = pos
        self.rotation = rotation
        self.colorize = colorize
        if type(texture) is type(""):
            texture = Texture(texture)
        if texture:
            self.texture = texture
        else:
            self.texture = BlankTexture()
        self.detail = detail
        self.scale = 1

        self.display_list = data.DisplayList()

        self._compile()

    def get_dimensions(self):
        """Return a three part tuple of the radius of the sphere - used in teh quadtree and collision testing"""
        return self.size, self.size, self.size

    def get_pos(self):
        """Return the position of the sphere"""
        return self.pos

    def _compile(self):
        """Compile the Sphere into a data.DisplayList"""
        self.display_list.begin()
        #Pyweek change - set rotation for faces to be correct!
        glRotatef(-90,1,0,0)
        Sphere = gluNewQuadric()
        gluQuadricTexture(Sphere, GLU_TRUE)
        gluSphere(Sphere, 1, self.detail, self.detail)
        self.display_list.end()

    def render(self, camera=None):
        """Render the Sphere
           camera can be None or the camera object the scene is using"""
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glScalef(self.size, self.size, self.size)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size)
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        """Return a copy of the Sphere - sharing the same display list"""
        n = Sphere(self.size, self.pos, self.colorize, self.texture, self.detail)
        n.scale = self.scale
        n.display_list = self.display_list
        return n

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

class Skyball(Sphere):
    """A Skyball is like a Skybox - except it is a sphere intead of a cube"""
    def __init__(self, texture=None, colorize=(1,1,1,1), detail=30):
        """Create the Skyball
           texture can be None, a string filename or the data.Texture object to map to the Sphere"""
        Sphere.__init__(self, 1, colorize=colorize,
                        texture=texture, detail=detail)

    def render(self, camera):
        """Render the Skyball
           camera is the camera the scene is using"""
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        gb_cull = glGetBooleanv(GL_CULL_FACE)
        glDisable(GL_CULL_FACE)

        glPushMatrix()
        camera.set_skybox_data()
        glRotatef(-90, 1, 0, 0)
        Sphere.render(self)
        glPopMatrix()
        glDepthMask(GL_TRUE)
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        if gb_cull:
            glEnable(GL_CULL_FACE)

    def copy(self):
        """Return a copy of teh Skyball - sharing the same dadta.DisplayList"""
        n = Skyball(self.texture, self.colorize, self.detail)
        n.scale = self.scale
        n.display_list = self.display_list
        return n


#Pyweek changes:
import math3d, math
class Pyramid(BaseSceneObject):
    """A geometric pyramid that can be colored and textured"""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, hide_faces=[]):
        BaseSceneObject.__init__(self)

        self.hide_faces = hide_faces

        self.size = size
        self.pos = pos
        self.rotation = rotation
        if type(texture) is type(""):
            texture = Texture(texture)
        if texture:
            self.texture = texture
        else:
            self.texture = BlankTexture()
        self.colorize = colorize

        self.scale = 1

        self.display_list = data.DisplayList()

        self._compile()

    def _compile(self):
        """Compile the cube's rendering into a data.DisplayList"""
        self.display_list.begin()

        top = (0,0.5,0)
        bottomleft = (-math.sqrt(3)*0.25,-0.5,0.25)
        bottomright = (math.sqrt(3)*0.25,-0.5,0.25)
        bottomback = (0,-0.5,-0.5)

        tpoints = [[bottomleft,bottomright,bottomback],
                   [top, bottomleft, bottomright],
                   [top, bottomright, bottomback],
                   [top, bottomback, bottomleft]]

        ttp = []
        if not "bottom" in self.hide_faces:
            ttp.append(tpoints[0])
        if not "front" in self.hide_faces:
            ttp.append(tpoints[1])
        if not "right" in self.hide_faces:
            ttp.append(tpoints[2])
        if not "left" in self.hide_faces:
            ttp.append(tpoints[3])

        glBegin(GL_TRIANGLES)
        for i in ttp:
            coords = ((0.5,1), (0,0), (1,0))

            glNormal3f(*math3d.calcTriNormal(i[0],i[1],i[2],False))

            for p in xrange(3):
                glTexCoord2fv(coords[p])
                glVertex3f(*i[p])
        glEnd()

        self.display_list.end()

    def render(self, camera=None):
        """Render the cube
           camera is None or the camera object the scene is using to render this object"""
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        glScalef(self.size,self.size,self.size)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.texture.bind()
        if self.outline:
            misc.outline(self.display_list, self.outline_color, self.outline_size)
        self.display_list.render()
        glPopMatrix()

class DoublePyramid(Pyramid):
    """A geometric double-pyramid that can be colored and textured"""
    def __init__(self, size, pos=(0,0,0), rotation=(0,0,0),
                 colorize=(1,1,1,1), texture=None, hide_faces=[]):
        Pyramid.__init__(self, size, pos, rotation, colorize, texture, hide_faces)

    def _compile(self):
        """Compile the cube's rendering into a data.DisplayList"""
        self.display_list.begin()

        top = (0,0.5,0)
        bottom = (0,-0.5,0)
        midleft = (-math.sqrt(3)*0.25,0,0.25)
        midright = (math.sqrt(3)*0.25,0,0.25)
        midback = (0,0,-0.5)

        tpoints = [[top, midleft, midright],
                   [top, midright, midback],
                   [top, midback, midleft],

                   [bottom,midright,midleft],
                   [bottom,midleft,midback],
                   [bottom,midback,midright]]
        ttp = []
        if not "topfront" in self.hide_faces:
            ttp.append(tpoints[0])
        if not "topright" in self.hide_faces:
            ttp.append(tpoints[1])
        if not "topleft" in self.hide_faces:
            ttp.append(tpoints[2])

        if not "bottomfront" in self.hide_faces:
            ttp.append(tpoints[3])
        if not "bottomright" in self.hide_faces:
            ttp.append(tpoints[4])
        if not "bottomleft" in self.hide_faces:
            ttp.append(tpoints[5])

        glBegin(GL_TRIANGLES)
        for i in ttp:
            coords = ((0.5,1), (0,0), (1,0))

            glNormal3f(*math3d.calcTriNormal(i[0],i[1],i[2],False))

            for p in xrange(3):
                glTexCoord2fv(coords[p])
                glVertex3f(*i[p])
        glEnd()

        self.display_list.end()
