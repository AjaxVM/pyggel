"""
pyggle.mesh
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The mesh module contains mesh classes for different kinds of meshes, as well as loaders for various kinds of meshes.
"""

from include import *
import os
import image, view, misc, data
 
def OBJ(filename, swapyz=True, pos=(0,0,0),
        rotation=(0,0,0), colorize=(1,1,1,1)):
    """Loads a Wavefront OBJ file. Returns a BasicMesh object representing the OBJ mesh."""
    view.require_init()
    svertices = []
    snormals = []
    stexcoords = []
    sfaces = []

    material = None
    smtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = map(float, values[1:4])
            if swapyz:
                v = v[0], v[2], v[1]
            svertices.append(v)
        elif values[0] == 'vn':
            v = map(float, values[1:4])
            if swapyz:
                v = v[0], v[2], v[1]
            snormals.append(v)
        elif values[0] == 'vt':
            stexcoords.append(map(float, values[1:3]))
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'mtllib':
            path = os.path.split(filename)[0]
            smtl = {}
            mtl = None
            for line in open(os.path.join(path, values[1]), "r"):
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'newmtl':
                    smtl[values[1]] = None
                    mtl = values[1]
                elif mtl is None:
                    raise ValueError, "mtl file doesn't start with newmtl stmt"
                elif values[0] == 'map_Kd':
                    tex = data.Texture(os.path.join(path, values[1]), 1)
                    smtl[mtl] = tex
                elif values[0]=="Kd":
                    tex = misc.create_empty_texture(color=map(float, values[1:]))
                    smtl[mtl] = tex
        elif values[0] == 'f':
            face = []
            texcoords = []
            norms = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    texcoords.append(int(w[1]))
                else:
                    texcoords.append(0)
                if len(w) >= 3 and len(w[2]) > 0:
                    norms.append(int(w[2]))
                else:
                    norms.append(0)
            sfaces.append((face, norms, texcoords, material))
        

    gl_list = data.DisplayList()
    gl_list.begin()
    for face in sfaces:
        vertices, normals, texture_coords, material = face
        if smtl:
            mtl = smtl[material]
            try:
                mtl.bind()
            except:
                blank_texture.bind()
        else:
            blank_texture.bind()
        glBegin(GL_POLYGON)
        for i in xrange(len(vertices)):
            if normals[i] > 0:
                glNormal3fv(snormals[normals[i] - 1])
            if texture_coords[i] > 0:
                glTexCoord2fv(stexcoords[texture_coords[i] - 1])
            glVertex3fv(svertices[vertices[i] - 1])
        glEnd()
    gl_list.end()

    verts = []
    for i in sfaces:
        for x in i[0]:
            verts.append(svertices[x-1])

    return BasicMesh(gl_list, pos, rotation, verts, 1, colorize, smtl)

class BasicMesh(object):
    """A basic, static (non-animated) mesh class."""
    def __init__(self, display_list, pos=(0,0,0),
                 rotation=(0,0,0), verts=[],
                 scale=1, colorize=(1,1,1,1),
                 materials=None):
        """Create the mesh object
           display_list is the data.DisplayList holding the 3d rendering of the mesh
           pos must be a three-part tuple representing the position of the mesh
           rotation must be a three-part tuple representing the rotation of the mesh
           verts is a list of vertices in the mesh
           scale must be a number or three part tuple representing the scale value of the mesh
           colorize is a 4 part tuple representing the (RGBA 0-1) color of the mesh
           materials are the texture/color materials the mesh uses"""
        view.require_init()
        self.display_list = display_list
        self.pos = pos
        self.rotation = rotation
        self.verts = verts
        self.scale = scale
        self.colorize = colorize
        self.visible = True
        self.materials = materials #this is necessary so the textures aren't deleted when they no longer have references to them!

        self.volume = misc.VolumeStore(self)

    def get_dimensions(self):
        """Return the width/height/depth of the mesh"""
        x = []
        y = []
        z = []
        for i in self.verts:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])

        return max((x, abs(min(x)))), max((y, abs(min(y)))), max((z, abs(min(z))))

    def get_pos(self):
        """Return the position of the mesh"""
        return self.pos

    def get_scale(self):
        """Return the scale of the object."""
        try: return self.scale[0], self.scale[1], self.scale[2]
        except: return self.scale, self.scale, self.scale

    def copy(self):
        """Return a copy of the mesh, sharing the same data.DisplayList"""
        return BasicMesh(self.display_list, list(self.pos),
                         list(self.rotation), list(self.verts),
                         self.scale, list(self.colorize),
                         self.materials)

    def render(self, camera=None):
        """Render the mesh
           camera must be None of the camera the scene is using"""
        if not self.volume.test_visible(camera):
            return None
        glPushMatrix()
        x,y,z = self.pos
        glTranslatef(x,y,-z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.display_list.render()
        glPopMatrix()
